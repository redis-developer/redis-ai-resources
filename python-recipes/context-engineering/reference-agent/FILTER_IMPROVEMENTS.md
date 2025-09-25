# Filter Expression Improvements

## Overview

This document describes the improvements made to filter expression construction in the Redis Context Course package, replacing manual string construction with proper RedisVL filter classes for better maintainability and type safety.

## Changes Made

### 1. Course Manager (`course_manager.py`)

**Before (Manual String Construction):**
```python
# Error-prone manual filter construction
filter_expressions = []
if "department" in filters:
    filter_expressions.append(f"@department:{{{filters['department']}}}")
if "year" in filters:
    filter_expressions.append(f"@year:[{filters['year']} {filters['year']}]")
if filter_expressions:
    vector_query.set_filter(" ".join(filter_expressions))
```

**After (RedisVL Filter Classes with Fallback):**
```python
# Type-safe filter construction with compatibility fallback
def _build_filters(self, filters: Dict[str, Any]) -> str:
    if REDISVL_AVAILABLE and Tag is not None and Num is not None:
        # Use RedisVL filter classes (preferred)
        filter_conditions = []
        if "department" in filters:
            filter_conditions.append(Tag("department") == filters["department"])
        if "year" in filters:
            filter_conditions.append(Num("year") == filters["year"])
        
        # Combine with proper boolean logic
        if filter_conditions:
            combined_filter = filter_conditions[0]
            for condition in filter_conditions[1:]:
                combined_filter = combined_filter & condition
            return combined_filter
    
    # Fallback to string construction for compatibility
    filter_expressions = []
    if "department" in filters:
        filter_expressions.append(f"@department:{{{filters['department']}}}")
    if "year" in filters:
        filter_expressions.append(f"@year:[{filters['year']} {filters['year']}]")
    return " ".join(filter_expressions)
```

### 2. Memory Manager (`memory.py`)

**Before (Manual String Construction):**
```python
# Manual memory filter construction
filters = [f"@student_id:{{{self.student_id}}}"]
if memory_types:
    type_filter = "|".join(memory_types)
    filters.append(f"@memory_type:{{{type_filter}}}")
vector_query.set_filter(" ".join(filters))
```

**After (RedisVL Filter Classes with Fallback):**
```python
# Type-safe memory filter construction
def _build_memory_filters(self, memory_types: Optional[List[str]] = None):
    if REDISVL_AVAILABLE and Tag is not None:
        # Use RedisVL filter classes (preferred)
        filter_conditions = [Tag("student_id") == self.student_id]
        
        if memory_types:
            if len(memory_types) == 1:
                filter_conditions.append(Tag("memory_type") == memory_types[0])
            else:
                # Proper OR logic for multiple types
                memory_type_filter = Tag("memory_type") == memory_types[0]
                for memory_type in memory_types[1:]:
                    memory_type_filter = memory_type_filter | (Tag("memory_type") == memory_type)
                filter_conditions.append(memory_type_filter)
        
        # Combine with AND logic
        combined_filter = filter_conditions[0]
        for condition in filter_conditions[1:]:
            combined_filter = combined_filter & condition
        return combined_filter
    
    # Fallback for compatibility
    filters = [f"@student_id:{{{self.student_id}}}"]
    if memory_types:
        type_filter = "|".join(memory_types)
        filters.append(f"@memory_type:{{{type_filter}}}")
    return " ".join(filters)
```

## Benefits

### 1. **Type Safety**
- Compile-time checking of field names and types
- IDE auto-completion and syntax highlighting
- Catches mistakes at development time

### 2. **Readability**
- Clear, expressive syntax that's easy to understand
- Self-documenting code with explicit operators
- Consistent patterns across the codebase

### 3. **Maintainability**
- No more string formatting errors or typos
- Easier to modify and extend filter logic
- Centralized filter construction logic

### 4. **Boolean Logic**
- Proper AND/OR operations with `&` and `|` operators
- Clear precedence and grouping
- Support for complex filter combinations

### 5. **Compatibility**
- Graceful fallback to string construction when RedisVL isn't available
- Works with different Pydantic versions (v1 and v2)
- Conditional imports prevent import errors

## Filter Examples

### Tag Filters (String/Categorical Fields)
```python
Tag('department') == 'Computer Science'
Tag('format') == 'online'
Tag('difficulty_level') == 'intermediate'
```

### Numeric Filters
```python
Num('year') == 2024
Num('credits') >= 3
Num('credits') <= 4
```

### Boolean Combinations
```python
# AND logic
(Tag('department') == 'CS') & (Num('credits') >= 3)

# OR logic
(Tag('format') == 'online') | (Tag('format') == 'hybrid')

# Complex combinations
cs_filter = Tag('department') == 'Computer Science'
credits_filter = (Num('credits') >= 3) & (Num('credits') <= 4)
online_filter = Tag('format') == 'online'
combined = cs_filter & credits_filter & online_filter
```

### Memory Type Filters
```python
# Single memory type
Tag('memory_type') == 'preference'

# Multiple memory types (OR logic)
(Tag('memory_type') == 'preference') | (Tag('memory_type') == 'goal')

# Student-specific memories
Tag('student_id') == 'student_123'
```

## Compatibility Strategy

The implementation uses a dual approach:

1. **Primary**: Use RedisVL filter classes when available
2. **Fallback**: Use string-based construction for compatibility

This ensures the package works in various environments:
- ✅ Full Redis + RedisVL environment (optimal)
- ✅ Limited environments without RedisVL (compatible)
- ✅ Different Pydantic versions (v1 and v2)
- ✅ Development environments with missing dependencies

## Testing

The improvements maintain backward compatibility while providing enhanced functionality:

```python
# Test basic functionality
from redis_context_course.course_manager import CourseManager
cm = CourseManager()

# Test filter building (works with or without RedisVL)
filters = {'department': 'Computer Science', 'credits_min': 3}
filter_expr = cm._build_filters(filters)
print(f"Filter expression: {filter_expr}")
```

## Future Enhancements

1. **Additional Filter Types**: Support for text search, date ranges, etc.
2. **Query Builder**: Higher-level query construction API
3. **Filter Validation**: Runtime validation of filter parameters
4. **Performance Optimization**: Caching of frequently used filters
5. **Documentation**: Interactive examples and tutorials

## Migration Guide

Existing code using the old string-based approach will continue to work unchanged. To take advantage of the new features:

1. Ensure RedisVL is properly installed
2. Use the new filter helper methods
3. Test with your specific Redis configuration
4. Consider migrating complex filter logic to use the new classes

The improvements are designed to be non-breaking and provide immediate benefits while maintaining full backward compatibility.
