#!/usr/bin/env python3
"""
Enhanced course catalog generation with hierarchical data.

Generates courses with full syllabi, assignments, learning objectives,
and prerequisites. Saves in both JSON and human-readable markdown format.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List

import click
from faker import Faker
from ulid import ULID

from redis_context_course.hierarchical_models import (
    Assignment,
    AssignmentType,
    CourseDetails,
    CourseSummary,
    CourseSyllabus,
    HierarchicalCourse,
    WeekPlan,
)
from redis_context_course.models import (
    CourseFormat,
    DifficultyLevel,
    Prerequisite,
    Semester,
)

fake = Faker()


class HierarchicalCourseGenerator:
    """Generates rich course data with syllabi and assignments."""

    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
            fake.seed_instance(seed)

        self.generated_courses: List[HierarchicalCourse] = []

    def generate_courses(self, count: int = 50) -> List[HierarchicalCourse]:
        """Generate hierarchical courses with full details."""

        # Course templates with rich content
        templates = self._get_course_templates()

        for i in range(count):
            template = random.choice(templates)
            course = self._generate_course_from_template(template, i + 1)
            self.generated_courses.append(course)

        return self.generated_courses

    def _get_course_templates(self) -> List[Dict[str, Any]]:
        """Define rich course templates."""
        return [
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Machine Learning Fundamentals",
                "short_desc": "Introduction to machine learning algorithms and applications.",
                "full_desc": "Introduction to machine learning algorithms and applications. This course covers supervised and unsupervised learning, neural networks, and deep learning. Students will learn to implement ML algorithms from scratch and use popular frameworks like scikit-learn and TensorFlow. The course emphasizes both theoretical foundations and practical applications.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["machine learning", "ai", "python", "neural networks"],
                "weeks": 14,
                "topics": [
                    "Introduction to ML and Python Setup",
                    "Linear Regression and Gradient Descent",
                    "Logistic Regression and Classification",
                    "Decision Trees and Random Forests",
                    "Support Vector Machines",
                    "Neural Networks Basics",
                    "Deep Learning and CNNs",
                    "Recurrent Neural Networks",
                    "Natural Language Processing",
                    "Unsupervised Learning and Clustering",
                    "Dimensionality Reduction (PCA, t-SNE)",
                    "Model Evaluation and Validation",
                    "Ensemble Methods",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Deep Learning and Neural Networks",
                "short_desc": "Advanced neural network architectures and deep learning techniques.",
                "full_desc": "Advanced neural network architectures and deep learning techniques. This course dives deep into modern deep learning, covering CNNs, RNNs, transformers, and GANs. Students will implement state-of-the-art models and work on real-world projects. Prerequisites include linear algebra, calculus, and programming experience.",
                "difficulty": DifficultyLevel.GRADUATE,
                "credits": 4,
                "tags": [
                    "deep learning",
                    "neural networks",
                    "transformers",
                    "computer vision",
                ],
                "weeks": 15,
                "topics": [
                    "Deep Learning Foundations",
                    "Convolutional Neural Networks",
                    "Advanced CNN Architectures (ResNet, VGG)",
                    "Object Detection (YOLO, R-CNN)",
                    "Recurrent Neural Networks",
                    "LSTM and GRU Networks",
                    "Attention Mechanisms",
                    "Transformer Architecture",
                    "BERT and GPT Models",
                    "Generative Adversarial Networks",
                    "Variational Autoencoders",
                    "Transfer Learning and Fine-tuning",
                    "Model Optimization and Deployment",
                    "Ethics in AI",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Natural Language Processing",
                "short_desc": "Processing and understanding human language with machine learning.",
                "full_desc": "Processing and understanding human language with machine learning. This course covers text processing, language models, sentiment analysis, and modern NLP techniques. Students will work with transformers, BERT, and GPT models. Projects include building chatbots, text classifiers, and language generation systems.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["nlp", "transformers", "text processing", "language models"],
                "weeks": 14,
                "topics": [
                    "Introduction to NLP and Text Processing",
                    "Tokenization and Word Embeddings",
                    "Word2Vec and GloVe",
                    "Text Classification",
                    "Sentiment Analysis",
                    "Named Entity Recognition",
                    "Part-of-Speech Tagging",
                    "Language Models and N-grams",
                    "Recurrent Networks for NLP",
                    "Attention and Transformers",
                    "BERT and Transfer Learning",
                    "GPT and Text Generation",
                    "Question Answering Systems",
                    "Final Projects",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Computer Vision",
                "short_desc": "Image processing, object detection, and visual recognition systems.",
                "full_desc": "Image processing, object detection, and visual recognition systems. This course teaches students how to build systems that can see and understand visual data. Topics include image processing, feature extraction, object detection, and semantic segmentation. Students will use OpenCV, PyTorch, and TensorFlow.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": [
                    "computer vision",
                    "image processing",
                    "object detection",
                    "cnn",
                ],
                "weeks": 14,
                "topics": [
                    "Introduction to Computer Vision",
                    "Image Processing Basics",
                    "Feature Detection and Extraction",
                    "Image Classification with CNNs",
                    "Advanced CNN Architectures",
                    "Object Detection (YOLO, SSD)",
                    "Semantic Segmentation",
                    "Instance Segmentation",
                    "Face Recognition",
                    "Optical Flow and Tracking",
                    "3D Vision and Depth Estimation",
                    "Video Analysis",
                    "Vision Transformers",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Linear Algebra for Machine Learning",
                "short_desc": "Matrix operations, eigenvalues, and applications to ML.",
                "full_desc": "Matrix operations, eigenvalues, and applications to machine learning. This course provides the mathematical foundation for understanding machine learning algorithms. Topics include vector spaces, matrix decompositions, eigenvalues, and optimization. Students will see how these concepts apply to PCA, SVD, and neural networks.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": [
                    "linear algebra",
                    "matrices",
                    "machine learning",
                    "mathematics",
                ],
                "weeks": 14,
                "topics": [
                    "Vectors and Vector Spaces",
                    "Matrix Operations",
                    "Linear Transformations",
                    "Matrix Decompositions",
                    "Eigenvalues and Eigenvectors",
                    "Singular Value Decomposition",
                    "Principal Component Analysis",
                    "Least Squares and Regression",
                    "Optimization Basics",
                    "Gradient Descent",
                    "Applications to Neural Networks",
                    "Dimensionality Reduction",
                    "Spectral Methods",
                    "Review and Applications",
                ],
            },
        ]

    def _generate_course_from_template(
        self, template: Dict[str, Any], course_num: int
    ) -> HierarchicalCourse:
        """Generate a complete hierarchical course from template."""

        course_code = f"{template['code_prefix']}{course_num:03d}"
        instructor = fake.name()

        # Generate syllabus
        syllabus = self._generate_syllabus(template)

        # Generate assignments
        assignments = self._generate_assignments(template["weeks"])

        # Generate prerequisites
        prerequisites = self._generate_prerequisites(template, course_num)

        # Create summary
        summary = CourseSummary(
            course_code=course_code,
            title=template["title"],
            department=template["department"],
            credits=template["credits"],
            difficulty_level=template["difficulty"],
            format=random.choice(list(CourseFormat)),
            instructor=instructor,
            short_description=template["short_desc"],
            prerequisite_codes=[p.course_code for p in prerequisites],
            tags=template["tags"],
        )
        summary.generate_embedding_text()

        # Create details
        details = CourseDetails(
            course_code=course_code,
            title=template["title"],
            department=template["department"],
            credits=template["credits"],
            difficulty_level=template["difficulty"],
            format=summary.format,
            instructor=instructor,
            full_description=template["full_desc"],
            prerequisites=prerequisites,
            learning_objectives=self._generate_learning_objectives(template),
            syllabus=syllabus,
            assignments=assignments,
            semester=random.choice(list(Semester)),
            year=2025,
            max_enrollment=random.randint(30, 80),
            tags=template["tags"],
        )

        # Create hierarchical course
        return HierarchicalCourse(
            id=str(ULID()),
            summary=summary,
            details=details,
        )

    def _generate_syllabus(self, template: Dict[str, Any]) -> CourseSyllabus:
        """Generate week-by-week syllabus."""
        weeks = []
        topics = template.get("topics", [])

        for week_num in range(1, template["weeks"] + 1):
            topic = (
                topics[week_num - 1]
                if week_num - 1 < len(topics)
                else f"Week {week_num} Topic"
            )

            week = WeekPlan(
                week_number=week_num,
                topic=topic,
                subtopics=[
                    f"{topic} - Part {i + 1}" for i in range(random.randint(2, 4))
                ],
                readings=[f"Chapter {week_num}", f"Research Paper {week_num}"],
                assignments=self._get_week_assignments(week_num, template["weeks"]),
                learning_objectives=[
                    f"Understand {topic.lower()}",
                    f"Apply {topic.lower()} concepts",
                    f"Implement {topic.lower()} solutions",
                ],
            )
            weeks.append(week)

        return CourseSyllabus(weeks=weeks, total_weeks=template["weeks"])

    def _get_week_assignments(self, week_num: int, total_weeks: int) -> List[str]:
        """Get assignments due in a specific week."""
        assignments = []

        # Homework every 2 weeks
        if week_num % 2 == 0 and week_num < total_weeks - 2:
            assignments.append(f"Homework {week_num // 2}")

        # Midterm
        if week_num == total_weeks // 2:
            assignments.append("Midterm Exam")

        # Final project milestones
        if week_num == total_weeks - 4:
            assignments.append("Project Proposal")
        elif week_num == total_weeks - 2:
            assignments.append("Project Draft")
        elif week_num == total_weeks:
            assignments.append("Final Project")

        return assignments

    def _generate_assignments(self, weeks: int) -> List[Assignment]:
        """Generate course assignments."""
        assignments = []

        # Homeworks (every 2 weeks)
        for i in range(1, weeks // 2):
            assignments.append(
                Assignment(
                    title=f"Homework {i}",
                    description=f"Problem set covering weeks {i * 2 - 1}-{i * 2}",
                    type=AssignmentType.HOMEWORK,
                    due_week=i * 2,
                    points=100,
                    estimated_hours=8.0,
                    submission_format="PDF or Jupyter Notebook",
                )
            )

        # Midterm
        assignments.append(
            Assignment(
                title="Midterm Exam",
                description="Comprehensive exam covering first half of course",
                type=AssignmentType.EXAM,
                due_week=weeks // 2,
                points=200,
                estimated_hours=3.0,
            )
        )

        # Final project
        assignments.extend(
            [
                Assignment(
                    title="Project Proposal",
                    description="1-page proposal for final project",
                    type=AssignmentType.PROJECT,
                    due_week=weeks - 4,
                    points=50,
                    estimated_hours=4.0,
                    group_work=True,
                    submission_format="PDF",
                ),
                Assignment(
                    title="Project Draft",
                    description="Working implementation and preliminary results",
                    type=AssignmentType.PROJECT,
                    due_week=weeks - 2,
                    points=100,
                    estimated_hours=15.0,
                    group_work=True,
                    submission_format="GitHub Repository",
                ),
                Assignment(
                    title="Final Project",
                    description="Complete project with code, report, and presentation",
                    type=AssignmentType.PROJECT,
                    due_week=weeks,
                    points=300,
                    estimated_hours=25.0,
                    group_work=True,
                    submission_format="GitHub + Presentation",
                ),
            ]
        )

        return assignments

    def _generate_prerequisites(
        self, template: Dict[str, Any], course_num: int
    ) -> List[Prerequisite]:
        """Generate prerequisites."""
        prerequisites = []

        # Advanced/graduate courses have prerequisites
        if template["difficulty"] in [
            DifficultyLevel.ADVANCED,
            DifficultyLevel.GRADUATE,
        ]:
            if course_num > 5:
                prereq_num = random.randint(1, course_num - 3)
                prerequisites.append(
                    Prerequisite(
                        course_code=f"{template['code_prefix']}{prereq_num:03d}",
                        course_title=f"Prerequisite Course {prereq_num}",
                        minimum_grade="C",
                        can_be_concurrent=False,
                    )
                )

        return prerequisites

    def _generate_learning_objectives(self, template: Dict[str, Any]) -> List[str]:
        """Generate learning objectives."""
        return [
            f"Understand core concepts in {template['title'].lower()}",
            f"Implement {template['title'].lower()} algorithms and techniques",
            f"Apply {template['title'].lower()} to real-world problems",
            f"Analyze and evaluate {template['title'].lower()} solutions",
            f"Design and build complete {template['department'].lower()} systems",
        ]

    def save_to_json(self, output_dir: Path):
        """Save courses to JSON file."""
        output_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "courses": [
                {
                    "id": course.id,
                    "summary": course.summary.model_dump(mode="json"),
                    "details": course.details.model_dump(mode="json"),
                    "created_at": course.created_at.isoformat(),
                }
                for course in self.generated_courses
            ]
        }

        json_file = output_dir / "hierarchical_courses.json"
        with open(json_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"✅ Saved {len(self.generated_courses)} courses to {json_file}")

    def save_to_markdown(self, output_dir: Path):
        """Save courses to human-readable markdown files."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create index file
        index_file = output_dir / "COURSE_CATALOG.md"
        with open(index_file, "w") as f:
            f.write("# Course Catalog\n\n")
            f.write(
                f"Generated {len(self.generated_courses)} courses with full syllabi and assignments.\n\n"
            )
            f.write("## Courses by Department\n\n")

            # Group by department
            by_dept = {}
            for course in self.generated_courses:
                dept = course.summary.department
                if dept not in by_dept:
                    by_dept[dept] = []
                by_dept[dept].append(course)

            for dept, courses in sorted(by_dept.items()):
                f.write(f"\n### {dept}\n\n")
                for course in sorted(courses, key=lambda c: c.summary.course_code):
                    f.write(
                        f"- **{course.summary.course_code}**: {course.summary.title}\n"
                    )
                    f.write(f"  - {course.summary.short_description}\n")
                    f.write(
                        f"  - Credits: {course.summary.credits} | Level: {course.summary.difficulty_level.value}\n"
                    )
                    f.write(f"  - [View Details]({course.summary.course_code}.md)\n\n")

        print(f"✅ Created course catalog index: {index_file}")

        # Create individual course files
        for course in self.generated_courses:
            self._save_course_markdown(course, output_dir)

        print(
            f"✅ Created {len(self.generated_courses)} individual course markdown files"
        )

    def _save_course_markdown(self, course: HierarchicalCourse, output_dir: Path):
        """Save individual course to markdown."""
        filename = output_dir / f"{course.summary.course_code}.md"

        with open(filename, "w") as f:
            # Header
            f.write(f"# {course.details.course_code}: {course.details.title}\n\n")

            # Basic info
            f.write("## Course Information\n\n")
            f.write(f"- **Department**: {course.details.department}\n")
            f.write(f"- **Credits**: {course.details.credits}\n")
            f.write(
                f"- **Difficulty Level**: {course.details.difficulty_level.value}\n"
            )
            f.write(f"- **Format**: {course.details.format.value}\n")
            f.write(f"- **Instructor**: {course.details.instructor}\n")
            f.write(
                f"- **Semester**: {course.details.semester.value} {course.details.year}\n"
            )
            f.write(f"- **Max Enrollment**: {course.details.max_enrollment}\n")

            # Description
            f.write(f"\n## Description\n\n{course.details.full_description}\n")

            # Prerequisites
            if course.details.prerequisites:
                f.write(f"\n## Prerequisites\n\n")
                for prereq in course.details.prerequisites:
                    f.write(f"- **{prereq.course_code}**: {prereq.course_title}")
                    if prereq.minimum_grade:
                        f.write(f" (Minimum grade: {prereq.minimum_grade})")
                    f.write("\n")

            # Learning objectives
            f.write(f"\n## Learning Objectives\n\n")
            for obj in course.details.learning_objectives:
                f.write(f"- {obj}\n")

            # Assignments
            f.write(f"\n## Assignments\n\n")
            f.write(f"**Total Points**: {course.details.get_total_points()}\n\n")

            by_type = {}
            for assignment in course.details.assignments:
                if assignment.type not in by_type:
                    by_type[assignment.type] = []
                by_type[assignment.type].append(assignment)

            for assign_type, assignments in sorted(
                by_type.items(), key=lambda x: x[0].value
            ):
                f.write(f"\n### {assign_type.value.title()}s\n\n")
                for assignment in sorted(assignments, key=lambda a: a.due_week):
                    f.write(f"#### {assignment.title} (Week {assignment.due_week})\n\n")
                    f.write(f"{assignment.description}\n\n")
                    f.write(f"- **Points**: {assignment.points}\n")
                    if assignment.estimated_hours:
                        f.write(
                            f"- **Estimated Hours**: {assignment.estimated_hours}\n"
                        )
                    if assignment.group_work:
                        f.write(f"- **Group Work**: Yes\n")
                    if assignment.submission_format:
                        f.write(
                            f"- **Submission Format**: {assignment.submission_format}\n"
                        )
                    f.write("\n")

            # Syllabus
            f.write(
                f"\n## Course Syllabus ({course.details.syllabus.total_weeks} weeks)\n\n"
            )
            for week in course.details.syllabus.weeks:
                f.write(f"\n### Week {week.week_number}: {week.topic}\n\n")

                if week.subtopics:
                    f.write("**Subtopics**:\n")
                    for subtopic in week.subtopics:
                        f.write(f"- {subtopic}\n")
                    f.write("\n")

                if week.learning_objectives:
                    f.write("**Learning Objectives**:\n")
                    for obj in week.learning_objectives:
                        f.write(f"- {obj}\n")
                    f.write("\n")

                if week.readings:
                    f.write("**Readings**:\n")
                    for reading in week.readings:
                        f.write(f"- {reading}\n")
                    f.write("\n")

                if week.assignments:
                    f.write("**Assignments Due**:\n")
                    for assignment in week.assignments:
                        f.write(f"- {assignment}\n")
                    f.write("\n")

            # Tags
            if course.details.tags:
                f.write(f"\n## Tags\n\n")
                f.write(", ".join([f"`{tag}`" for tag in course.details.tags]))
                f.write("\n")


