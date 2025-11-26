#!/usr/bin/env python3
"""
Course catalog generation script for the Redis University Class Agent.

This script generates realistic course data including courses, majors, prerequisites,
and other academic metadata for demonstration and testing purposes.
"""

import json
import random
from datetime import time
from typing import Any, Dict, List

import click
from faker import Faker

from redis_context_course.models import (
    Course,
    CourseFormat,
    CourseSchedule,
    DayOfWeek,
    DifficultyLevel,
    Major,
    Prerequisite,
    Semester,
)

fake = Faker()


class CourseGenerator:
    """Generates realistic course catalog data."""

    def __init__(self):
        self.majors_data = self._define_majors()
        self.course_templates = self._define_course_templates()
        self.generated_courses = []
        self.generated_majors = []

    def _define_majors(self) -> Dict[str, Dict[str, Any]]:
        """Define major programs with their characteristics."""
        return {
            "Computer Science": {
                "code": "CS",
                "department": "Computer Science",
                "description": "Study of computational systems, algorithms, and software design",
                "required_credits": 120,
                "career_paths": [
                    "Software Engineer",
                    "Data Scientist",
                    "Systems Architect",
                    "AI Researcher",
                ],
            },
            "Data Science": {
                "code": "DS",
                "department": "Data Science",
                "description": "Interdisciplinary field using statistics, programming, and domain expertise",
                "required_credits": 120,
                "career_paths": [
                    "Data Analyst",
                    "Machine Learning Engineer",
                    "Business Intelligence Analyst",
                ],
            },
            "Mathematics": {
                "code": "MATH",
                "department": "Mathematics",
                "description": "Study of numbers, structures, patterns, and logical reasoning",
                "required_credits": 120,
                "career_paths": [
                    "Mathematician",
                    "Statistician",
                    "Actuary",
                    "Research Scientist",
                ],
            },
            "Business Administration": {
                "code": "BUS",
                "department": "Business",
                "description": "Management, finance, marketing, and organizational behavior",
                "required_credits": 120,
                "career_paths": [
                    "Business Analyst",
                    "Project Manager",
                    "Consultant",
                    "Entrepreneur",
                ],
            },
            "Psychology": {
                "code": "PSY",
                "department": "Psychology",
                "description": "Scientific study of mind, behavior, and mental processes",
                "required_credits": 120,
                "career_paths": [
                    "Clinical Psychologist",
                    "Counselor",
                    "Research Psychologist",
                    "HR Specialist",
                ],
            },
        }

    def _define_course_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Define course templates for each major."""
        return {
            "Computer Science": [
                {
                    "title_template": "Introduction to Programming",
                    "description": "Fundamental programming concepts using Python. Variables, control structures, functions, and basic data structures.",
                    "difficulty": DifficultyLevel.BEGINNER,
                    "credits": 3,
                    "tags": ["programming", "python", "fundamentals"],
                    "learning_objectives": [
                        "Write basic Python programs",
                        "Understand variables and data types",
                        "Use control structures effectively",
                        "Create and use functions",
                    ],
                },
                {
                    "title_template": "Data Structures and Algorithms",
                    "description": "Study of fundamental data structures and algorithms. Arrays, linked lists, trees, graphs, sorting, and searching.",
                    "difficulty": DifficultyLevel.INTERMEDIATE,
                    "credits": 4,
                    "tags": ["algorithms", "data structures", "problem solving"],
                    "learning_objectives": [
                        "Implement common data structures",
                        "Analyze algorithm complexity",
                        "Solve problems using appropriate data structures",
                        "Understand time and space complexity",
                    ],
                },
                {
                    "title_template": "Database Systems",
                    "description": "Design and implementation of database systems. SQL, normalization, transactions, and database administration.",
                    "difficulty": DifficultyLevel.INTERMEDIATE,
                    "credits": 3,
                    "tags": ["databases", "sql", "data management"],
                    "learning_objectives": [
                        "Design relational databases",
                        "Write complex SQL queries",
                        "Understand database normalization",
                        "Implement database transactions",
                    ],
                },
                {
                    "title_template": "Machine Learning",
                    "description": "Introduction to machine learning algorithms and applications. Supervised and unsupervised learning, neural networks.",
                    "difficulty": DifficultyLevel.ADVANCED,
                    "credits": 4,
                    "tags": ["machine learning", "ai", "statistics"],
                    "learning_objectives": [
                        "Understand ML algorithms",
                        "Implement classification and regression models",
                        "Evaluate model performance",
                        "Apply ML to real-world problems",
                    ],
                },
                {
                    "title_template": "Web Development",
                    "description": "Full-stack web development using modern frameworks. HTML, CSS, JavaScript, React, and backend APIs.",
                    "difficulty": DifficultyLevel.INTERMEDIATE,
                    "credits": 3,
                    "tags": ["web development", "javascript", "react", "apis"],
                    "learning_objectives": [
                        "Build responsive web interfaces",
                        "Develop REST APIs",
                        "Use modern JavaScript frameworks",
                        "Deploy web applications",
                    ],
                },
            ],
            "Data Science": [
                {
                    "title_template": "Statistics for Data Science",
                    "description": "Statistical methods and probability theory for data analysis. Hypothesis testing, regression, and statistical inference.",
                    "difficulty": DifficultyLevel.INTERMEDIATE,
                    "credits": 4,
                    "tags": ["statistics", "probability", "data analysis"],
                    "learning_objectives": [
                        "Apply statistical methods to data",
                        "Perform hypothesis testing",
                        "Understand probability distributions",
                        "Conduct statistical inference",
                    ],
                },
                {
                    "title_template": "Data Visualization",
                    "description": "Creating effective visualizations for data communication. Tools include Python matplotlib, seaborn, and Tableau.",
                    "difficulty": DifficultyLevel.BEGINNER,
                    "credits": 3,
                    "tags": ["visualization", "python", "tableau", "communication"],
                    "learning_objectives": [
                        "Create effective data visualizations",
                        "Choose appropriate chart types",
                        "Use visualization tools",
                        "Communicate insights through visuals",
                    ],
                },
            ],
            "Mathematics": [
                {
                    "title_template": "Calculus I",
                    "description": "Differential calculus including limits, derivatives, and applications. Foundation for advanced mathematics.",
                    "difficulty": DifficultyLevel.INTERMEDIATE,
                    "credits": 4,
                    "tags": ["calculus", "derivatives", "limits"],
                    "learning_objectives": [
                        "Understand limits and continuity",
                        "Calculate derivatives",
                        "Apply calculus to real problems",
                        "Understand fundamental theorem",
                    ],
                },
                {
                    "title_template": "Linear Algebra",
                    "description": "Vector spaces, matrices, eigenvalues, and linear transformations. Essential for data science and engineering.",
                    "difficulty": DifficultyLevel.INTERMEDIATE,
                    "credits": 3,
                    "tags": ["linear algebra", "matrices", "vectors"],
                    "learning_objectives": [
                        "Perform matrix operations",
                        "Understand vector spaces",
                        "Calculate eigenvalues and eigenvectors",
                        "Apply linear algebra to problems",
                    ],
                },
            ],
            "Business Administration": [
                {
                    "title_template": "Principles of Management",
                    "description": "Fundamental management concepts including planning, organizing, leading, and controlling organizational resources.",
                    "difficulty": DifficultyLevel.BEGINNER,
                    "credits": 3,
                    "tags": ["management", "leadership", "organization"],
                    "learning_objectives": [
                        "Understand management principles",
                        "Apply leadership concepts",
                        "Organize teams effectively",
                        "Control organizational resources",
                    ],
                },
                {
                    "title_template": "Marketing Strategy",
                    "description": "Strategic marketing planning, market analysis, consumer behavior, and digital marketing techniques.",
                    "difficulty": DifficultyLevel.INTERMEDIATE,
                    "credits": 3,
                    "tags": ["marketing", "strategy", "consumer behavior"],
                    "learning_objectives": [
                        "Develop marketing strategies",
                        "Analyze market opportunities",
                        "Understand consumer behavior",
                        "Implement digital marketing",
                    ],
                },
            ],
            "Psychology": [
                {
                    "title_template": "Introduction to Psychology",
                    "description": "Overview of psychological principles, research methods, and major areas of study in psychology.",
                    "difficulty": DifficultyLevel.BEGINNER,
                    "credits": 3,
                    "tags": ["psychology", "research methods", "behavior"],
                    "learning_objectives": [
                        "Understand psychological principles",
                        "Learn research methods",
                        "Explore areas of psychology",
                        "Apply psychological concepts",
                    ],
                },
                {
                    "title_template": "Cognitive Psychology",
                    "description": "Study of mental processes including perception, memory, thinking, and problem-solving.",
                    "difficulty": DifficultyLevel.INTERMEDIATE,
                    "credits": 3,
                    "tags": ["cognitive psychology", "memory", "perception"],
                    "learning_objectives": [
                        "Understand cognitive processes",
                        "Study memory systems",
                        "Analyze problem-solving",
                        "Explore perception mechanisms",
                    ],
                },
            ],
        }

    def generate_majors(self) -> List[Major]:
        """Generate major objects."""
        majors = []
        for name, data in self.majors_data.items():
            major = Major(
                name=name,
                code=data["code"],
                department=data["department"],
                description=data["description"],
                required_credits=data["required_credits"],
                career_paths=data["career_paths"],
            )
            majors.append(major)

        self.generated_majors = majors
        return majors

    def generate_courses(self, courses_per_major: int = 10) -> List[Course]:
        """Generate course objects for all majors."""
        courses = []
        course_counter = 1

        for major_name, major_data in self.majors_data.items():
            templates = self.course_templates.get(major_name, [])

            # Generate courses based on templates and variations
            for i in range(courses_per_major):
                if templates:
                    template = random.choice(templates)
                else:
                    # Fallback template for majors without specific templates
                    template = {
                        "title_template": f"{major_name} Course {i + 1}",
                        "description": f"Advanced topics in {major_name.lower()}",
                        "difficulty": random.choice(list(DifficultyLevel)),
                        "credits": random.choice([3, 4]),
                        "tags": [major_name.lower().replace(" ", "_")],
                        "learning_objectives": [f"Understand {major_name} concepts"],
                    }

                # Create course code
                course_code = f"{major_data['code']}{course_counter:03d}"
                course_counter += 1

                # Generate schedule
                schedule = self._generate_schedule()

                # Generate prerequisites (some courses have them)
                prerequisites = []
                if i > 2 and random.random() < 0.3:  # 30% chance for advanced courses
                    # Add 1-2 prerequisites from earlier courses
                    prereq_count = random.randint(1, 2)
                    for _ in range(prereq_count):
                        prereq_num = random.randint(1, max(1, course_counter - 10))
                        prereq_code = f"{major_data['code']}{prereq_num:03d}"
                        prereq = Prerequisite(
                            course_code=prereq_code,
                            course_title=f"Prerequisite Course {prereq_num}",
                            minimum_grade=random.choice(["C", "C+", "B-"]),
                            can_be_concurrent=random.random() < 0.2,
                        )
                        prerequisites.append(prereq)

                course = Course(
                    course_code=course_code,
                    title=template["title_template"],
                    description=template["description"],
                    credits=template["credits"],
                    difficulty_level=template["difficulty"],
                    format=random.choice(list(CourseFormat)),
                    department=major_data["department"],
                    major=major_name,
                    prerequisites=prerequisites,
                    schedule=schedule,
                    semester=random.choice(list(Semester)),
                    year=2024,
                    instructor=fake.name(),
                    max_enrollment=random.randint(20, 100),
                    current_enrollment=random.randint(0, 80),
                    tags=template["tags"],
                    learning_objectives=template["learning_objectives"],
                )

                courses.append(course)

        self.generated_courses = courses
        return courses

    def _generate_schedule(self) -> CourseSchedule:
        """Generate a random course schedule."""
        # Common schedule patterns
        patterns = [
            ([DayOfWeek.MONDAY, DayOfWeek.WEDNESDAY, DayOfWeek.FRIDAY], 50),  # MWF
            ([DayOfWeek.TUESDAY, DayOfWeek.THURSDAY], 75),  # TR
            ([DayOfWeek.MONDAY, DayOfWeek.WEDNESDAY], 75),  # MW
            ([DayOfWeek.TUESDAY], 150),  # T (long class)
            ([DayOfWeek.THURSDAY], 150),  # R (long class)
        ]

        days, duration = random.choice(patterns)

        # Generate start time (8 AM to 6 PM)
        start_hour = random.randint(8, 18)
        start_time = time(start_hour, random.choice([0, 30]))

        # Calculate end time
        end_hour = start_hour + (duration // 60)
        end_minute = start_time.minute + (duration % 60)
        if end_minute >= 60:
            end_hour += 1
            end_minute -= 60

        end_time = time(end_hour, end_minute)

        # Generate location
        buildings = [
            "Science Hall",
            "Engineering Building",
            "Liberal Arts Center",
            "Business Complex",
            "Technology Center",
        ]
        room_number = random.randint(100, 999)
        location = f"{random.choice(buildings)} {room_number}"

        return CourseSchedule(
            days=days, start_time=start_time, end_time=end_time, location=location
        )

    def save_to_json(self, filename: str):
        """Save generated data to JSON file."""
        data = {
            "majors": [major.dict() for major in self.generated_majors],
            "courses": [course.dict() for course in self.generated_courses],
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(
            f"Generated {len(self.generated_majors)} majors and {len(self.generated_courses)} courses"
        )
        print(f"Data saved to {filename}")


@click.command()
@click.option("--output", "-o", default="course_catalog.json", help="Output JSON file")
@click.option(
    "--courses-per-major", "-c", default=10, help="Number of courses per major"
)
@click.option("--seed", "-s", type=int, help="Random seed for reproducible generation")
def main(output: str, courses_per_major: int, seed: int):
    """Generate course catalog data for the Redis University Class Agent."""

    if seed:
        random.seed(seed)
        fake.seed_instance(seed)

    generator = CourseGenerator()

    print("Generating majors...")
    majors = generator.generate_majors()

    print(f"Generating {courses_per_major} courses per major...")
    courses = generator.generate_courses(courses_per_major)

    print(f"Saving to {output}...")
    generator.save_to_json(output)

    print("\nGeneration complete!")
    print(f"Total majors: {len(majors)}")
    print(f"Total courses: {len(courses)}")


if __name__ == "__main__":
    main()
