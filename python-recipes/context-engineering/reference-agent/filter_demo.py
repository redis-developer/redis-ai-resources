#!/usr/bin/env python3
"""
Demo script showing the improved filter usage in the Redis Context Course package.

This script demonstrates how we've replaced manual filter expression construction
with proper RedisVL filter classes for better maintainability and type safety.
"""

def demo_old_vs_new_filters():
    """Show the difference between old manual filters and new RedisVL filter classes."""
    
    print("🔍 Filter Expression Improvements")
    print("=" * 50)
    
    print("\n❌ OLD WAY (Manual String Construction):")
    print("```python")
    print("# Manual filter expression construction - error prone!")
    print("filter_expressions = []")
    print("if filters.get('department'):")
    print("    filter_expressions.append(f\"@department:{{{filters['department']}}}\")")
    print("if filters.get('difficulty_level'):")
    print("    filter_expressions.append(f\"@difficulty_level:{{{filters['difficulty_level']}}}\")")
    print("if filters.get('year'):")
    print("    filter_expressions.append(f\"@year:[{filters['year']} {filters['year']}]\")")
    print("if filters.get('credits_min'):")
    print("    min_credits = filters['credits_min']")
    print("    max_credits = filters.get('credits_max', 10)")
    print("    filter_expressions.append(f\"@credits:[{min_credits} {max_credits}]\")")
    print("")
    print("# Combine with string concatenation")
    print("if filter_expressions:")
    print("    vector_query.set_filter(\" \".join(filter_expressions))")
    print("```")
    
    print("\n✅ NEW WAY (RedisVL Filter Classes):")
    print("```python")
    print("from redisvl.query.filter import Tag, Num")
    print("")
    print("# Type-safe filter construction!")
    print("filter_conditions = []")
    print("if filters.get('department'):")
    print("    filter_conditions.append(Tag('department') == filters['department'])")
    print("if filters.get('difficulty_level'):")
    print("    filter_conditions.append(Tag('difficulty_level') == filters['difficulty_level'])")
    print("if filters.get('year'):")
    print("    filter_conditions.append(Num('year') == filters['year'])")
    print("if filters.get('credits_min'):")
    print("    min_credits = filters['credits_min']")
    print("    max_credits = filters.get('credits_max', 10)")
    print("    filter_conditions.append(Num('credits') >= min_credits)")
    print("    if max_credits != min_credits:")
    print("        filter_conditions.append(Num('credits') <= max_credits)")
    print("")
    print("# Combine with proper boolean logic")
    print("if filter_conditions:")
    print("    combined_filter = filter_conditions[0]")
    print("    for condition in filter_conditions[1:]:")
    print("        combined_filter = combined_filter & condition")
    print("    vector_query.set_filter(combined_filter)")
    print("```")
    
    print("\n🎯 Benefits of the New Approach:")
    benefits = [
        "**Type Safety**: Compile-time checking of field names and types",
        "**Readability**: Clear, expressive syntax that's easy to understand",
        "**Maintainability**: No more string formatting errors or typos",
        "**Boolean Logic**: Proper AND/OR operations with & and | operators",
        "**IDE Support**: Auto-completion and syntax highlighting",
        "**Error Prevention**: Catches mistakes at development time",
        "**Consistency**: Uniform approach across all filter operations"
    ]
    
    for benefit in benefits:
        print(f"  ✅ {benefit}")
    
    print("\n📚 Filter Class Examples:")
    print("```python")
    print("# Tag filters (for string/categorical fields)")
    print("Tag('department') == 'Computer Science'")
    print("Tag('format') == 'online'")
    print("Tag('difficulty_level') == 'intermediate'")
    print("")
    print("# Numeric filters (for number fields)")
    print("Num('year') == 2024")
    print("Num('credits') >= 3")
    print("Num('credits') <= 4")
    print("")
    print("# Boolean combinations")
    print("(Tag('department') == 'CS') & (Num('credits') >= 3)")
    print("(Tag('format') == 'online') | (Tag('format') == 'hybrid')")
    print("")
    print("# Complex combinations")
    print("cs_filter = Tag('department') == 'Computer Science'")
    print("credits_filter = (Num('credits') >= 3) & (Num('credits') <= 4)")
    print("online_filter = Tag('format') == 'online'")
    print("combined = cs_filter & credits_filter & online_filter")
    print("```")