@click.command()
@click.option(
    "--output-dir", "-o", default="generated_courses", help="Output directory"
)
@click.option("--count", "-c", default=50, help="Number of courses to generate")
@click.option("--seed", "-s", type=int, help="Random seed for reproducible generation")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown", "both"]),
    default="both",
    help="Output format",
)
def main(output_dir: str, count: int, seed: int, format: str):
    """Generate hierarchical course catalog with syllabi and assignments."""

    print(f"🎓 Generating {count} courses with full details...\n")

    generator = HierarchicalCourseGenerator(seed=seed)
    courses = generator.generate_courses(count)

    output_path = Path(output_dir)

    if format in ["json", "both"]:
        print("\n📄 Saving to JSON...")
        generator.save_to_json(output_path)

    if format in ["markdown", "both"]:
        print("\n📝 Saving to Markdown...")
        generator.save_to_markdown(output_path)

    print(f"\n✅ Generation complete!")
    print(f"   Total courses: {len(courses)}")
    print(f"   Output directory: {output_path.absolute()}")

    # Print summary statistics
    total_assignments = sum(c.details.get_total_assignments() for c in courses)
    total_weeks = sum(c.details.syllabus.total_weeks for c in courses)

    print(f"\n📊 Statistics:")
    print(f"   Total assignments: {total_assignments}")
    print(f"   Total weeks of content: {total_weeks}")
    print(f"   Average assignments per course: {total_assignments / len(courses):.1f}")
    print(f"   Average weeks per course: {total_weeks / len(courses):.1f}")


if __name__ == "__main__":
    main()
