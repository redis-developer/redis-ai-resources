"""
RedisVL Semantic Router and Semantic Cache Code Snippets
=========================================================

This file contains all the code snippets for implementing RedisVL enhancements
in Notebook 02: Scaling with Semantic Tool Selection.

These snippets replace the custom tool selector implementation with production-ready
RedisVL extensions.

Usage:
    Copy the relevant sections into the notebook cells as indicated by the
    section markers.
"""

# ==============================================================================
# SECTION 1: IMPORTS (Add to imports cell)
# ==============================================================================

from redisvl.extensions.router import Route, SemanticRouter
from redisvl.extensions.llmcache import SemanticCache

# ==============================================================================
# SECTION 2: CREATE SEMANTIC ROUTES (Replaces custom index creation)
# ==============================================================================

"""
🎓 EDUCATIONAL CONTENT: What is Semantic Router?

Semantic Router is a RedisVL extension that provides KNN-style classification
over a set of "routes" (in our case, tools). It automatically:
- Creates and manages Redis vector index
- Generates embeddings for route references
- Performs semantic similarity search
- Returns best matching route(s) with distance scores

🔑 Why This Matters for Context Engineering:

Context engineering is about managing what information reaches the LLM.
Semantic Router helps by:
1. Intelligent Tool Selection - Only relevant tools in context
2. Constant Token Overhead - Top-k selection = predictable context size
3. Semantic Understanding - Matches query intent to tool purpose
4. Production Patterns - Industry-standard approaches

Key Concept: Routes are "semantic buckets" - each route (tool) has reference
examples that define when it should be selected.
"""

# Create routes for each tool
print("🔨 Creating semantic routes for tools...")

search_courses_route = Route(
    name="search_courses_hybrid",
    references=[
        "Find courses by topic or subject",
        "Explore available courses",
        "Get course recommendations",
        "Search for specific course types",
        "What courses are available?",
        "Show me machine learning courses",
        "Browse the course catalog"
    ],
    metadata={"tool": search_courses_hybrid, "category": "course_discovery"},
    distance_threshold=0.3  # Lower = more strict matching
)

search_memories_route = Route(
    name="search_memories",
    references=[
        "Recall user preferences",
        "Remember past goals",
        "Personalize recommendations based on history",
        "Check user history",
        "What format does the user prefer?",
        "What did I say about my learning goals?",
        "Remember my preferences"
    ],
    metadata={"tool": search_memories, "category": "personalization"},
    distance_threshold=0.3
)

store_memory_route = Route(
    name="store_memory",
    references=[
        "Save user preferences",
        "Remember user goals",
        "Store important facts",
        "Record constraints",
        "Remember that I prefer online courses",
        "Save my learning goal",
        "Keep track of my interests"
    ],
    metadata={"tool": store_memory, "category": "personalization"},
    distance_threshold=0.3
)

check_prerequisites_route = Route(
    name="check_prerequisites",
    references=[
        "Check course prerequisites",
        "Verify readiness for a course",
        "Understand course requirements",
        "Find what to learn first",
        "What do I need before taking this course?",
        "Am I ready for RU202?",
        "What are the requirements?"
    ],
    metadata={"tool": check_prerequisites, "category": "course_planning"},
    distance_threshold=0.3
)

compare_courses_route = Route(
    name="compare_courses",
    references=[
        "Compare course options",
        "Understand differences between courses",
        "Choose between similar courses",
        "Evaluate course alternatives",
        "What's the difference between RU101 and RU102?",
        "Which course is better for beginners?",
        "Compare these two courses"
    ],
    metadata={"tool": compare_courses, "category": "course_planning"},
    distance_threshold=0.3
)

print("✅ Created 5 semantic routes")
print(f"\nExample route:")
print(f"   Name: {check_prerequisites_route.name}")
print(f"   References: {len(check_prerequisites_route.references)} examples")
print(f"   Distance threshold: {check_prerequisites_route.distance_threshold}")

# ==============================================================================
# SECTION 3: INITIALIZE SEMANTIC ROUTER
# ==============================================================================

