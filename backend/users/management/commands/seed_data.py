"""
Run with:  python manage.py seed_data

Populates the DB with demo content so the frontend has things to show.
Idempotent — safe to run multiple times.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Student, Teacher
from resources.models import Subject, Chapter, Resource
from quizzes.models import Quiz, Question
from doubts.models import DoubtSession, DoubtMessage

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with demo students/teachers/resources/quizzes/doubts"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...\n")

        # ---------- Users ----------
        demo, _ = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@x.com", "first_name": "Demo", "last_name": "Student", "role": "student"},
        )
        if not demo.has_usable_password():
            demo.set_password("demo123")
            demo.save()
        student, _ = Student.objects.get_or_create(user=demo, defaults={"grade": 5})

        teacher_user, _ = User.objects.get_or_create(
            username="teacher",
            defaults={"email": "t@x.com", "first_name": "Demo", "last_name": "Teacher", "role": "teacher"},
        )
        if not teacher_user.has_usable_password():
            teacher_user.set_password("teacher123")
            teacher_user.save()
        teacher, _ = Teacher.objects.get_or_create(
            user=teacher_user,
            defaults={"assigned_grades": "5,6,7", "assigned_subjects": "maths,science"},
        )
        self.stdout.write(self.style.SUCCESS("   Users (demo / teacher)"))

        # ---------- Subjects ----------
        subjects = {}
        for code, _label in [("maths", "Mathematics"), ("science", "Science"), ("english", "English")]:
            s, _ = Subject.objects.get_or_create(name=code)
            subjects[code] = s
        self.stdout.write(self.style.SUCCESS("   Subjects"))

        # ---------- Chapters + Resources + Quizzes ----------
        chapters_data = [
            ("maths", 5, 1, "Numbers & Place Value"),
            ("maths", 5, 2, "Addition & Subtraction"),
            ("maths", 5, 3, "Multiplication"),
            ("maths", 5, 4, "Fractions"),
            ("science", 5, 1, "Living Things"),
            ("science", 5, 2, "Plants Around Us"),
            ("english", 5, 1, "Grammar Basics"),
        ]

        for code, grade, num, title in chapters_data:
            ch, _ = Chapter.objects.get_or_create(
                subject=subjects[code],
                grade=grade,
                chapter_number=num,
                defaults={"title": title, "description": f"Class {grade} - {title}"},
            )

            # Resource for this chapter (sample placeholder URL)
            Resource.objects.get_or_create(
                chapter=ch,
                title=f"{title} - Notes",
                defaults={
                    "description": f"Comprehensive PDF notes for {title}.",
                    "resource_type": "pdf",
                    "grade": grade,
                    "subject": code,
                    "uploaded_by": teacher,
                    "file_path": "https://example.com/sample.pdf",
                    "file_size": 1024 * 200,
                    "is_approved": True,
                },
            )
            Resource.objects.get_or_create(
                chapter=ch,
                title=f"{title} - Video Lesson",
                defaults={
                    "description": f"Animated video explaining {title}.",
                    "resource_type": "video",
                    "grade": grade,
                    "subject": code,
                    "uploaded_by": teacher,
                    "file_path": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "file_size": 1024 * 1024 * 5,
                    "is_approved": True,
                },
            )

            # Quiz for this chapter
            quiz, created = Quiz.objects.get_or_create(
                chapter=ch,
                title=f"{title} - Practice Quiz",
                defaults={
                    "description": f"Test your understanding of {title}.",
                    "subject": code,
                    "grade": grade,
                    "num_questions": 3,
                    "duration_minutes": 10,
                    "passing_percentage": 50,
                    "is_published": True,
                    "created_by": teacher,
                },
            )

            if created:
                # Add 3 sample MCQs per chapter
                Question.objects.create(
                    quiz=quiz,
                    question_text=f"Sample question 1 about {title}?",
                    options_json=[
                        {"key": "a", "text": "Option A (correct)"},
                        {"key": "b", "text": "Option B"},
                        {"key": "c", "text": "Option C"},
                        {"key": "d", "text": "Option D"},
                    ],
                    correct_answer="a",
                    explanation="Option A is the correct answer.",
                    difficulty="easy",
                    marks=1,
                )
                Question.objects.create(
                    quiz=quiz,
                    question_text=f"Sample question 2 about {title}?",
                    options_json=[
                        {"key": "a", "text": "Wrong"},
                        {"key": "b", "text": "Correct answer"},
                        {"key": "c", "text": "Wrong"},
                        {"key": "d", "text": "Wrong"},
                    ],
                    correct_answer="b",
                    explanation="Option B is correct.",
                    difficulty="medium",
                    marks=1,
                )
                Question.objects.create(
                    quiz=quiz,
                    question_text=f"Sample question 3 about {title}?",
                    options_json=[
                        {"key": "a", "text": "Wrong"},
                        {"key": "b", "text": "Wrong"},
                        {"key": "c", "text": "Correct"},
                        {"key": "d", "text": "Wrong"},
                    ],
                    correct_answer="c",
                    explanation="Option C is correct.",
                    difficulty="medium",
                    marks=1,
                )

        self.stdout.write(self.style.SUCCESS(f"   {len(chapters_data)} chapters with resources & quizzes"))

        # ---------- Doubts ----------
        DoubtSession.objects.get_or_create(
            student=student,
            subject="Maths",
            description="I don't understand how to add fractions with different denominators. Can you help?",
            defaults={"status": "open"},
        )
        DoubtSession.objects.get_or_create(
            student=student,
            subject="Science",
            description="What is the difference between plants and animals?",
            defaults={"status": "open"},
        )
        self.stdout.write(self.style.SUCCESS("   Sample doubts"))

        self.stdout.write(self.style.SUCCESS("\n Done! Demo data ready.\n"))
        self.stdout.write("Login as:")
        self.stdout.write("  Student:  demo / demo123")
        self.stdout.write("  Teacher:  teacher / teacher123")
