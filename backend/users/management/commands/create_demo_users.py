from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Student, Teacher

User = get_user_model()


class Command(BaseCommand):
    help = 'Create demo users for testing'

    def handle(self, *args, **options):
        # Create or update demo student
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@ruralsiksha.com',
                'first_name': 'Demo',
                'last_name': 'Student',
            }
        )
        if created:
            demo_user.set_password('demo123')
        demo_user.role = 'student'
        demo_user.save()
        Student.objects.get_or_create(user=demo_user, defaults={'grade': 5})
        self.stdout.write(
            self.style.SUCCESS('✓ Demo student ready (username: demo, password: demo123)')
        )

        # Create or update test student
        test_user, created = User.objects.get_or_create(
            username='testuser123',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
            }
        )
        if created:
            test_user.set_password('password123')
        test_user.role = 'student'
        test_user.save()
        Student.objects.get_or_create(user=test_user, defaults={'grade': 6})
        self.stdout.write(
            self.style.SUCCESS('✓ Test student ready (username: testuser123, password: password123)')
        )

        # Create or update demo teacher
        teacher_user, created = User.objects.get_or_create(
            username='teacher_demo',
            defaults={
                'email': 'teacher@ruralsiksha.com',
                'first_name': 'Demo',
                'last_name': 'Teacher',
            }
        )
        if created:
            teacher_user.set_password('teacher123')
        teacher_user.role = 'teacher'
        teacher_user.save()
        Teacher.objects.get_or_create(user=teacher_user)
        self.stdout.write(
            self.style.SUCCESS('✓ Demo teacher ready (username: teacher_demo, password: teacher123)')
        )

        self.stdout.write(self.style.SUCCESS('\n✓ Demo users created successfully!'))