"""
🎓 EDUCATIONAL CONTENT: Router Initialization

The SemanticRouter automatically:
1. Creates Redis vector index for route references
2. Generates embeddings for all references
3. Stores embeddings in Redis
4. Provides simple API for routing queries

This replaces ~180 lines of custom code with ~10 lines!
"""

print("🔨 Initializing Semantic Router...")

tool_router = SemanticRouter(
    name="course-advisor-tool-router",
    routes=[
        search_courses_route,
        search_memories_route,
        store_memory_route,
        check_prerequisites_route,
        compare_courses_route
    ],
    redis_url=REDIS_URL,
    overwrite=True  # Recreate index if it exists
)

print("✅ Semantic Router initialized")
print(f"   Router name: {tool_router.name}")
print(f"   Routes: {len(tool_router.routes)}")
print(f"   Index created: course-advisor-tool-router")
print("\n💡 The router automatically created the Redis index and stored all embeddings!")

# ==============================================================================
# SECTION 4: TEST TOOL ROUTING FUNCTION
# ==============================================================================

async def test_tool_routing(query: str, max_k: int = 3):
    """
    Test semantic tool routing for a given query.
    
    This demonstrates how the router:
    1. Embeds the query
    2. Compares to all route references
    3. Returns top-k most similar routes (tools)
    
    🎓 Educational Note:
    - Distance: 0.0 = perfect match, 1.0 = completely different
    - Similarity: 1.0 = perfect match, 0.0 = completely different
    """
    print("=" * 80)
    print(f"🔍 QUERY: {query}")
    print("=" * 80)
    
    # Get top-k route matches
    route_matches = tool_router.route_many(query, max_k=max_k)
    
    print(f"\n📊 Top {max_k} Tool Matches:")
    print(f"{'Rank':<6} {'Tool Name':<30} {'Distance':<12} {'Similarity':<12}")
    print("-" * 80)
    
    for i, match in enumerate(route_matches, 1):
        similarity = 1.0 - match.distance
        print(f"{i:<6} {match.name:<30} {match.distance:<12.3f} {similarity:<12.3f}")
    
    # Get the actual tool objects
    selected_tools = [match.metadata["tool"] for match in route_matches]
    
    print(f"\n✅ Selected {len(selected_tools)} tools for this query")
    print(f"   Tools: {', '.join([match.name for match in route_matches])}")
    
    return route_matches, selected_tools

# ==============================================================================
# SECTION 5: SEMANTIC CACHE IMPLEMENTATION
# ==============================================================================

"""
🎓 EDUCATIONAL CONTENT: What is Semantic Cache?

Semantic Cache is a RedisVL extension that caches LLM responses (or in our case,
tool selections) based on semantic similarity of queries.

The Problem:
- "What ML courses are available?"
- "Show me machine learning courses"
→ These are semantically similar but would trigger separate tool selections

The Solution:
Semantic Cache stores query-result pairs and returns cached results for similar queries.

🔑 Why This Matters for Context Engineering:

1. Reduced Latency - Skip embedding + vector search for similar queries
2. Cost Savings - Fewer OpenAI API calls
3. Consistency - Same results for similar queries
4. Production Pattern - Real-world caching strategy
"""

# Initialize Semantic Cache
tool_selection_cache = SemanticCache(
    name="tool_selection_cache",
    redis_url=REDIS_URL,
    distance_threshold=0.1,  # Very similar queries (0.0-0.2 recommended)
    ttl=3600  # Cache for 1 hour
)

print("✅ Semantic Cache initialized")
print(f"   Cache name: {tool_selection_cache.name}")
print(f"   Distance threshold: {tool_selection_cache.distance_threshold}")
print(f"   TTL: 3600 seconds (1 hour)")

# ==============================================================================
# SECTION 6: CACHED TOOL SELECTOR CLASS
# ==============================================================================

