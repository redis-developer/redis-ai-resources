#!/usr/bin/env python3
"""
Course catalog ingestion script for the Redis University Class Agent.

This script loads course catalog data from JSON files and ingests it into Redis
with proper vector indexing for semantic search capabilities.
"""

import json
import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Any
import click
from rich.console import Console
from rich.progress import Progress, TaskID
from dotenv import load_dotenv

from redis_context_course.models import Course, Major, DifficultyLevel, CourseFormat, Semester, DayOfWeek, Prerequisite, CourseSchedule
from redis_context_course.course_manager import CourseManager
from redis_context_course.redis_config import redis_config

# Load environment variables
load_dotenv()

console = Console()


class CourseIngestionPipeline:
    """Pipeline for ingesting course catalog data into Redis."""
    
    def __init__(self):
        self.course_manager = CourseManager()
        self.redis_client = redis_config.redis_client
    
    def load_catalog_from_json(self, filename: str) -> Dict[str, List[Dict[str, Any]]]:
        """Load course catalog data from JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            console.print(f"[green]✅ Loaded catalog from {filename}[/green]")
            console.print(f"   Majors: {len(data.get('majors', []))}")
            console.print(f"   Courses: {len(data.get('courses', []))}")
            
            return data
        except FileNotFoundError:
            console.print(f"[red]❌ File not found: {filename}[/red]")
            raise
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Invalid JSON in {filename}: {e}[/red]")
            raise
    
    def _dict_to_course(self, course_data: Dict[str, Any]) -> Course:
        """Convert dictionary data to Course object."""
        # Parse prerequisites
        prerequisites = []
        for prereq_data in course_data.get('prerequisites', []):
            prereq = Prerequisite(**prereq_data)
            prerequisites.append(prereq)
        
        # Parse schedule
        schedule = None
        if course_data.get('schedule'):
            schedule_data = course_data['schedule']
            # Convert day strings to DayOfWeek enums
            days = [DayOfWeek(day) for day in schedule_data['days']]
            schedule_data['days'] = days
            schedule = CourseSchedule(**schedule_data)
        
        # Create course object
        course = Course(
            id=course_data.get('id'),
            course_code=course_data['course_code'],
            title=course_data['title'],
            description=course_data['description'],
            credits=course_data['credits'],
            difficulty_level=DifficultyLevel(course_data['difficulty_level']),
            format=CourseFormat(course_data['format']),
            department=course_data['department'],
            major=course_data['major'],
            prerequisites=prerequisites,
            schedule=schedule,
            semester=Semester(course_data['semester']),
            year=course_data['year'],
            instructor=course_data['instructor'],
            max_enrollment=course_data['max_enrollment'],
            current_enrollment=course_data['current_enrollment'],
            tags=course_data.get('tags', []),
            learning_objectives=course_data.get('learning_objectives', [])
        )
        
        return course
    
    def _dict_to_major(self, major_data: Dict[str, Any]) -> Major:
        """Convert dictionary data to Major object."""
        return Major(
            id=major_data.get('id'),
            name=major_data['name'],
            code=major_data['code'],
            department=major_data['department'],
            description=major_data['description'],
            required_credits=major_data['required_credits'],
            core_courses=major_data.get('core_courses', []),
            elective_courses=major_data.get('elective_courses', []),
            career_paths=major_data.get('career_paths', [])
        )
    
    async def ingest_courses(self, courses_data: List[Dict[str, Any]]) -> int:
        """Ingest courses into Redis with progress tracking."""
        ingested_count = 0
        
        with Progress() as progress:
            task = progress.add_task("[green]Ingesting courses...", total=len(courses_data))
            
            for course_data in courses_data:
                try:
                    course = self._dict_to_course(course_data)
                    await self.course_manager.store_course(course)
                    ingested_count += 1
                    progress.update(task, advance=1)
                except Exception as e:
                    console.print(f"[red]❌ Failed to ingest course {course_data.get('course_code', 'unknown')}: {e}[/red]")
        
        return ingested_count
    
    def ingest_majors(self, majors_data: List[Dict[str, Any]]) -> int:
        """Ingest majors into Redis."""
        ingested_count = 0
        
        with Progress() as progress:
            task = progress.add_task("[blue]Ingesting majors...", total=len(majors_data))
            
            for major_data in majors_data:
                try:
                    major = self._dict_to_major(major_data)
                    # Store major data in Redis (simple hash storage)
                    key = f"major:{major.id}"
                    # Convert any non-scalar fields to JSON strings for Redis hash storage
                    major_map = {}
                    for k, v in major.dict().items():
                        if isinstance(v, (list, dict)):
                            major_map[k] = json.dumps(v)
                        elif isinstance(v, datetime):
                            major_map[k] = v.isoformat()
                        else:
                            major_map[k] = v
                    self.redis_client.hset(key, mapping=major_map)
                    ingested_count += 1
                    progress.update(task, advance=1)
                except Exception as e:
                    console.print(f"[red]❌ Failed to ingest major {major_data.get('name', 'unknown')}: {e}[/red]")
        
        return ingested_count
    
    def clear_existing_data(self):
        """Clear existing course and major data from Redis."""
        console.print("[yellow]🧹 Clearing existing data...[/yellow]")
        
        # Clear course data
        course_keys = self.redis_client.keys(f"{redis_config.vector_index_name}:*")
        if course_keys:
            self.redis_client.delete(*course_keys)
            console.print(f"   Cleared {len(course_keys)} course records")
        
        # Clear major data
        major_keys = self.redis_client.keys("major:*")
        if major_keys:
            self.redis_client.delete(*major_keys)
            console.print(f"   Cleared {len(major_keys)} major records")
        
        console.print("[green]✅ Data cleared successfully[/green]")
    
    def verify_ingestion(self) -> Dict[str, int]:
        """Verify the ingestion by counting stored records."""
        course_count = len(self.redis_client.keys(f"{redis_config.vector_index_name}:*"))
        major_count = len(self.redis_client.keys("major:*"))
        
        return {
            "courses": course_count,
            "majors": major_count
        }
    
    async def run_ingestion(self, catalog_file: str, clear_existing: bool = False):
        """Run the complete ingestion pipeline."""
        console.print("[bold blue]🚀 Starting Course Catalog Ingestion[/bold blue]")
        
        # Check Redis connection
        if not redis_config.health_check():
            console.print("[red]❌ Redis connection failed. Please check your Redis server.[/red]")
            return False
        
        console.print("[green]✅ Redis connection successful[/green]")
        
        # Clear existing data if requested
        if clear_existing:
            self.clear_existing_data()
        
        # Load catalog data
        try:
            catalog_data = self.load_catalog_from_json(catalog_file)
        except Exception:
            return False
        
        # Ingest majors
        majors_data = catalog_data.get('majors', [])
        if majors_data:
            major_count = self.ingest_majors(majors_data)
            console.print(f"[green]✅ Ingested {major_count} majors[/green]")
        
        # Ingest courses
        courses_data = catalog_data.get('courses', [])
        if courses_data:
            course_count = await self.ingest_courses(courses_data)
            console.print(f"[green]✅ Ingested {course_count} courses[/green]")
        
        # Verify ingestion
        verification = self.verify_ingestion()
        console.print(f"[blue]📊 Verification - Courses: {verification['courses']}, Majors: {verification['majors']}[/blue]")
        
        console.print("[bold green]🎉 Ingestion completed successfully![/bold green]")
        return True


@click.command()
@click.option('--catalog', '-c', default='course_catalog.json', help='Course catalog JSON file')
@click.option('--clear', is_flag=True, help='Clear existing data before ingestion')
@click.option('--redis-url', help='Redis connection URL')
def main(catalog: str, clear: bool, redis_url: str):
    """Ingest course catalog data into Redis for the Class Agent."""
    
    # Set Redis URL if provided
    if redis_url:
        os.environ['REDIS_URL'] = redis_url
    
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        console.print("[red]❌ OPENAI_API_KEY environment variable is required[/red]")
        console.print("[yellow]Please set your OpenAI API key for embedding generation[/yellow]")
        sys.exit(1)
    
    # Run ingestion
    pipeline = CourseIngestionPipeline()
    
    try:
        success = asyncio.run(pipeline.run_ingestion(catalog, clear))
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Ingestion interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Ingestion failed: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
