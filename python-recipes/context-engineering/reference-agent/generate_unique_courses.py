#!/usr/bin/env python3
"""
Generate unique course data without duplicates.
Quick fix for the duplicate course issue.
"""

import json
import random
from typing import List, Dict, Any

def generate_unique_courses():
    """Generate unique courses without duplicates."""
    
    # Define majors
    majors = [
        {
            "id": "01K897CBGND1XDP0TPQEAWB54S",
            "name": "Computer Science",
            "code": "CS",
            "department": "Computer Science",
            "description": "Study of computational systems, algorithms, and software design",
            "required_credits": 120,
            "career_paths": ["Software Engineer", "Data Scientist", "Systems Architect", "AI Researcher"]
        },
        {
            "id": "01K897CBGND1XDP0TPQEAWB54T",
            "name": "Data Science", 
            "code": "DS",
            "department": "Data Science",
            "description": "Interdisciplinary field using statistics, programming, and domain expertise",
            "required_credits": 120,
            "career_paths": ["Data Analyst", "Machine Learning Engineer", "Business Intelligence Analyst"]
        },
        {
            "id": "01K897CBGND1XDP0TPQEAWB54V",
            "name": "Mathematics",
            "code": "MATH", 
            "department": "Mathematics",
            "description": "Study of numbers, structures, patterns, and logical reasoning",
            "required_credits": 120,
            "career_paths": ["Mathematician", "Statistician", "Actuary", "Research Scientist"]
        },
        {
            "id": "01K897CBGND1XDP0TPQEAWB54W",
            "name": "Business Administration",
            "code": "BUS",
            "department": "Business", 
            "description": "Management, finance, marketing, and organizational behavior",
            "required_credits": 120,
            "career_paths": ["Business Analyst", "Project Manager", "Consultant", "Entrepreneur"]
        },
        {
            "id": "01K897CBGND1XDP0TPQEAWB54X",
            "name": "Psychology",
            "code": "PSY",
            "department": "Psychology",
            "description": "Scientific study of mind, behavior, and mental processes", 
            "required_credits": 120,
            "career_paths": ["Clinical Psychologist", "Counselor", "Research Psychologist", "HR Specialist"]
        }
    ]
    
    # Define unique course titles for each major
    course_titles = {
        "CS": [
            "Introduction to Programming", "Data Structures and Algorithms", "Computer Architecture",
            "Operating Systems", "Database Systems", "Software Engineering", "Web Development",
            "Machine Learning", "Computer Networks", "Cybersecurity Fundamentals", 
            "Mobile App Development", "Artificial Intelligence", "Computer Graphics",
            "Distributed Systems", "Human-Computer Interaction"
        ],
        "DS": [
            "Introduction to Data Science", "Statistics for Data Science", "Data Visualization",
            "Machine Learning for Data Science", "Big Data Analytics", "Data Mining",
            "Statistical Modeling", "Business Intelligence", "Data Ethics", "Time Series Analysis",
            "Natural Language Processing", "Deep Learning", "Predictive Analytics",
            "Data Warehousing", "Experimental Design"
        ],
        "MATH": [
            "Calculus I", "Calculus II", "Linear Algebra", "Differential Equations",
            "Probability Theory", "Mathematical Statistics", "Abstract Algebra", 
            "Real Analysis", "Discrete Mathematics", "Number Theory", "Topology",
            "Numerical Analysis", "Mathematical Modeling", "Optimization Theory",
            "Complex Analysis"
        ],
        "BUS": [
            "Principles of Management", "Marketing Strategy", "Financial Accounting",
            "Managerial Accounting", "Corporate Finance", "Operations Management",
            "Human Resource Management", "Business Ethics", "Strategic Management",
            "International Business", "Entrepreneurship", "Supply Chain Management",
            "Business Law", "Organizational Behavior", "Project Management"
        ],
        "PSY": [
            "Introduction to Psychology", "Cognitive Psychology", "Social Psychology",
            "Developmental Psychology", "Abnormal Psychology", "Research Methods in Psychology",
            "Biological Psychology", "Personality Psychology", "Learning and Memory",
            "Sensation and Perception", "Clinical Psychology", "Health Psychology",
            "Educational Psychology", "Industrial Psychology", "Positive Psychology"
        ]
    }
    
    courses = []
    course_counter = 1
    
    for major in majors:
        major_code = major["code"]
        major_name = major["name"]
        titles = course_titles[major_code]
        
        for i, title in enumerate(titles):
            course_code = f"{major_code}{course_counter:03d}"
            course_counter += 1
            
            # Generate realistic course data
            difficulty_levels = ["beginner", "intermediate", "advanced"]
            formats = ["in_person", "online", "hybrid"]
            credits = random.choice([3, 4])
            
            # Assign difficulty based on course progression
            if i < 5:
                difficulty = "beginner"
            elif i < 10:
                difficulty = "intermediate"
            else:
                difficulty = "advanced"
                
            course = {
                "id": f"course_{course_counter:03d}",
                "course_code": course_code,
                "title": title,
                "description": f"Comprehensive study of {title.lower()}. Core concepts and practical applications in {major_name.lower()}.",
                "credits": credits,
                "difficulty_level": difficulty,
                "format": random.choice(formats),
                "department": major["department"],
                "major": major_name,
                "prerequisites": [],
                "semester": random.choice(["fall", "spring", "summer"]),
                "year": 2024,
                "instructor": f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'])}",
                "max_enrollment": random.randint(20, 50),
                "current_enrollment": random.randint(10, 45),
                "learning_objectives": [
                    f"Understand fundamental concepts of {title.lower()}",
                    f"Apply {title.lower()} principles to real-world problems",
                    f"Develop skills in {major_name.lower()} methodology"
                ],
                "tags": [major_name.lower().replace(" ", "_"), title.lower().replace(" ", "_")],
                "schedule": {
                    "days": random.choice([["monday", "wednesday"], ["tuesday", "thursday"], ["monday", "wednesday", "friday"]]),
                    "start_time": random.choice(["09:00", "10:00", "11:00", "13:00", "14:00", "15:00"]),
                    "end_time": random.choice(["10:30", "11:30", "12:30", "14:30", "15:30", "16:30"]),
                    "location": f"Room {random.randint(100, 999)}"
                }
            }
            
            courses.append(course)
    
    # Create the final data structure
    catalog = {
        "majors": majors,
        "courses": courses,
        "metadata": {
            "generated_at": "2025-10-23T17:52:00Z",
            "total_majors": len(majors),
            "total_courses": len(courses),
            "version": "1.0.0"
        }
    }
    
    return catalog

def main():
    """Generate and save unique course catalog."""
    print("Generating unique course catalog...")
    catalog = generate_unique_courses()
    
    # Save to file
    with open("course_catalog_unique.json", "w") as f:
        json.dump(catalog, f, indent=2)
    
    print(f"Generated {len(catalog['majors'])} majors and {len(catalog['courses'])} unique courses")
    print("Saved to course_catalog_unique.json")
    
    # Verify no duplicates
    titles = [course["title"] for course in catalog["courses"]]
    unique_titles = set(titles)
    
    if len(titles) == len(unique_titles):
        print("✅ No duplicate titles found!")
    else:
        print(f"❌ Found {len(titles) - len(unique_titles)} duplicate titles")
    
    # Show sample
    print("\nSample courses:")
    for course in catalog["courses"][:5]:
        print(f"  {course['course_code']}: {course['title']}")

if __name__ == "__main__":
    main()