class CachedSemanticToolSelector:
    """
    Tool selector with semantic caching for performance optimization.
    
    This demonstrates a production pattern:
    1. Check cache first (fast path - ~5ms)
    2. If cache miss, use router (slow path - ~65ms)
    3. Store result in cache for future queries
    
    🎓 Educational Note:
    This pattern is used in production LLM applications to reduce latency
    and costs. Cache hit rates of 30-40% are typical for course advisor
    use cases, resulting in significant performance improvements.
    """
    
    def __init__(
        self,
        router: SemanticRouter,
        cache: SemanticCache,
        max_k: int = 3
    ):
        self.router = router
        self.cache = cache
        self.max_k = max_k
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def select_tools(self, query: str, max_k: Optional[int] = None) -> tuple:
        """
        Select tools with caching.
        
        Returns:
            (tool_names, cache_hit, latency_ms)
        """
        import time
        start_time = time.time()
        
        k = max_k or self.max_k
        
        # Check cache first
        cached_result = self.cache.check(prompt=query)
        
        if cached_result:
            # Cache hit!
            self.cache_hits += 1
            tool_names = json.loads(cached_result[0]["response"])
            latency_ms = (time.time() - start_time) * 1000
            return tool_names, True, latency_ms
        
        # Cache miss - use router
        self.cache_misses += 1
        route_matches = self.router.route_many(query, max_k=k)
        tool_names = [match.name for match in route_matches]
        
        # Store in cache
        self.cache.store(
            prompt=query,
            response=json.dumps(tool_names),
            metadata={"timestamp": datetime.now().isoformat()}
        )
        
        latency_ms = (time.time() - start_time) * 1000
        return tool_names, False, latency_ms
    
    def get_cache_stats(self) -> dict:
        """Get cache performance statistics."""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "total_requests": total,
            "hit_rate_pct": hit_rate
        }

# Initialize cached selector
cached_selector = CachedSemanticToolSelector(
    router=tool_router,
    cache=tool_selection_cache,
    max_k=3
)

print("✅ Cached tool selector initialized")

# ==============================================================================
# SECTION 7: CACHE PERFORMANCE TEST
# ==============================================================================

async def test_cache_performance():
    """
    Test cache performance with similar queries.
    
    🎓 Educational Note:
    This test demonstrates how semantic cache improves performance for
    similar queries. Notice how:
    1. First query in each group = MISS (slow)
    2. Similar queries = HIT (fast)
    3. Cache hits are 10-20x faster than misses
    """
    
    # Test queries - some are semantically similar
    test_queries = [
        # Group 1: Course search (similar)
        "What machine learning courses are available?",
        "Show me ML courses",
        "Find courses about machine learning",
        
        # Group 2: Prerequisites (similar)
        "What are the prerequisites for RU202?",
        "What do I need before taking RU202?",
        
        # Group 3: Comparison (similar)
        "Compare RU101 and RU102JS",
        "What's the difference between RU101 and RU102JS?",
        
        # Group 4: Unique queries
        "Remember that I prefer online courses",
        "What did I say about my learning goals?"
    ]
    
    print("=" * 80)
    print("🧪 SEMANTIC CACHE PERFORMANCE TEST")
    print("=" * 80)
    print(f"\n{'Query':<50} {'Cache':<12} {'Latency':<12} {'Tools Selected':<30}")
    print("-" * 80)
    
    for query in test_queries:
        tool_names, cache_hit, latency_ms = await cached_selector.select_tools(query)
        cache_status = "🎯 HIT" if cache_hit else "🔍 MISS"
        tools_str = ", ".join(tool_names[:2]) + ("..." if len(tool_names) > 2 else "")
        
        print(f"{query[:48]:<50} {cache_status:<12} {latency_ms:>8.1f}ms   {tools_str:<30}")
    
    # Show cache statistics
    stats = cached_selector.get_cache_stats()
    
    print("\n" + "=" * 80)
    print("📊 CACHE STATISTICS")
    print("=" * 80)
    print(f"   Cache hits:     {stats['cache_hits']}")
    print(f"   Cache misses:   {stats['cache_misses']}")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Hit rate:       {stats['hit_rate_pct']:.1f}%")
    print("=" * 80)
    
    print("\n💡 Key Insight:")
    print("   Cache hits are ~10-20x faster than cache misses!")
    print("   Typical latencies:")
    print("      - Cache hit:  ~5-10ms")
    print("      - Cache miss: ~50-100ms (embedding + vector search)")

# Run the test
await test_cache_performance()

