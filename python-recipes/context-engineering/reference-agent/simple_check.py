#!/usr/bin/env python3
"""
Simple script to check if course data exists in Redis.
"""

import redis
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_redis_data():
    """Check what data exists in Redis."""
    try:
        # Connect to Redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url, decode_responses=True)
        
        print("🔍 Checking Redis data...")
        
        # Test connection
        r.ping()
        print("✅ Redis connection successful")
        
        # Check all keys
        all_keys = r.keys("*")
        print(f"\n📊 Total keys in Redis: {len(all_keys)}")
        
        # Look for course-related keys
        course_keys = [key for key in all_keys if "course" in key.lower()]
        print(f"📚 Course-related keys: {len(course_keys)}")
        
        # Look for major keys
        major_keys = [key for key in all_keys if "major" in key.lower()]
        print(f"🎓 Major-related keys: {len(major_keys)}")
        
        # Check for vector index keys
        vector_keys = [key for key in all_keys if "course_catalog:" in key]
        print(f"🔍 Vector index keys: {len(vector_keys)}")
        
        # Show some sample keys
        if all_keys:
            print(f"\n📋 Sample keys (first 10):")
            for i, key in enumerate(all_keys[:10]):
                print(f"  {i+1}. {key}")
        
        # Check specific keys we expect
        expected_keys = ["majors", "course_catalog:index_info"]
        print(f"\n🔎 Checking expected keys:")
        for key in expected_keys:
            exists = r.exists(key)
            status = "✅" if exists else "❌"
            print(f"  {status} {key}")
            
        # If we have course_catalog keys, show a sample
        if vector_keys:
            sample_key = vector_keys[0]
            try:
                sample_data = r.hgetall(sample_key)
                print(f"\n📄 Sample course data from {sample_key}:")
                for field, value in list(sample_data.items())[:5]:
                    if field != "content_vector":  # Skip the vector data
                        print(f"  {field}: {value}")
            except UnicodeDecodeError:
                print(f"\n📄 Sample course found (contains binary vector data)")
                # Try to get just text fields
                try:
                    title = r.hget(sample_key, "title")
                    course_code = r.hget(sample_key, "course_code")
                    if title and course_code:
                        print(f"  course_code: {course_code}")
                        print(f"  title: {title}")
                except:
                    print("  (Binary data - course exists but can't display)")

        return len(course_keys) > 0 or len(vector_keys) > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function."""
    print("🎓 Redis Data Check")
    print("=" * 30)
    print("⚠️  DEPRECATED: Use 'python simple_health_check.py' instead")
    print("This script only checks Redis keys, not actual functionality.")
    print("=" * 30)

    has_courses = check_redis_data()

    print("\n" + "=" * 30)
    if has_courses:
        print("✅ Course data found in Redis!")
        print("Your agent should be able to search for courses.")
        print("\n🚀 Try testing the agent with:")
        print("  redis-class-agent --student-id your_name")
        print("\n💡 For comprehensive testing, use:")
        print("  python simple_health_check.py")
    else:
        print("❌ No course data found in Redis.")
        print("Run: ingest-courses --catalog course_catalog.json --clear")

if __name__ == "__main__":
    main()
