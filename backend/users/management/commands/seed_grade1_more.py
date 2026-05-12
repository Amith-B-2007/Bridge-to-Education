"""
python manage.py seed_grade1_more

Adds an extra batch of Grade 1 quizzes (12 quizzes, 6 questions each = 72 new
questions) across Maths, English, Science (EVS) and Kannada.

Uses chapter numbers >= 21 to avoid collisions with the original Grade 1 set.
Idempotent — re-running is safe.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from users.models import Teacher
from resources.models import Subject, Chapter
from quizzes.models import Quiz, Question

User = get_user_model()


def _q(text, opts, correct, explanation="", difficulty="easy"):
    return {
        "text": text,
        "options": [{"key": k, "text": v} for k, v in zip(["a", "b", "c", "d"], opts)],
        "correct": correct,
        "explanation": explanation,
        "difficulty": difficulty,
    }


# (subject_code, chap_num, chapter_title, [questions]) — all Grade 1
QUIZZES = [

    # ─── MATHS (4 more) ──────────────────────────────────────────────────
    ("maths", 21, "Counting Backwards", [
        _q("After 10, counting backwards next is:", ["11", "9", "0", "8"], "b", "10 → 9 → 8 ...", "easy"),
        _q("Count back from 5: 5, 4, 3, ?", ["1", "2", "0", "5"], "b", "5,4,3,2", "easy"),
        _q("Number just before 7:", ["5", "6", "8", "9"], "b", "Before 7 = 6", "easy"),
        _q("Counting back: 20, 19, 18, ?", ["16", "17", "21", "0"], "b", "Subtract 1 each time", "easy"),
        _q("If a rocket counts down 3, 2, 1, what comes next?", ["0 (lift-off!)", "5", "10", "−1"], "a", "Countdown ends at zero", "easy"),
        _q("Counting backwards by 1, the smallest counting number is:", ["0", "1", "10", "20"], "a", "We stop at zero in normal counting", "easy"),
    ]),
    ("maths", 22, "Comparing Numbers", [
        _q("Which is greater: 8 or 5?", ["8", "5", "Equal", "Cannot tell"], "a", "8 > 5", "easy"),
        _q("Which is smaller: 12 or 9?", ["12", "9", "Equal", "Cannot tell"], "b", "9 < 12", "easy"),
        _q("Sign for 'greater than':", ["<", ">", "=", "+"], "b", "> means greater than", "easy"),
        _q("Compare: 0 ___ 1", ["<", ">", "=", "×"], "a", "0 is less than 1", "easy"),
        _q("Largest number among: 3, 7, 5, 2:", ["3", "7", "5", "2"], "b", "7 is the biggest", "easy"),
        _q("Smallest number among: 9, 4, 6, 1:", ["9", "4", "6", "1"], "d", "1 is the smallest", "easy"),
    ]),
    ("maths", 23, "Money Basics", [
        _q("Indian currency is the:", ["Dollar", "Rupee (₹)", "Pound", "Yen"], "b", "₹ Rupee", "easy"),
        _q("Symbol of Rupee:", ["$", "₹", "€", "¥"], "b", "₹", "easy"),
        _q("How many ₹1 coins make ₹5?", ["3", "4", "5", "10"], "c", "5 × 1 = 5", "easy"),
        _q("How many ₹2 coins make ₹10?", ["2", "5", "8", "10"], "b", "5 × 2 = 10", "easy"),
        _q("If a toffee costs ₹2 and you buy 3, total is:", ["₹3", "₹5", "₹6", "₹10"], "c", "3 × 2 = 6", "easy"),
        _q("Which is bigger amount: ₹10 or ₹5?", ["₹10", "₹5", "Equal", "Cannot tell"], "a", "₹10 > ₹5", "easy"),
    ]),
    ("maths", 24, "Time Basics", [
        _q("Number of days in a week:", ["5", "6", "7", "8"], "c", "7 days", "easy"),
        _q("First day of the week (in school):", ["Sunday", "Monday", "Tuesday", "Saturday"], "b", "Mon → Fri school days", "easy"),
        _q("Day after Monday:", ["Sunday", "Tuesday", "Friday", "Saturday"], "b", "Mon → Tue", "easy"),
        _q("Time to wake up usually:", ["Morning", "Midnight", "Late night", "Evening"], "a", "Morning", "easy"),
        _q("Time to go to sleep usually:", ["Morning", "Afternoon", "Night", "Lunchtime"], "c", "Night", "easy"),
        _q("Number of months in a year:", ["10", "11", "12", "13"], "c", "12 months", "easy"),
    ]),

    # ─── ENGLISH (3 more) ────────────────────────────────────────────────
    ("english", 21, "Bubbles (Poem)", [
        _q("Bubbles are usually:", ["Heavy", "Light and float in air", "Made of stone", "Square"], "b", "Light, fly with air", "easy"),
        _q("Bubbles are made by mixing soap with:", ["Sand", "Water", "Oil", "Stone"], "b", "Soap + water → bubbles", "easy"),
        _q("Bubbles are usually:", ["Square", "Round", "Triangle", "Long"], "b", "Spheres", "easy"),
        _q("When bubble touches something hard, it:", ["Grows bigger", "Pops / bursts", "Becomes a stone", "Hides"], "b", "Bubble bursts", "easy"),
        _q("Children love bubbles because they are:", ["Boring", "Fun and colourful", "Sad", "Heavy"], "b", "Fun for play", "easy"),
        _q("Colours seen on a bubble are because of:", ["Paint", "Light reflecting on the thin film", "Smoke", "Salt"], "b", "Light interference makes rainbows", "medium"),
    ]),
    ("english", 22, "Hide and Seek", [
        _q("'Hide and Seek' is a:", ["Song", "Game children play", "Story only", "Drink"], "b", "Popular children's game", "easy"),
        _q("In hide and seek, one player is the:", ["Cook", "Seeker", "Driver", "King"], "b", "Seeker hunts the hiders", "easy"),
        _q("To play, you need at least:", ["1 person", "2 people", "10 people only", "100 people"], "b", "Minimum 2 to play", "easy"),
        _q("Children hide so they will not be:", ["Loved", "Found / seen by the seeker", "Fed", "Watered"], "b", "Stay hidden", "easy"),
        _q("This game is usually played:", ["Indoors and outdoors", "Only in space", "Only in water", "Only at night"], "a", "Either indoors or outdoors", "easy"),
        _q("The game teaches us:", ["To shout always", "Patience and quietness", "To break things", "To be lazy"], "b", "Patience and being quiet", "easy"),
    ]),
    ("english", 23, "Lalu and Peelu", [
        _q("Lalu and Peelu were two:", ["Boys", "Chickens (chicks)", "Trees", "Cars"], "b", "Two pet chicks", "easy"),
        _q("'Lalu' (in story) likes red things and 'Peelu' likes:", ["Green", "Yellow", "Black", "White"], "b", "Peelu = peela = yellow", "easy"),
        _q("Lalu pecks at:", ["Black stones only", "Red things (a chilli)", "Books", "Soap"], "b", "Red chilli — turns out spicy", "medium"),
        _q("After eating the chilli, Lalu felt:", ["Happy", "Sick / spicy mouth", "Sleepy", "Hungry"], "b", "Hot, spicy", "easy"),
        _q("The story teaches us:", ["Not everything that looks nice is good", "To never share", "To eat anything", "To stay sad"], "a", "Don't judge by colour alone", "easy"),
        _q("Peelu eats:", ["Coal", "Yellow grain (corn)", "Stones", "Plastic"], "b", "Yellow corn / grain", "easy"),
    ]),

    # ─── EVS (science) (3 more) ──────────────────────────────────────────
    ("science", 21, "Plants Around Us", [
        _q("Plants need ___ to grow:", ["Only sunlight", "Water, sunlight, air, soil", "Only TV", "Only milk"], "b", "All needed for growth", "easy"),
        _q("Roots of a plant grow:", ["Up to the sky", "Down into soil", "Sideways only", "On leaves"], "b", "Roots go into soil", "easy"),
        _q("Most leaves are coloured:", ["Black", "Green", "Red always", "Blue"], "b", "Chlorophyll = green", "easy"),
        _q("A young new plant from a seed is called a:", ["Twig", "Sapling", "Stone", "Stem only"], "b", "Sapling = young plant", "medium"),
        _q("Mango grows on a:", ["Bush", "Tree", "Creeper", "Grass"], "b", "Mango tree", "easy"),
        _q("Plants give us:", ["Just smoke", "Food, oxygen and shade", "Anger", "Lies"], "b", "Food + O₂ + shade", "easy"),
    ]),
    ("science", 22, "Food We Eat", [
        _q("Food gives us:", ["Sleep only", "Energy and nutrients to grow", "Sadness", "Boredom"], "b", "Energy + nutrients", "easy"),
        _q("Roti / chapati is made from:", ["Sugar", "Wheat flour", "Salt", "Plastic"], "b", "Wheat → flour → roti", "easy"),
        _q("We eat ___ for protein:", ["Stones", "Pulses (dal), eggs, milk", "Sand", "Paper"], "b", "Dal/eggs/milk", "easy"),
        _q("Healthy snack:", ["Chocolate only", "Fruits like apple, banana", "Stones", "Plastic chips"], "b", "Fruits", "easy"),
        _q("Before eating we should:", ["Sleep", "Wash our hands", "Run", "Cry"], "b", "Wash hands for hygiene", "easy"),
        _q("Drinking enough ___ keeps us healthy:", ["Petrol", "Water", "Mud", "Oil"], "b", "Water keeps body hydrated", "easy"),
    ]),
    ("science", 23, "Seasons", [
        _q("Hot season is called:", ["Winter", "Summer", "Rainy", "Autumn"], "b", "Summer = hot", "easy"),
        _q("Cold season is called:", ["Summer", "Winter", "Rainy", "Spring"], "b", "Winter = cold", "easy"),
        _q("In rainy season we use a/an:", ["Sweater", "Umbrella / raincoat", "Sunglasses only", "Sandals only"], "b", "Umbrella keeps us dry", "easy"),
        _q("In summer we wear:", ["Heavy woolen clothes", "Light cotton clothes", "Snow boots", "Raincoats only"], "b", "Cotton is cool", "easy"),
        _q("Spring season has:", ["Snow", "Many flowers blooming", "Heavy rain only", "Storms only"], "b", "Spring = flowers bloom", "easy"),
        _q("Festival of colours that comes in spring:", ["Diwali", "Holi", "Eid", "Christmas"], "b", "Holi celebrates spring", "medium"),
    ]),

    # ─── KANNADA (2 more) ────────────────────────────────────────────────
    ("kannada", 21, "Sankhyegalu (Numbers)", [
        _q("'Ondu' means:", ["Two", "One", "Three", "Four"], "b", "Ondu = 1", "easy"),
        _q("'Eradu' means:", ["One", "Two", "Three", "Four"], "b", "Eradu = 2", "easy"),
        _q("'Mooru' means:", ["Two", "Three", "Four", "Five"], "b", "Mooru = 3", "easy"),
        _q("'Aidu' means:", ["Four", "Five", "Six", "Seven"], "b", "Aidu = 5", "easy"),
        _q("'Hattu' means:", ["Eight", "Nine", "Ten", "Eleven"], "c", "Hattu = 10", "easy"),
        _q("'Naalku' means:", ["Three", "Four", "Five", "Six"], "b", "Naalku = 4", "easy"),
    ]),
    ("kannada", 22, "Dehada Bhagagalu (Body Parts)", [
        _q("'Kannu' means:", ["Eye", "Nose", "Ear", "Hand"], "a", "Kannu = eye", "easy"),
        _q("'Mookha' means:", ["Ear", "Nose", "Eye", "Foot"], "b", "Mooku/Mookha = nose", "easy"),
        _q("'Kivi' means:", ["Hand", "Eye", "Ear", "Foot"], "c", "Kivi = ear", "easy"),
        _q("'Kai' means:", ["Hand", "Leg", "Eye", "Mouth"], "a", "Kai = hand", "easy"),
        _q("'Baayi' means:", ["Eye", "Mouth", "Nose", "Hair"], "b", "Baayi = mouth", "easy"),
        _q("'Tale' means:", ["Foot", "Head", "Hand", "Stomach"], "b", "Tale = head", "easy"),
    ]),
]


class Command(BaseCommand):
    help = "Add MORE Grade 1 quizzes (Maths, English, EVS, Kannada) — 12 quizzes, 6 questions each."

    def handle(self, *args, **options):
        teacher_user = User.objects.filter(role="teacher").first()
        if not teacher_user:
            teacher_user, _ = User.objects.get_or_create(
                username="teacher",
                defaults={
                    "email": "teacher@demo.ruralsiksha.in",
                    "first_name": "Demo",
                    "last_name": "Teacher",
                    "role": "teacher",
                },
            )
            teacher_user.set_password("teacher123")
            teacher_user.save()

        teacher, _ = Teacher.objects.get_or_create(
            user=teacher_user,
            defaults={
                "assigned_grades": "1,2,3,4,5,6,7,8,9,10",
                "assigned_subjects": "maths,science,english,social_science,kannada",
            },
        )

        added_quizzes = 0
        added_questions = 0
        skipped_questions = 0

        for subject_code, chap_num, chap_title, questions in QUIZZES:
            subj, _ = Subject.objects.get_or_create(name=subject_code)
            chapter, _ = Chapter.objects.get_or_create(
                subject=subj, grade=1, chapter_number=chap_num,
                defaults={
                    "title": chap_title,
                    "description": f"Grade 1 {chap_title}",
                },
            )

            quiz_title = f"{chap_title} - Quiz"
            quiz, created = Quiz.objects.get_or_create(
                chapter=chapter,
                title=quiz_title,
                defaults={
                    "subject": subject_code,
                    "grade": 1,
                    "description": f"Practice quiz on {chap_title}",
                    "num_questions": len(questions),
                    "duration_minutes": 10,
                    "passing_percentage": 40.0,
                    "is_published": True,
                    "created_by": teacher,
                },
            )
            if created:
                added_quizzes += 1

            for qd in questions:
                _, q_created = Question.objects.get_or_create(
                    quiz=quiz,
                    question_text=qd["text"],
                    defaults={
                        "options_json": qd["options"],
                        "correct_answer": qd["correct"],
                        "explanation": qd.get("explanation", ""),
                        "difficulty": qd.get("difficulty", "easy"),
                        "marks": 1,
                    },
                )
                if q_created:
                    added_questions += 1
                else:
                    skipped_questions += 1

            quiz.num_questions = quiz.questions.count()
            quiz.save(update_fields=["num_questions"])

        self.stdout.write(self.style.SUCCESS(
            f"\nGrade 1 expansion: +{added_quizzes} new quizzes, "
            f"+{added_questions} new questions, {skipped_questions} duplicates skipped."
        ))