def demo_memory_filters():
    """Show the memory filter improvements."""
    
    print("\n🧠 Memory Filter Improvements")
    print("=" * 40)
    
    print("\n❌ OLD WAY (Memory Filters):")
    print("```python")
    print("# Manual string construction for memory filters")
    print("filters = [f\"@student_id:{{{self.student_id}}}\"]")
    print("if memory_types:")
    print("    type_filter = \"|\".join(memory_types)")
    print("    filters.append(f\"@memory_type:{{{type_filter}}}\")")
    print("vector_query.set_filter(\" \".join(filters))")
    print("```")
    
    print("\n✅ NEW WAY (Memory Filters):")
    print("```python")
    print("# Type-safe memory filter construction")
    print("filter_conditions = [Tag('student_id') == self.student_id]")
    print("")
    print("if memory_types:")
    print("    if len(memory_types) == 1:")
    print("        filter_conditions.append(Tag('memory_type') == memory_types[0])")
    print("    else:")
    print("        # Create OR condition for multiple memory types")
    print("        memory_type_filter = Tag('memory_type') == memory_types[0]")
    print("        for memory_type in memory_types[1:]:")
    print("            memory_type_filter = memory_type_filter | (Tag('memory_type') == memory_type)")
    print("        filter_conditions.append(memory_type_filter)")
    print("")
    print("# Combine with AND logic")
    print("combined_filter = filter_conditions[0]")
    print("for condition in filter_conditions[1:]:")
    print("    combined_filter = combined_filter & condition")
    print("vector_query.set_filter(combined_filter)")
    print("```")


def demo_real_world_examples():
    """Show real-world filter examples."""
    
    print("\n🌍 Real-World Filter Examples")
    print("=" * 40)
    
    examples = [
        {
            "name": "Find Online CS Courses",
            "description": "Computer Science courses available online",
            "filter": "(Tag('department') == 'Computer Science') & (Tag('format') == 'online')"
        },
        {
            "name": "Beginner Programming Courses",
            "description": "Programming courses suitable for beginners with 3-4 credits",
            "filter": "(Tag('tags').contains('programming')) & (Tag('difficulty_level') == 'beginner') & (Num('credits') >= 3) & (Num('credits') <= 4)"
        },
        {
            "name": "Current Year Courses",
            "description": "Courses offered in the current academic year",
            "filter": "Num('year') == 2024"
        },
        {
            "name": "Student Preferences Memory",
            "description": "Retrieve preference memories for a specific student",
            "filter": "(Tag('student_id') == 'student_123') & (Tag('memory_type') == 'preference')"
        },
        {
            "name": "Multiple Memory Types",
            "description": "Get preferences and goals for a student",
            "filter": "(Tag('student_id') == 'student_123') & ((Tag('memory_type') == 'preference') | (Tag('memory_type') == 'goal'))"
        }
    ]
    
    for example in examples:
        print(f"\n📝 **{example['name']}**")
        print(f"   Description: {example['description']}")
        print(f"   Filter: `{example['filter']}`")


def main():
    """Run the filter demo."""
    try:
        demo_old_vs_new_filters()
        demo_memory_filters()
        demo_real_world_examples()
        
        print("\n🎉 Filter Improvements Complete!")
        print("\n📋 Summary of Changes:")
        print("  ✅ course_manager.py: Updated search_courses method")
        print("  ✅ memory.py: Updated retrieve_memories method")
        print("  ✅ Added proper imports for Tag and Num classes")
        print("  ✅ Replaced manual string construction with type-safe filters")
        print("  ✅ Improved boolean logic handling")
        
        print("\n🚀 Next Steps:")
        print("  1. Test with actual Redis instance to verify functionality")
        print("  2. Add unit tests for filter construction")
        print("  3. Consider adding more complex filter combinations")
        print("  4. Document filter patterns for other developers")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
