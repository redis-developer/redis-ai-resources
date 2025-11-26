"""
Hierarchical course manager for two-tier retrieval.

This module implements progressive disclosure:
1. Search summaries (lightweight, fast)
2. Fetch details for top matches (comprehensive, on-demand)

This demonstrates context budget management and advanced Section 2 techniques.
"""

import json
import logging
from typing import List, Optional, Tuple
from redis import Redis
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.query.filter import Tag

from .redis_config import redis_config
from .hierarchical_models import CourseSummary, CourseDetails, HierarchicalCourse

logger = logging.getLogger(__name__)


class HierarchicalCourseManager:
    """
    Manages two-tier course retrieval for progressive disclosure.
    
    Architecture:
    - Tier 1: Vector index of course summaries (for search)
    - Tier 2: Hash storage of full course details (for deep dives)
    
    This enables:
    - Fast initial search across all courses
    - Detailed information only for relevant courses
    - Efficient context budget management
    """
    
    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        summary_index_name: str = "course_summaries",
        details_prefix: str = "course_details",
    ):
        """
        Initialize hierarchical course manager.
        
        Args:
            redis_client: Redis client (uses default if None)
            summary_index_name: Name for summary vector index
            details_prefix: Prefix for details hash keys
        """
        self.redis = redis_client or redis_config.get_redis_client()
        self.summary_index_name = summary_index_name
        self.details_prefix = details_prefix
        
        # Will be initialized when needed
        self._summary_index: Optional[SearchIndex] = None
    
    def _get_summary_index(self) -> SearchIndex:
        """Get or create summary vector index."""
        if self._summary_index is None:
            # Define index schema for summaries
            schema = {
                "index": {
                    "name": self.summary_index_name,
                    "prefix": f"{self.summary_index_name}:",
                    "storage_type": "hash",
                },
                "fields": [
                    {
                        "name": "course_code",
                        "type": "tag",
                    },
                    {
                        "name": "title",
                        "type": "text",
                    },
                    {
                        "name": "department",
                        "type": "tag",
                    },
                    {
                        "name": "difficulty_level",
                        "type": "tag",
                    },
                    {
                        "name": "tags",
                        "type": "tag",
                    },
                    {
                        "name": "embedding_text",
                        "type": "text",
                    },
                    {
                        "name": "embedding",
                        "type": "vector",
                        "attrs": {
                            "dims": 1536,  # OpenAI ada-002 dimensions
                            "algorithm": "hnsw",
                            "distance_metric": "cosine",
                        },
                    },
                ],
            }
            
            self._summary_index = SearchIndex.from_dict(schema)
            self._summary_index.set_client(self.redis)
            
            # Create index if it doesn't exist
            try:
                self._summary_index.create(overwrite=False)
                logger.info(f"Created summary index: {self.summary_index_name}")
            except Exception as e:
                if "Index already exists" not in str(e):
                    logger.warning(f"Index creation note: {e}")
        
        return self._summary_index
    
    async def add_course(self, course: HierarchicalCourse) -> bool:
        """
        Add a hierarchical course to storage.
        
        Args:
            course: HierarchicalCourse with summary and details
            
        Returns:
            True if successful
        """
        try:
            # Store summary in vector index
            await self._store_summary(course.summary, course.id)
            
            # Store details in hash
            await self._store_details(course.details, course.id)
            
            logger.info(f"Added course: {course.summary.course_code}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding course {course.summary.course_code}: {e}")
            return False
    
    async def _store_summary(self, summary: CourseSummary, course_id: str):
        """Store course summary in vector index."""
        # Generate embedding text if not present
        if not summary.embedding_text:
            summary.generate_embedding_text()
        
        # Get embedding from OpenAI
        from openai import OpenAI
        client = OpenAI()
        
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=summary.embedding_text
        )
        embedding = response.data[0].embedding
        
        # Prepare data for storage
        data = {
            "id": course_id,
            "course_code": summary.course_code,
            "title": summary.title,
            "department": summary.department,
            "credits": summary.credits,
            "difficulty_level": summary.difficulty_level.value,
            "format": summary.format.value,
            "instructor": summary.instructor,
            "short_description": summary.short_description,
            "prerequisite_codes": "|".join(summary.prerequisite_codes),
            "tags": "|".join(summary.tags),
            "embedding_text": summary.embedding_text,
            "embedding": embedding,
        }
        
        # Store in Redis
        key = f"{self.summary_index_name}:{course_id}"
        self.redis.hset(key, mapping={k: json.dumps(v) if isinstance(v, list) else str(v) for k, v in data.items()})
        
        logger.debug(f"Stored summary for {summary.course_code}")
    
    async def _store_details(self, details: CourseDetails, course_id: str):
        """Store full course details in hash."""
        # Serialize details to JSON
        details_json = details.model_dump_json()
        
        # Store in Redis hash
        key = f"{self.details_prefix}:{course_id}"
        self.redis.set(key, details_json)
        
        logger.debug(f"Stored details for {details.course_code}")
    
    async def search_summaries(
        self,
        query: str,
        limit: int = 5,
        department: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> List[CourseSummary]:
        """
        Search course summaries using vector similarity.
        
        This is Tier 1: Fast search across all courses.
        
        Args:
            query: Search query
            limit: Maximum number of results
            department: Filter by department
            difficulty: Filter by difficulty level
            
        Returns:
            List of course summaries
        """
        # Get embedding for query
        from openai import OpenAI
        client = OpenAI()
        
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_embedding = response.data[0].embedding
        
        # Create vector query
        index = self._get_summary_index()
        vector_query = VectorQuery(
            vector=query_embedding,
            vector_field_name="embedding",
            return_fields=[
                "id", "course_code", "title", "department", "credits",
                "difficulty_level", "format", "instructor", "short_description",
                "prerequisite_codes", "tags"
            ],
            num_results=limit,
        )
        
        # Add filters if specified
        if department:
            vector_query.set_filter(Tag("department") == department)
        if difficulty:
            vector_query.set_filter(Tag("difficulty_level") == difficulty)
        
        # Execute search
        results = index.query(vector_query)
        
        # Convert to CourseSummary objects
        summaries = []
        for result in results:
            summary = CourseSummary(
                course_code=result.get("course_code", ""),
                title=result.get("title", ""),
                department=result.get("department", ""),
                credits=int(result.get("credits", 0)),
                difficulty_level=result.get("difficulty_level", "beginner"),
                format=result.get("format", "online"),
                instructor=result.get("instructor", ""),
                short_description=result.get("short_description", ""),
                prerequisite_codes=result.get("prerequisite_codes", "").split("|") if result.get("prerequisite_codes") else [],
                tags=result.get("tags", "").split("|") if result.get("tags") else [],
            )
            summaries.append(summary)
        
        logger.info(f"Found {len(summaries)} course summaries for query: {query}")
        return summaries
    
    async def fetch_details(self, course_codes: List[str]) -> List[CourseDetails]:
        """
        Fetch full details for specific courses.
        
        This is Tier 2: Detailed information on-demand.
        
        Args:
            course_codes: List of course codes to fetch
            
        Returns:
            List of course details
        """
        details_list = []
        
        for course_code in course_codes:
            # Find course ID from summary index
            course_id = await self._get_course_id(course_code)
            if not course_id:
                logger.warning(f"Course not found: {course_code}")
                continue
            
            # Fetch details from hash
            key = f"{self.details_prefix}:{course_id}"
            details_json = self.redis.get(key)
            
            if details_json:
                details = CourseDetails.model_validate_json(details_json)
                details_list.append(details)
                logger.debug(f"Fetched details for {course_code}")
            else:
                logger.warning(f"Details not found for {course_code}")
        
        logger.info(f"Fetched {len(details_list)} course details")
        return details_list
    
    async def _get_course_id(self, course_code: str) -> Optional[str]:
        """Get course ID from course code."""
        # Search summary index for course code
        keys = self.redis.keys(f"{self.summary_index_name}:*")
        for key in keys:
            data = self.redis.hgetall(key)
            if data.get(b"course_code", b"").decode() == course_code:
                return data.get(b"id", b"").decode()
        return None
    
    async def hierarchical_search(
        self,
        query: str,
        summary_limit: int = 5,
        detail_limit: int = 2,
        **filters
    ) -> Tuple[List[CourseSummary], List[CourseDetails]]:
        """
        Two-stage hierarchical retrieval.
        
        This demonstrates progressive disclosure:
        1. Search summaries (all matches)
        2. Fetch details (top N matches)
        
        Args:
            query: Search query
            summary_limit: Number of summaries to return
            detail_limit: Number of detailed courses to fetch
            **filters: Additional filters (department, difficulty)
            
        Returns:
            Tuple of (summaries, details)
        """
        logger.info(f"Hierarchical search: '{query}' (summaries={summary_limit}, details={detail_limit})")
        
        # Stage 1: Search summaries
        summaries = await self.search_summaries(query, limit=summary_limit, **filters)
        
        # Stage 2: Fetch details for top N
        top_codes = [s.course_code for s in summaries[:detail_limit]]
        details = await self.fetch_details(top_codes)
        
        logger.info(f"Hierarchical search complete: {len(summaries)} summaries, {len(details)} details")
        return summaries, details

