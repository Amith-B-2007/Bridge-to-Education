"""
python manage.py seed_extra_quizzes

Adds an extra set of curriculum quizzes (and questions) on top of what
seed_demo_data + seed_questions + seed_lower_grades already produced.

Uses chapter numbers >= 11 so it never collides with the original chapters.
Safe to re-run.
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


# (grade, subject_code, chap_num, chapter_title, [questions])
QUIZZES = [

    # ─── GRADE 1 (extra) ─────────────────────────────────────────────────
    (1, "maths", 11, "Subtraction", [
        _q("5 − 2 = ?", ["1", "2", "3", "4"], "c", "5 − 2 = 3", "easy"),
        _q("9 − 4 = ?", ["3", "4", "5", "6"], "c", "9 − 4 = 5", "easy"),
        _q("If you have 8 candies and eat 3, how many left?", ["3", "4", "5", "6"], "c", "8 − 3 = 5", "easy"),
    ]),
    (1, "maths", 12, "Shapes", [
        _q("A shape with 3 sides is a:", ["Square", "Triangle", "Circle", "Star"], "b", "Tri = 3 sides", "easy"),
        _q("A circle has how many corners?", ["0", "1", "2", "4"], "a", "Circle has no corners", "easy"),
        _q("A square has how many equal sides?", ["2", "3", "4", "6"], "c", "Square has 4 equal sides", "easy"),
    ]),
    (1, "english", 11, "One Little Kitten", [
        _q("In the poem, how many kittens?", ["One", "Two", "Three", "Four"], "a", "Title says 'One Little Kitten'", "easy"),
        _q("A baby cat is called a:", ["Puppy", "Kitten", "Calf", "Cub"], "b", "Baby cat = kitten", "easy"),
        _q("Kittens like to drink:", ["Tea", "Milk", "Coffee", "Juice"], "b", "Kittens love milk", "easy"),
    ]),
    (1, "science", 11, "Birds Around Us", [
        _q("Birds fly using their:", ["Legs", "Wings", "Tail", "Beak"], "b", "Wings help birds fly", "easy"),
        _q("Birds lay:", ["Babies", "Eggs", "Seeds", "Stones"], "b", "Birds lay eggs", "easy"),
        _q("Which is NOT a bird?", ["Crow", "Sparrow", "Bat", "Parrot"], "c", "A bat is a mammal, not a bird", "medium"),
    ]),

    # ─── GRADE 2 (extra) ─────────────────────────────────────────────────
    (2, "maths", 11, "Patterns", [
        _q("Continue the pattern: 2, 4, 6, 8, ?", ["9", "10", "11", "12"], "b", "Skip count by 2: 8+2 = 10", "easy"),
        _q("In the pattern A, B, A, B, A, ? — what comes next?", ["A", "B", "C", "D"], "b", "ABAB → next is B", "easy"),
        _q("5, 10, 15, 20, ?", ["22", "24", "25", "30"], "c", "Skip count by 5", "easy"),
    ]),
    (2, "maths", 12, "Time", [
        _q("How many days in one week?", ["5", "6", "7", "8"], "c", "7 days in a week", "easy"),
        _q("Number of months in a year:", ["10", "11", "12", "13"], "c", "12 months", "easy"),
        _q("How many hours in one day?", ["12", "20", "24", "30"], "c", "24 hours", "medium"),
    ]),
    (2, "english", 11, "Storm in the Garden", [
        _q("In the story a storm comes to the:", ["School", "Garden / yard", "Hospital", "Train station"], "b", "Storm in the garden", "easy"),
        _q("Storms usually bring:", ["Sunshine only", "Strong winds and rain", "Snow only", "Quiet"], "b", "Wind and rain together", "easy"),
        _q("After the storm the garden is:", ["Cleaner / refreshed", "Burnt", "Frozen", "Empty forever"], "a", "Rain washes plants", "easy"),
    ]),
    (2, "science", 11, "Things We Wear", [
        _q("In summer we wear:", ["Wool sweaters", "Cotton clothes", "Raincoats only", "Heavy coats"], "b", "Cotton is cool", "easy"),
        _q("In winter we wear:", ["Sleeveless shirts", "Warm woollen clothes", "Swimsuits", "Slippers only"], "b", "Wool keeps us warm", "easy"),
        _q("Raincoats are made of:", ["Paper", "Waterproof material like plastic", "Wool", "Cotton"], "b", "Plastic / rubber repels water", "medium"),
    ]),

    # ─── GRADE 3 (extra) ─────────────────────────────────────────────────
    (3, "maths", 11, "Time and Money", [
        _q("How many minutes in 1 hour?", ["30", "45", "60", "90"], "c", "60 minutes", "easy"),
        _q("100 paise = ₹ ?", ["1", "10", "100", "1000"], "a", "100 paise = 1 rupee", "easy"),
        _q("If 1 pen costs ₹5, then 4 pens cost:", ["₹15", "₹20", "₹25", "₹30"], "b", "4 × 5 = ₹20", "medium"),
    ]),
    (3, "maths", 12, "Smart Charts (Data)", [
        _q("A simple way to show data is a:", ["Story", "Bar chart / pictograph", "Poem", "Drawing of a face"], "b", "Bar charts and pictographs", "easy"),
        _q("If 5 children like apples and 3 like mangoes, more like:", ["Mangoes", "Apples", "Same", "Bananas"], "b", "5 > 3", "easy"),
        _q("The most common value in a list is the:", ["Mean", "Mode", "Total", "Range"], "b", "Mode = most common", "medium"),
    ]),
    (3, "english", 11, "Little by Little", [
        _q("'Little by little' means:", ["All at once", "Slowly, step by step", "Never", "Backwards"], "b", "Gradually", "easy"),
        _q("In the poem, who is growing little by little?", ["A river", "An acorn becoming a tree", "A car", "A building"], "b", "Tiny acorn grows into oak", "medium"),
        _q("The poem teaches us:", ["To rush", "Patience and steady effort", "To give up easily", "To be lazy"], "b", "Steady growth and patience", "easy"),
    ]),
    (3, "science", 11, "Air Around Us", [
        _q("Air is:", ["Visible like water", "Invisible but everywhere", "A solid", "Found only in books"], "b", "Air is around us, invisible", "easy"),
        _q("We breathe air to take in:", ["Carbon dioxide", "Oxygen", "Hydrogen", "Helium"], "b", "Oxygen is needed for life", "easy"),
        _q("Wind is:", ["Still air", "Moving air", "Hot only", "Heavy water"], "b", "Wind = air in motion", "easy"),
    ]),

    # ─── GRADE 4 (extra) ─────────────────────────────────────────────────
    (4, "maths", 11, "Tick-Tick-Tick (Time)", [
        _q("12:00 noon comes after:", ["11:00 AM", "1:00 PM", "10:00 PM", "Midnight"], "a", "11 AM → 12 noon", "easy"),
        _q("How many seconds in 1 minute?", ["30", "45", "60", "100"], "c", "60 seconds", "easy"),
        _q("From 9:30 AM to 11:30 AM is:", ["1 hour", "2 hours", "3 hours", "30 minutes"], "b", "Difference = 2 hours", "medium"),
    ]),
    (4, "maths", 12, "Jugs and Mugs (Capacity)", [
        _q("1 litre = ___ millilitres", ["10", "100", "1000", "10000"], "c", "1 L = 1000 mL", "easy"),
        _q("Best unit to measure water in a glass:", ["Litre", "Millilitre", "Kilolitre", "Metre"], "b", "Glass holds about 200 mL", "medium"),
        _q("A bucket usually holds about:", ["1 mL", "100 mL", "10–15 L", "100 L"], "c", "Buckets typically hold 10-15 litres", "medium"),
    ]),
    (4, "english", 11, "Why? (Poem)", [
        _q("The child in the poem keeps asking:", ["For sweets", "'Why?' about everything", "For toys", "For money"], "b", "Curiosity = lots of why questions", "easy"),
        _q("Asking 'why' shows:", ["Foolishness", "Curiosity / wanting to learn", "Anger", "Fear"], "b", "Curiosity helps us learn", "easy"),
        _q("Children ask 'why' to:", ["Annoy parents", "Understand the world", "Be lazy", "Sleep more"], "b", "Understanding the world", "easy"),
    ]),
    (4, "science", 11, "From Market to Home", [
        _q("Vegetables are grown by:", ["Doctors", "Farmers", "Engineers", "Pilots"], "b", "Farmers grow crops", "easy"),
        _q("Vegetables move from farm to market in a:", ["Plane", "Truck or cart", "Boat only", "Submarine"], "b", "Trucks/carts transport produce", "easy"),
        _q("A weekly market is called a:", ["Mall", "Santhe / haat", "Supermarket", "Stadium"], "b", "Santhe = village weekly market", "medium"),
    ]),

    # ─── GRADE 5 (extra) ─────────────────────────────────────────────────
    (5, "maths", 11, "The Junk Seller (Money)", [
        _q("If 1 kg paper sells for ₹8, what is 5 kg worth?", ["₹30", "₹35", "₹40", "₹45"], "c", "5 × 8 = ₹40", "easy"),
        _q("₹100 − ₹37 = ?", ["₹53", "₹63", "₹73", "₹83"], "b", "100 − 37 = 63", "easy"),
        _q("How many ₹10 notes make ₹100?", ["5", "8", "10", "20"], "c", "10 × 10 = 100", "easy"),
    ]),
    (5, "science", 11, "Every Drop Counts (Water)", [
        _q("A simple way to save water at home is:", ["Leave taps running", "Close taps when not in use", "Take very long baths", "Wash car daily with hose"], "b", "Closed tap saves water", "easy"),
        _q("Drinking water at home is best stored:", ["In open dirty buckets", "In a clean covered container", "On the floor", "In paper bags"], "b", "Covered = clean and germ-free", "easy"),
        _q("Rainwater harvesting means:", ["Wasting rain", "Collecting and storing rainwater", "Burning rain", "Drinking dirty water"], "b", "Save rain for later use", "medium"),
    ]),
    (5, "english", 11, "My Shadow (Poem)", [
        _q("Author of 'My Shadow':", ["R L Stevenson", "Wordsworth", "Tagore", "Frost"], "a", "Robert Louis Stevenson", "medium"),
        _q("Where does the poet's shadow follow him?", ["Only at night", "Wherever he goes", "Only in school", "Only in the rain"], "b", "Shadow always follows", "easy"),
        _q("The poet finds his shadow:", ["Boring", "Funny / strange", "Frightening always", "Useless"], "b", "He observes it with humour", "easy"),
    ]),

    # ─── GRADE 6 (extra) ─────────────────────────────────────────────────
    (6, "maths", 11, "Integers", [
        _q("Which is the smallest integer?", ["-5", "-1", "0", "5"], "a", "More negative = smaller", "easy"),
        _q("(-3) + 5 = ?", ["-8", "-2", "2", "8"], "c", "5 − 3 = 2", "easy"),
        _q("Which integer is neither positive nor negative?", ["-1", "0", "1", "100"], "b", "Zero is neutral", "easy"),
    ]),
    (6, "science", 11, "Body Movements", [
        _q("Bones meet at:", ["Skin", "Joints", "Muscles", "Hair"], "b", "Joints connect bones", "easy"),
        _q("Hinge joint is found at the:", ["Shoulder", "Elbow / knee", "Skull", "Spine"], "b", "Elbows and knees bend like hinges", "medium"),
        _q("The hard, protective box around the brain is the:", ["Ribcage", "Skull", "Spine", "Pelvis"], "b", "Skull protects the brain", "easy"),
    ]),
    (6, "english", 11, "The Friendly Mongoose", [
        _q("The mongoose was a pet of a:", ["Tiger", "Farmer's family", "Lion", "King"], "b", "Farmer brought it home for the baby", "easy"),
        _q("The mongoose saved the baby from a:", ["Crow", "Snake", "Dog", "Spider"], "b", "Mongoose killed the snake", "easy"),
        _q("The farmer's wife mistakenly thought the mongoose:", ["Stole gold", "Had killed the baby (because of blood on its mouth)", "Ran away", "Slept all day"], "b", "She judged hastily", "medium"),
    ]),

    # ─── GRADE 7 (extra) ─────────────────────────────────────────────────
    (7, "maths", 11, "The Triangle and its Properties", [
        _q("Sum of all interior angles of a triangle:", ["90°", "180°", "270°", "360°"], "b", "Always 180°", "easy"),
        _q("In a right triangle, one angle is exactly:", ["45°", "60°", "90°", "120°"], "c", "Right angle = 90°", "easy"),
        _q("An equilateral triangle has all angles equal to:", ["45°", "60°", "75°", "90°"], "b", "180° / 3 = 60°", "medium"),
    ]),
    (7, "science", 11, "Wind, Storms and Cyclones", [
        _q("Hot air is ___ than cold air.", ["Heavier", "Lighter", "Same weight", "Solid"], "b", "Hot air rises (lighter)", "easy"),
        _q("A very strong wind storm with eye is called a:", ["Breeze", "Cyclone / hurricane", "Drizzle", "Frost"], "b", "Cyclone has a calm 'eye'", "medium"),
        _q("Cyclones often hit the ___ coast of India most:", ["Northern", "Eastern", "Western", "None"], "b", "Bay of Bengal — east coast", "medium"),
    ]),
    (7, "english", 11, "The Ashes That Made Trees Bloom", [
        _q("This story is set in:", ["India", "Japan", "Russia", "USA"], "b", "Japanese folk tale", "easy"),
        _q("The good old man's pet was a:", ["Cat", "Dog", "Bird", "Rabbit"], "b", "A faithful dog", "easy"),
        _q("The story teaches that:", ["Greed brings good luck", "Kindness is rewarded; greed is punished", "Money is most important", "Magic always wins"], "b", "Moral about kindness vs greed", "medium"),
    ]),

    # ─── GRADE 8 (extra) ─────────────────────────────────────────────────
    (8, "maths", 11, "Algebraic Expressions and Identities", [
        _q("Coefficient of x in 5x + 3:", ["3", "5", "x", "15"], "b", "Number multiplying x is 5", "easy"),
        _q("(a + b)² = ?", ["a² + b²", "a² + 2ab + b²", "a² − 2ab + b²", "ab"], "b", "Standard identity", "medium"),
        _q("(x + 2)(x + 3) = ?", ["x² + 5x + 6", "x² + 6", "x² + 5", "x² − 6"], "a", "x² + 5x + 6 by FOIL", "medium"),
    ]),
    (8, "science", 11, "Friction", [
        _q("Friction always opposes:", ["Motion", "Mass", "Time", "Volume"], "a", "Friction opposes relative motion", "easy"),
        _q("Friction is ___ on rough surfaces:", ["Less", "Greater", "Zero", "Negative"], "b", "Rough = more friction", "easy"),
        _q("Lubricants are used to:", ["Increase friction", "Reduce friction", "Increase weight", "Stop motion"], "b", "Oil/grease reduces friction", "medium"),
    ]),
    (8, "english", 11, "Bepin Choudhury's Lapse of Memory", [
        _q("Author of the story:", ["Satyajit Ray", "Tagore", "R K Narayan", "Premchand"], "a", "Famous Bengali writer & filmmaker", "medium"),
        _q("The story is about Bepin Babu's:", ["Lost wallet", "Memory loss / confusion", "Wedding", "New car"], "b", "He cannot remember a Ranchi trip", "easy"),
        _q("The whole 'incident' was actually:", ["Real", "A practical joke / planned trick by a friend", "A dream", "An accident"], "b", "Friend Chunilal played a prank to get back at him", "medium"),
    ]),

    # ─── GRADE 9 (extra) ─────────────────────────────────────────────────
    (9, "maths", 11, "Triangles", [
        _q("Two triangles are congruent if their corresponding sides and angles are:", ["Different", "Equal", "Doubled", "Halved"], "b", "Congruent = exactly equal", "easy"),
        _q("SSS criterion checks:", ["3 angles", "3 sides", "2 sides + 1 angle", "1 side + 2 angles"], "b", "Side-Side-Side", "medium"),
        _q("Sum of any two sides of a triangle is ___ the third side.", ["Less than", "Equal to", "Greater than", "Half of"], "c", "Triangle inequality", "medium"),
    ]),
    (9, "science", 11, "Force and Laws of Motion", [
        _q("Newton's first law is also called the law of:", ["Action–reaction", "Inertia", "Gravity", "Friction"], "b", "Inertia: object stays in motion/rest unless acted on", "easy"),
        _q("Force = ?", ["mass + acceleration", "mass × acceleration", "mass / acceleration", "mass − acceleration"], "b", "F = m × a (Newton's 2nd law)", "medium"),
        _q("To every action there is an equal and opposite ___:", ["Push", "Reaction", "Weight", "Speed"], "b", "Newton's 3rd law", "easy"),
    ]),
    (9, "english", 11, "My Childhood (Abdul Kalam)", [
        _q("The chapter is from the autobiography of:", ["Mahatma Gandhi", "APJ Abdul Kalam", "Nehru", "Tagore"], "b", "Wings of Fire — Kalam's autobiography", "easy"),
        _q("Kalam grew up in:", ["Hyderabad", "Rameswaram", "Madurai", "Trichy"], "b", "Rameswaram, Tamil Nadu", "medium"),
        _q("The chapter shows the values of:", ["Hatred", "Communal harmony and hard work", "Greed", "Laziness"], "b", "Hindu-Muslim friendship and effort", "easy"),
    ]),

    # ─── GRADE 10 (extra) ────────────────────────────────────────────────
    (10, "maths", 11, "Trigonometry (Introduction)", [
        _q("sin 30° = ?", ["1/2", "√3/2", "1", "0"], "a", "sin 30° = 1/2", "easy"),
        _q("cos 0° = ?", ["0", "1/2", "1", "√3/2"], "c", "cos 0° = 1", "easy"),
        _q("tan 45° = ?", ["0", "1", "√3", "Undefined"], "b", "tan 45° = 1", "medium"),
    ]),
    (10, "science", 11, "Light – Reflection and Refraction", [
        _q("A concave mirror is also called a:", ["Diverging mirror", "Converging mirror", "Plane mirror", "Cylindrical mirror"], "b", "It converges light", "medium"),
        _q("Refractive index of a medium tells us:", ["How heavy it is", "How much it bends light", "Its colour", "Its weight"], "b", "Higher n = more bending", "medium"),
        _q("A pencil in water looks bent because of:", ["Reflection", "Refraction", "Diffraction", "Magnetism"], "b", "Light bends at water/air boundary", "easy"),
    ]),
    (10, "english", 11, "From the Diary of Anne Frank", [
        _q("Anne Frank's diary was written during:", ["WWI", "World War II", "Cold War", "Indian freedom"], "b", "Hiding from Nazis, WWII", "easy"),
        _q("Anne and her family hid in a/an:", ["Ship", "Secret annexe / attic in Amsterdam", "Forest", "Cave"], "b", "Hidden room behind a bookcase", "medium"),
        _q("The diary celebrates a teenager's:", ["Hatred", "Hope, dreams, and inner life", "Wealth", "Travels"], "b", "Hope amid horror", "easy"),
    ]),
]


class Command(BaseCommand):
    help = "Add an extra batch of curriculum quizzes for Grades 1-10"

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

        added = 0
        skipped = 0

        for grade, subject_code, chap_num, chap_title, questions in QUIZZES:
            subj, _ = Subject.objects.get_or_create(name=subject_code)
            chapter, _ = Chapter.objects.get_or_create(
                subject=subj, grade=grade, chapter_number=chap_num,
                defaults={
                    "title": chap_title,
                    "description": f"Grade {grade} {chap_title}",
                },
            )

            quiz_title = f"{chap_title} - Quiz"
            quiz, created = Quiz.objects.get_or_create(
                chapter=chapter,
                title=quiz_title,
                defaults={
                    "subject": subject_code,
                    "grade": grade,
                    "description": f"Practice quiz on {chap_title}",
                    "num_questions": len(questions),
                    "duration_minutes": 10,
                    "passing_percentage": 40.0,
                    "is_published": True,
                    "created_by": teacher,
                },
            )

            placeholder_qs = quiz.questions.filter(question_text__startswith="Sample question")
            has_real = quiz.questions.exclude(question_text__startswith="Sample question").exists()

            if has_real and not placeholder_qs.exists():
                skipped += 1
                continue

            placeholder_qs.delete()
            for qd in questions:
                Question.objects.create(
                    quiz=quiz,
                    question_text=qd["text"],
                    options_json=qd["options"],
                    correct_answer=qd["correct"],
                    explanation=qd.get("explanation", ""),
                    difficulty=qd.get("difficulty", "easy"),
                    marks=1,
                )

            quiz.num_questions = len(questions)
            quiz.save(update_fields=["num_questions"])
            added += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nExtra quizzes added: {added}, skipped (already filled): {skipped}"
        ))
