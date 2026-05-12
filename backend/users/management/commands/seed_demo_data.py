"""
python manage.py seed_demo_data

Creates 6 realistic demo students with quiz history, AI-tutor chat history,
and scheme/scholarship queries — all spread naturally over the last 21 days.

Safe to run multiple times (idempotent).

Priority students for live demo:
  Ravi Kumar  (ravi / demo123)  — Study Hub, Quiz, Progress, Career Guidance
  Priya Sharma (priya / demo123) — Schemes chatbot, Resources
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from users.models import Student, Teacher
from resources.models import Subject, Chapter
from quizzes.models import Quiz, Question, StudentQuizAttempt
from ai_tutor.models import TutorSession, SessionMessage
from doubts.models import DoubtSession, DoubtMessage
from study_hub.models import StudyLesson

User = get_user_model()

# ── helpers ────────────────────────────────────────────────────────────────

def ago(days, hour=10, minute=0):
    """Return a timezone-aware datetime that is `days` days in the past."""
    return timezone.now().replace(hour=hour, minute=minute, second=0, microsecond=0) - timedelta(days=days)


def _ensure_subject(code):
    subj, _ = Subject.objects.get_or_create(name=code)
    return subj


def _ensure_chapter(subject_code, grade, number, title):
    subj = _ensure_subject(subject_code)
    ch, _ = Chapter.objects.get_or_create(
        subject=subj, grade=grade, chapter_number=number,
        defaults={"title": title, "description": f"Grade {grade} {title}"},
    )
    return ch


def _ensure_quiz(chapter, subject_code, grade, title, teacher):
    quiz, created = Quiz.objects.get_or_create(
        chapter=chapter,
        title=title,
        defaults={
            "subject": subject_code,
            "grade": grade,
            "description": f"Practice quiz on {title}",
            "num_questions": 10,
            "duration_minutes": 15,
            "passing_percentage": 40.0,
            "is_published": True,
            "created_by": teacher,
        },
    )
    if created:
        # Add 3 placeholder questions so the quiz is non-empty
        for i, (diff, ans) in enumerate([("easy", "a"), ("medium", "b"), ("hard", "c")], 1):
            Question.objects.create(
                quiz=quiz,
                question_text=f"Sample question {i} about {title}?",
                options_json=[
                    {"key": "a", "text": "Option A"},
                    {"key": "b", "text": "Option B"},
                    {"key": "c", "text": "Option C"},
                    {"key": "d", "text": "Option D"},
                ],
                correct_answer=ans,
                explanation=f"Option {ans.upper()} is correct.",
                difficulty=diff,
                marks=1,
            )
    return quiz


def _record_attempt(student, quiz, pct, submitted_at):
    """Create or update a quiz attempt — always reflects the latest seed values."""
    attempt, created = StudentQuizAttempt.objects.update_or_create(
        student=student,
        quiz=quiz,
        defaults={
            "score": round(pct / 10, 1),        # out of 10
            "total_marks": 10.0,
            "percentage": float(pct),
            "passed": pct >= 40,
            "is_submitted": True,
            "submitted_at": submitted_at,
        },
    )
    if created:
        # Override auto_now_add started_at to 20 min before submission
        StudentQuizAttempt.objects.filter(pk=attempt.pk).update(
            started_at=submitted_at - timedelta(minutes=20)
        )
    return attempt


def _add_tutor_session(student, grade, syllabus, subject, chapter, language, messages, session_date):
    """Create a TutorSession + messages if none exist for this chapter."""
    session, created = TutorSession.objects.get_or_create(
        student=student,
        subject=subject,
        chapter=chapter,
        defaults={
            "grade": grade,
            "syllabus": syllabus,
            "language": language,
            "title": chapter,
            "message_count": len(messages),
            "is_active": False,
        },
    )
    if created:
        TutorSession.objects.filter(pk=session.pk).update(created_at=session_date)
        for i, (role, content) in enumerate(messages):
            msg_time = session_date + timedelta(minutes=i * 3)
            msg = SessionMessage.objects.create(
                session=session, role=role, content=content
            )
            SessionMessage.objects.filter(pk=msg.pk).update(created_at=msg_time)


def _add_scheme_query(student, teacher_user, question, ai_answer, days_ago):
    """Store a scheme/scholarship query as a DoubtSession + two messages."""
    session, created = DoubtSession.objects.get_or_create(
        student=student,
        subject="Schemes & Scholarships",
        description=question,
        defaults={"status": "resolved"},
    )
    if created:
        DoubtSession.objects.filter(pk=session.pk).update(created_at=ago(days_ago))
        # Student question message
        q_msg = DoubtMessage.objects.create(
            session=session, sender=student.user, message=question
        )
        DoubtMessage.objects.filter(pk=q_msg.pk).update(created_at=ago(days_ago, hour=14))
        # AI / teacher answer message
        a_msg = DoubtMessage.objects.create(
            session=session, sender=teacher_user, message=ai_answer
        )
        DoubtMessage.objects.filter(pk=a_msg.pk).update(
            created_at=ago(days_ago, hour=14) + timedelta(minutes=1)
        )


def _add_study_lesson(grade, syllabus, subject, chapter, language, summary, key_points):
    StudyLesson.objects.get_or_create(
        grade=grade, syllabus=syllabus, subject=subject,
        chapter=chapter, language=language,
        defaults={"summary": summary, "key_points": key_points},
    )


# ── per-student seed functions ─────────────────────────────────────────────

def seed_ravi(teacher, teacher_user):
    """Ravi Kumar — Grade 8 CBSE, Hindi.  PRIORITY DEMO STUDENT."""
    user, created = User.objects.get_or_create(
        username="ravi",
        defaults={
            "email": "ravi@demo.ruralsiksha.in",
            "first_name": "Ravi",
            "last_name": "Kumar",
            "role": "student",
            "school_name": "Govt. Higher Secondary School, Kolar",
        },
    )
    if created:
        user.set_password("demo123")
        user.save()
    student, _ = Student.objects.get_or_create(
        user=user,
        defaults={
            "grade": 8,
            "subjects_interested": "maths,science,social_science",
            "attendance": 88.5,
            "total_sessions": 14,
            "total_quiz_attempts": 15,
        },
    )

    # ── Quiz attempts: clear upward Maths trend ──────────────────────────
    #  Maths: 50 → 62 → 74 → 83 → 90  (the impressive demo arc)
    maths_quizzes = [
        (1, "Rational Numbers",                      50, 21),
        (2, "Linear Equations in One Variable",      62, 17),
        (3, "Understanding Quadrilaterals",           74, 13),
        (4, "Data Handling",                          83,  8),
        (5, "Squares and Square Roots",               90,  3),
    ]
    for num, title, pct, days in maths_quizzes:
        ch = _ensure_chapter("maths", 8, num, title)
        quiz = _ensure_quiz(ch, "maths", 8, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=16))

    # Science: gradual improvement with one dip (looks authentic)
    science_quizzes = [
        (1, "Crop Production and Management",  58, 20),
        (2, "Microorganisms: Friend and Foe",  65, 16),
        (3, "Coal and Petroleum",              70, 12),
        (4, "Combustion and Flame",            60, 7),   # dip — authentic
        (5, "Conservation of Plants",          77,  2),
    ]
    for num, title, pct, days in science_quizzes:
        ch = _ensure_chapter("science", 8, num, title)
        quiz = _ensure_quiz(ch, "science", 8, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=15))

    # Social Science: steady climb
    ss_quizzes = [
        (1, "Resources",                55, 19),
        (2, "Land, Soil, Water",        62, 14),
        (3, "Mineral and Power",        68, 10),
        (4, "Agriculture",              72,  6),
        (5, "Industries",               75,  1),
    ]
    for num, title, pct, days in ss_quizzes:
        ch = _ensure_chapter("social_science", 8, num, title)
        quiz = _ensure_quiz(ch, "social_science", 8, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=17))

    # Hindi (Vasant Bhag 3): improving trend matching Maths arc
    hindi_quizzes = [
        (1, "Dhwani",                          70, 19),
        (2, "Lakh Ki Chudiyan",               74, 14),
        (3, "Bus Ki Yatra",                   78,  9),
        (4, "Deewanon Ki Hasti",              80,  4),
        (5, "Chitthiyon Ki Anoothi Duniya",   85,  1),
    ]
    for num, title, pct, days in hindi_quizzes:
        ch = _ensure_chapter("hindi", 8, num, title)
        quiz = _ensure_quiz(ch, "hindi", 8, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=18))

    # English (Honeydew — Grade 8 CBSE)
    eng_quizzes = [
        (1, "The Best Christmas Present in the World", 78, 18),
        (2, "The Tsunami",                             82, 12),
        (3, "Glimpses of the Past",                    80,  5),
    ]
    for num, title, pct, days in eng_quizzes:
        ch = _ensure_chapter("english", 8, num, title)
        quiz = _ensure_quiz(ch, "english", 8, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=11))

    # Kannada (third language — Karnataka CBSE schools)
    kn_quizzes = [
        (1, "Bettadakke Hogi Baa",  72, 16),
        (2, "Nanna Baalya",         76, 10),
        (3, "Akkamahadevi Vachana", 80,  3),
    ]
    for num, title, pct, days in kn_quizzes:
        ch = _ensure_chapter("kannada", 8, num, title)
        quiz = _ensure_quiz(ch, "kannada", 8, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=12))

    # ── AI Tutor sessions ─────────────────────────────────────────────────
    _add_tutor_session(
        student, 8, "CBSE", "maths", "Rational Numbers", "hi",
        [
            ("student", "Sir, rational number kya hota hai? Mujhe textbook padhne ke baad bhi samajh nahi aaya."),
            ("tutor",   "Bilkul! Rational number voh number hota hai jise p/q ke roop mein likha ja sake, jahan p aur q dono integer ho aur q zero na ho. Jaise: 1/2, -3/4, 7 (jo 7/1 hai), aur 0 (jo 0/1 hai)."),
            ("student", "Kya 0 ek rational number hai? Mujhe laga tha nahi hoga."),
            ("tutor",   "Haan! 0 ek rational number hai kyunki ise 0/1 likha ja sakta hai — numerator 0 aur denominator 1 hai, jo zero nahi hai. Isliye 0 rational number ki definition satisfy karta hai."),
            ("student", "Irrational number aur rational number mein kya fark hai? Kuch examples bhi batao."),
            ("tutor",   "Bahut acha sawaal! Rational numbers exactly represent ho sakte hain p/q mein — jaise 0.5, 1.333... (1/3), -2. Irrational numbers kabhi exactly nahi likhe ja sakte — jaise sqrt(2) = 1.41421356... jo kabhi khatam nahi hota aur kabhi repeat nahi hota. Pi (3.14159...) bhi irrational hai. Yaad rakho: sqrt(perfect square) = rational; sqrt(non-perfect square) = irrational."),
        ],
        ago(20, hour=18),
    )

    _add_tutor_session(
        student, 8, "CBSE", "science", "Force and Pressure", "hi",
        [
            ("student", "Force aur pressure mein kya difference hai? Dono ka matlab toh same lag raha hai."),
            ("tutor",   "Yeh common confusion hai! Force ek push ya pull hai — isme direction hoti hai. Pressure yeh batata hai ki force kitne area par distribute hai. Formula: Pressure = Force / Area. Isliye agar area zyada ho toh pressure kam hoga."),
            ("student", "To wide tyres kyun use karte hain heavy trucks mein? Kya yeh pressure se related hai?"),
            ("tutor",   "Bilkul sahi socha! Wide tyres ka area zyada hota hai. Isse weight zyada area mein distribute hota hai aur pressure per unit area kam ho jata hai. Isliye road nahi tuttti aur truck dhansata nahi. Snowshoes bhi isi liye wide hote hain — barff mein pressure kam karne ke liye."),
            ("student", "Sharp knife aasani se kaat deta hai lekin blunt knife nahi. Yeh bhi pressure wali baat hai?"),
            ("tutor",   "Ek dum sahi! Sharp knife ka edge bahut kam area ka hota hai. Agar tum same force lagao toh zyada pressure banta hai (P = F/A, A chhota = P bada). Blunt knife ka area zyada hai toh same force se kam pressure — isliye aasani se nahi kaatta. Yeh ek perfect real-life example hai Force and Pressure chapter ka!"),
        ],
        ago(15, hour=17),
    )

    _add_tutor_session(
        student, 8, "CBSE", "maths", "Linear Equations in One Variable", "hi",
        [
            ("student", "2x + 5 = 13 ko kaise solve kare? Step by step batao."),
            ("tutor",   "Sure! Step 1: Dono side se 5 ghataao — 2x + 5 - 5 = 13 - 5, toh 2x = 8. Step 2: Dono side ko 2 se divide karo — x = 8/2 = 4. Check: 2(4) + 5 = 8 + 5 = 13. Sahi hai!"),
            ("student", "3(x - 2) = 2x + 1 mein bracket kaise handle karte hain?"),
            ("tutor",   "Pehle bracket expand karo: 3x - 6 = 2x + 1. Phir 2x dono side se ghataao: 3x - 2x - 6 = 1, toh x - 6 = 1. Ab 6 add karo dono side: x = 7. Verify: 3(7-2) = 15 aur 2(7)+1 = 15. Correct!"),
        ],
        ago(10, hour=19),
    )

    # ── Scheme queries ────────────────────────────────────────────────────
    _add_scheme_query(
        student, teacher_user,
        question=(
            "Mera family OBC category mein aata hai. Hamare ghar ki saalik amdani lagbhag 2.5 lakh rupaye hai. "
            "Main abhi 8th class mein hun aur government school mein padh raha hun. "
            "Kya mujhe koi government scholarship mil sakti hai?"
        ),
        ai_answer=(
            "Bilkul! Aapke liye kuch aham scholarships available hain:\n\n"
            "1. PRE-MATRIC SCHOLARSHIP (OBC) — National Scholarship Portal\n"
            "   • Eligibility: OBC student, Class 1-10, family income < 2.5 lakh/year\n"
            "   • Amount: Rs. 825/year (day scholar) + books allowance\n"
            "   • Apply at: scholarships.gov.in\n"
            "   • Documents: Income certificate, Aadhaar, school certificate\n\n"
            "2. PM YASASVI SCHOLARSHIP (Class 9 ke baad)\n"
            "   • Abhi Class 8 mein ho — class 9 mein jaate hi apply karo\n"
            "   • NTA YASASVI Entrance Test (YET) paas karna hoga\n"
            "   • Amount: Rs. 75,000/year (Class 9-10)\n"
            "   • Topics: MAT + Maths + Science + Social Studies\n\n"
            "3. NMMS SCHOLARSHIP — abhi apply karo!\n"
            "   • Specifically Class 8 government school students ke liye\n"
            "   • Amount: Rs. 12,000/year (Rs. 1,000/month)\n"
            "   • Exam: MAT (90 min) + SAT (90 min), November mein hogi\n"
            "   • Income limit: 1.5 lakh/year (check your state's limit)\n\n"
            "Meri salah: PEHLE NSP par OBC Pre-Matric scholarship ke liye apply karo "
            "(deadline aata hai September-October). Saath mein NMMS ki taiyaari shuru karo!"
        ),
        days_ago=18,
    )

    _add_scheme_query(
        student, teacher_user,
        question=(
            "NMMS scholarship ke baare mein detail mein batao. "
            "Exam pattern kya hai aur kaise taiyaari karein?"
        ),
        ai_answer=(
            "NMMS (National Means-cum-Merit Scholarship) — Complete Guide:\n\n"
            "AMOUNT: Rs. 12,000/year (Rs. 1,000/month), Class 9 se 12 tak\n\n"
            "ELIGIBILITY:\n"
            "• Class 8 mein government school student\n"
            "• Class 7 mein minimum 55% marks (SC/ST ke liye 50%)\n"
            "• Family income < Rs. 3.5 lakh/year\n\n"
            "EXAM PATTERN:\n"
            "Part 1 — MAT (Mental Ability Test): 90 questions, 90 minutes\n"
            "  • Analogy, classification, numerical series, pattern perception\n"
            "  • Tarkik sochne ki shakti test ki jaati hai\n\n"
            "Part 2 — SAT (Scholastic Aptitude Test): 90 questions, 90 minutes\n"
            "  • Science: 35 questions (Class 7-8 NCERT)\n"
            "  • Social Studies: 35 questions\n"
            "  • Maths: 20 questions\n\n"
            "TAIYAARI TIPS:\n"
            "• MAT ke liye rooz 10 reasoning puzzles solve karo\n"
            "• SAT ke liye Class 7 aur 8 ki NCERT books padho\n"
            "• Previous year papers solve karo (SCERT ki website par available)\n"
            "• Minimum qualifying marks: 40% each section (SC/ST: 32%)\n\n"
            "APPLY KAISE KAREIN:\n"
            "• Application form school ke through milega\n"
            "• Deadline: July-August (state ke hisaab se)\n"
            "• Admit card download: SCERT ya state education portal\n\n"
            "1 lakh scholarships nationally diye jaate hain — competition hai "
            "lekin consistent preparation se definitely qualify kar sakte ho!"
        ),
        days_ago=11,
    )

    # ── Study Hub lessons ─────────────────────────────────────────────────
    _add_study_lesson(
        8, "CBSE", "maths", "Rational Numbers", "hi",
        summary=(
            "## Rational Numbers — Class 8 CBSE\n\n"
            "Rational numbers voh numbers hain jo p/q form mein represent ho sakte hain "
            "jahan p, q integers hain aur q ≠ 0.\n\n"
            "### Kuch Khaas Baatein\n"
            "- **Positive rational numbers:** jab p aur q dono same sign ke hote hain\n"
            "- **Negative rational numbers:** jab p aur q alag sign ke hote hain\n"
            "- **Properties:** addition, subtraction, multiplication, division — sabhi operations "
            "rational numbers par kiye ja sakte hain (sivaay zero se divide karne ke)\n\n"
            "### Number Line par Representation\n"
            "Har rational number ko number line par point ke roop mein dikhaya ja sakta hai. "
            "Do rational numbers ke beech mein hamesha infinite rational numbers hote hain — "
            "ise density property kehte hain."
        ),
        key_points=[
            "Rational number = p/q jahan p, q integers aur q ≠ 0",
            "0 ek rational number hai (0 = 0/1)",
            "Sabhi integers rational numbers hain",
            "Two rational numbers ke beech infinite rational numbers hote hain",
            "Rational + Rational = Rational (closed under addition)",
        ],
    )

    _add_study_lesson(
        8, "CBSE", "science", "Force and Pressure", "hi",
        summary=(
            "## Force and Pressure — Class 8 Science\n\n"
            "**Force** ek push ya pull hai jo kisi object par lagaya jaata hai. "
            "Force ek vector quantity hai — isme magnitude aur direction dono hoti hai.\n\n"
            "**Pressure** = Force / Area\n\n"
            "### Real-Life Applications\n"
            "| Example | Concept |\n|---|---|\n"
            "| Sharp knife | Kam area → zyada pressure |\n"
            "| Wide truck tyres | Zyada area → kam pressure |\n"
            "| Snowshoes | Area badhao, barff mein dhanso mat |\n"
            "| Dams wide base | Gehra paani zyada pressure deta hai |\n\n"
            "### Atmospheric Pressure\n"
            "Humare upar ki hava ka weight earth ki surface par pressure dalta hai. "
            "Sea level par: 1 atm = 101,325 Pa (Pascal)."
        ),
        key_points=[
            "Force = push ya pull; unit = Newton (N)",
            "Pressure = Force ÷ Area; unit = Pascal (Pa)",
            "Area badhaane se pressure kam hota hai",
            "Area ghataane se pressure badh jaata hai",
            "Liquids aur gases bhi pressure dete hain",
        ],
    )

    return student


def seed_priya(teacher, teacher_user):
    """Priya Sharma — Grade 6 CBSE, English.  PRIORITY DEMO STUDENT."""
    user, created = User.objects.get_or_create(
        username="priya",
        defaults={
            "email": "priya@demo.ruralsiksha.in",
            "first_name": "Priya",
            "last_name": "Sharma",
            "role": "student",
            "school_name": "Kendriya Vidyalaya, Dharwad",
        },
    )
    if created:
        user.set_password("demo123")
        user.save()
    student, _ = Student.objects.get_or_create(
        user=user,
        defaults={
            "grade": 6,
            "subjects_interested": "maths,science,english",
            "attendance": 92.0,
            "total_sessions": 10,
            "total_quiz_attempts": 15,
        },
    )

    # ── Quiz attempts (HIGH performer — good grades demo) ─────────────────
    maths_quizzes = [
        (1, "Knowing Our Numbers",       82, 21),
        (2, "Whole Numbers",             80, 17),
        (3, "Playing with Numbers",      86, 13),
        (4, "Basic Geometrical Ideas",   82, 8),
        (5, "Understanding Elem. Shapes",92, 3),
    ]
    for num, title, pct, days in maths_quizzes:
        ch = _ensure_chapter("maths", 6, num, title)
        quiz = _ensure_quiz(ch, "maths", 6, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=15))

    science_quizzes = [
        (1, "Food: Where Does It Come From?", 80, 20),
        (2, "Components of Food",              82, 15),
        (3, "Fibre to Fabric",                 85, 11),
        (4, "Sorting Materials",               88, 6),
        (5, "Separation of Substances",         90,  1),
    ]
    for num, title, pct, days in science_quizzes:
        ch = _ensure_chapter("science", 6, num, title)
        quiz = _ensure_quiz(ch, "science", 6, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=14))

    english_quizzes = [
        (1, "Who Did Patrick's Homework?",      78, 19),
        (2, "How the Dog Found Himself a Master",82, 14),
        (3, "Taro's Reward",                    86, 10),
        (4, "An Indian-American Woman in Space", 88,  5),
        (5, "A Different Kind of School",        90,  2),
    ]
    for num, title, pct, days in english_quizzes:
        ch = _ensure_chapter("english", 6, num, title)
        quiz = _ensure_quiz(ch, "english", 6, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=16))

    # Kannada (Grade 6 — high performer)
    kn_quizzes = [
        (1, "Shishuvina Haadu",        82, 18),
        (2, "Namma Uttara Karnataka",  86, 11),
        (3, "Nanna Priya Kavi",        88,  4),
    ]
    for num, title, pct, days in kn_quizzes:
        ch = _ensure_chapter("kannada", 6, num, title)
        quiz = _ensure_quiz(ch, "kannada", 6, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=12))

    # ── AI Tutor sessions ─────────────────────────────────────────────────
    _add_tutor_session(
        student, 6, "CBSE", "maths", "Integers", "en",
        [
            ("student", "What exactly are integers? My teacher mentioned negative numbers and I got confused."),
            ("tutor",   "Great question! Integers are the set of whole numbers AND their negatives, including zero: ...-3, -2, -1, 0, 1, 2, 3... They do NOT include fractions or decimals. Think of a thermometer — temperatures can be positive (hot) or negative (cold) — those are all integers!"),
            ("student", "How do I add -5 + 3? I always get confused with negative numbers."),
            ("tutor",   "Use the number line trick! Start at -5. Now move 3 steps to the RIGHT (because we're adding positive 3). You land on -2. So -5 + 3 = -2. Another way: |5| - |3| = 2. Since 5 is bigger and negative, the answer is -2."),
            ("student", "What about multiplying? Like (-3) × (-4)?"),
            ("tutor",   "Here's the rule: Negative × Negative = POSITIVE. So (-3) × (-4) = +12. Think of it this way: 'the enemy of my enemy is my friend.' Two negatives cancel each other. But Negative × Positive = Negative: (-3) × 4 = -12."),
            ("student", "When do we use negative numbers in real life?"),
            ("tutor",   "Everywhere! Temperature below 0°C, floors below ground (B1, B2 in a lift), bank balance when you owe money (debt), sea depth below surface, and even golf scores! When you see '-2' in golf it means 2 below par. You're already using integers daily without realising it!"),
        ],
        ago(19, hour=17),
    )

    _add_tutor_session(
        student, 6, "CBSE", "science", "Components of Food", "en",
        [
            ("student", "Can you explain the main nutrients in food? There are so many, I can't remember them all."),
            ("tutor",   "Use this memory trick: 'CPFVMW' — Carbohydrates, Proteins, Fats, Vitamins, Minerals, Water. Each has a different job: Carbs = energy (rice, bread), Proteins = body building (dal, eggs), Fats = energy storage + warmth (oil, butter), Vitamins = disease protection, Minerals = strong bones/teeth, Water = all body processes."),
            ("student", "Why does my mother say eat less sugar but sugar gives energy?"),
            ("tutor",   "Smart question! Yes, sugar (a carbohydrate) gives instant energy. But TOO MUCH sugar that the body doesn't use immediately gets stored as fat. Also, excess sugar causes tooth decay and increases risk of diabetes. So sugar is NOT bad — too much sugar is bad. Jaggery (gud) is a healthier alternative as it also has minerals!"),
            ("student", "What disease comes from not eating enough Vitamin C?"),
            ("tutor",   "Vitamin C deficiency causes SCURVY — symptoms include bleeding gums, loose teeth, and weakness. Historically, sailors on long voyages got scurvy because they had no fresh fruits. The solution? Eat citrus fruits like oranges, amla (Indian gooseberry — richest source of Vitamin C!), and lemons. Just one amla has more Vitamin C than an orange."),
        ],
        ago(13, hour=16),
    )

    # ── Scheme queries ────────────────────────────────────────────────────
    _add_scheme_query(
        student, teacher_user,
        question=(
            "I am studying in Grade 6 in a government school. My father is a daily wage worker "
            "and our family income is about Rs. 80,000 per year. Are there any government "
            "scholarships I can apply for? I am a girl student."
        ),
        ai_answer=(
            "You have excellent options! Being a girl student from a low-income family makes you "
            "eligible for multiple scholarships:\n\n"
            "1. PRE-MATRIC SCHOLARSHIP (NSP — National Scholarship Portal)\n"
            "   • For: Classes 1-10, family income < Rs. 1 lakh/year ✓\n"
            "   • Amount: Rs. 600/year (Classes 1-5) or Rs. 1,100/year (Classes 6-10)\n"
            "   • Extra: Rs. 500/year for books and stationery\n"
            "   • Apply: scholarships.gov.in → New Registration → Pre-Matric\n"
            "   • Deadline: Usually September-October each year\n\n"
            "2. STATE GOVERNMENT GIRLS SCHOLARSHIP\n"
            "   • Many states offer additional scholarships for girl students\n"
            "   • Ask your school for state-specific schemes\n"
            "   • Karnataka: Bhagyalakshmi scheme, Kuvempu scholarship\n\n"
            "3. INSPIRE SCHOLARSHIP (for later — Class 11 onwards)\n"
            "   • For science students who score top marks in Class 10\n"
            "   • Keep this in mind as a future goal!\n\n"
            "DOCUMENTS YOU'LL NEED:\n"
            "• Income certificate from Tahsildar/Revenue officer\n"
            "• Aadhaar card (yours + parent's)\n"
            "• Bank account in your name (Aadhaar-linked)\n"
            "• School enrollment certificate\n"
            "• Previous year's marksheet\n\n"
            "My advice: Apply for NSP Pre-Matric scholarship FIRST — it's the easiest and "
            "fastest. Ask your school headmaster for help with the application. You deserve this!"
        ),
        days_ago=17,
    )

    _add_scheme_query(
        student, teacher_user,
        question=(
            "My teacher told me about a CBSE scholarship for single girl child. "
            "What are the details? How much money is given and what are the conditions?"
        ),
        ai_answer=(
            "Your teacher is referring to the CBSE Merit Scholarship Scheme for Single Girl Child (SGC)!\n\n"
            "WHAT IS IT?\n"
            "A scholarship for girl students who are the only child of their parents — "
            "designed to encourage education of the single girl child.\n\n"
            "AMOUNT: Rs. 500 per month during Classes 11 and 12\n"
            "• Paid directly to your bank account by CBSE\n"
            "• Can continue into college if you maintain marks\n\n"
            "ELIGIBILITY:\n"
            "✓ Must be a Single Girl Child (no siblings)\n"
            "✓ Passed CBSE Class 10 with at least 60% marks\n"
            "✓ Enrolled in Class 11 in a CBSE-affiliated school\n"
            "✓ Parents' income — no upper limit for this one!\n\n"
            "HOW TO APPLY (when you reach Class 11):\n"
            "1. Visit cbse.gov.in → Scholarships section\n"
            "2. Application opens after Class 10 board results\n"
            "3. Need: Class 10 marksheet, birth certificate (proving you are the only child), "
            "school certificate, bank details\n\n"
            "SINCE YOU'RE IN CLASS 6 NOW:\n"
            "• Study hard and aim for 60%+ in Class 10 boards\n"
            "• Keep your Single Girl Child status certificate ready\n"
            "• This scholarship is 4 years away — but definitely worth planning for!\n\n"
            "Also check: National Merit Scholarship and State board merit scholarships "
            "which may have less strict eligibility."
        ),
        days_ago=10,
    )

    _add_scheme_query(
        student, teacher_user,
        question=(
            "Is there any scholarship that pays for science books and lab equipment? "
            "I really like science but my parents cannot afford extra books."
        ),
        ai_answer=(
            "Yes! A few schemes specifically help with study materials:\n\n"
            "1. NSP PRE-MATRIC SCHOLARSHIP includes a books/stationery allowance\n"
            "   • Rs. 500/year extra for books — apply at scholarships.gov.in\n\n"
            "2. VIDYASIRI SCHOLARSHIP (Karnataka)\n"
            "   • For government school students in Karnataka\n"
            "   • Covers books and study material costs\n"
            "   • Apply through your school or at ssp.postmatric.karnataka.gov.in\n\n"
            "3. FREE NCERT TEXTBOOKS\n"
            "   • All NCERT books are FREE to download as PDFs from ncert.nic.in\n"
            "   • Ask your school — government schools distribute NCERT books free\n\n"
            "4. PM eVIDYA PROGRAMME\n"
            "   • Free digital learning content for all students\n"
            "   • Access at diksha.gov.in — hundreds of free science resources\n"
            "   • Works offline too after downloading!\n\n"
            "5. DIGITAL INDIA INITIATIVE — FREE TABLETS\n"
            "   • Some states give free tablets to meritorious government school students\n"
            "   • Ask your school principal if your school is enrolled\n\n"
            "For your love of science — also explore KVPY (Kishore Vaigyanik Protsahan "
            "Yojana) when you reach Class 11. It's a prestigious scholarship for science students!"
        ),
        days_ago=4,
    )

    # ── Study Hub lessons ─────────────────────────────────────────────────
    _add_study_lesson(
        6, "CBSE", "maths", "Integers", "en",
        summary=(
            "## Integers — Class 6 Mathematics\n\n"
            "Integers are the complete set of whole numbers including negatives: "
            "...-3, -2, -1, 0, 1, 2, 3...\n\n"
            "### On the Number Line\n"
            "Numbers to the **right** of 0 are positive. Numbers to the **left** of 0 "
            "are negative. Zero is neither positive nor negative.\n\n"
            "### Operations with Integers\n"
            "| Operation | Rule | Example |\n|---|---|---|\n"
            "| (+) + (+) | Add, keep + | 3 + 4 = 7 |\n"
            "| (-) + (-) | Add, keep - | -3 + (-4) = -7 |\n"
            "| (+) + (-) | Subtract, keep sign of bigger | 7 + (-3) = 4 |\n"
            "| (-) × (-) | Positive | (-3)×(-4) = 12 |\n"
            "| (+) × (-) | Negative | 3×(-4) = -12 |\n\n"
            "### Real-Life Uses\n"
            "Temperature, altitude, bank balance, floors in a building, golf scores."
        ),
        key_points=[
            "Integers include all whole numbers and their negatives",
            "Zero is an integer but neither positive nor negative",
            "Number line: right = positive, left = negative",
            "Two negatives multiplied give a positive",
            "Integers are closed under addition, subtraction and multiplication",
        ],
    )

    _add_study_lesson(
        6, "CBSE", "science", "Components of Food", "en",
        summary=(
            "## Components of Food — Class 6 Science\n\n"
            "Food contains nutrients that our body needs for energy, growth and protection.\n\n"
            "### The 6 Main Nutrients\n"
            "1. **Carbohydrates** — main energy source (rice, wheat, potato, sugar)\n"
            "2. **Proteins** — body building and repair (dal, eggs, milk, soya)\n"
            "3. **Fats** — energy storage and organ protection (oil, ghee, nuts)\n"
            "4. **Vitamins** — protect from diseases (fruits, vegetables)\n"
            "5. **Minerals** — strong bones, nerves (calcium, iron, iodine)\n"
            "6. **Water** — transport of nutrients, temperature control\n\n"
            "### Deficiency Diseases\n"
            "| Deficiency | Disease |\n|---|---|\n"
            "| Vitamin C | Scurvy (bleeding gums) |\n"
            "| Vitamin D | Rickets (soft bones) |\n"
            "| Iron | Anaemia |\n"
            "| Iodine | Goitre |\n"
            "| Protein | Kwashiorkor, Marasmus |"
        ),
        key_points=[
            "Carbohydrates, proteins, fats = macronutrients (needed in large amounts)",
            "Vitamins, minerals = micronutrients (needed in small amounts)",
            "Balanced diet contains all 6 nutrients in right proportions",
            "Roughage/fibre helps in digestion but has no nutritional value",
            "Deficiency of nutrients leads to specific diseases",
        ],
    )

    return student


def seed_ananya(teacher):
    """Ananya Das — Grade 10, Karnataka State Board, Kannada."""
    user, created = User.objects.get_or_create(
        username="ananya",
        defaults={
            "email": "ananya@demo.ruralsiksha.in",
            "first_name": "Ananya",
            "last_name": "Das",
            "role": "student",
            "school_name": "Govt. PU College, Mysuru",
        },
    )
    if created:
        user.set_password("demo123")
        user.save()
    student, _ = Student.objects.get_or_create(
        user=user,
        defaults={
            "grade": 10,
            "subjects_interested": "maths,science,kannada",
            "attendance": 85.0,
            "total_sessions": 8,
            "total_quiz_attempts": 12,
        },
    )

    maths_quizzes = [
        (1, "Real Numbers",                      65, 20),
        (2, "Polynomials",                        70, 15),
        (3, "Pair of Linear Equations",           62, 11),
        (4, "Quadratic Equations",                58, 7),
        (5, "Arithmetic Progressions",            72, 2),
    ]
    for num, title, pct, days in maths_quizzes:
        ch = _ensure_chapter("maths", 10, num, title)
        quiz = _ensure_quiz(ch, "maths", 10, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=16))

    science_quizzes = [
        (1, "Chemical Reactions and Equations",  70, 18),
        (2, "Acids, Bases and Salts",             68, 13),
        (3, "Metals and Non-metals",              74, 9),
        (4, "Carbon and its Compounds",           72, 5),
        (5, "Life Processes",                     78, 1),
    ]
    for num, title, pct, days in science_quizzes:
        ch = _ensure_chapter("science", 10, num, title)
        quiz = _ensure_quiz(ch, "science", 10, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=15))

    kannada_quizzes = [
        (1, "Jnanapeeta Puraskrutha Lekhakaru", 65, 17),
        (2, "Karnataka Ekikarana",               68, 12),
        (3, "Dheera Naari Abbakka Rani",         72,  8),
        (4, "Kavirajamarga",                     70,  4),
        (5, "Manushyatvada Gaana",               75,  1),
    ]
    for num, title, pct, days in kannada_quizzes:
        ch = _ensure_chapter("kannada", 10, num, title)
        quiz = _ensure_quiz(ch, "kannada", 10, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=17))

    # English (First Flight — Grade 10 NCERT)
    eng_quizzes = [
        (1, "A Letter to God",                      68, 16),
        (2, "Nelson Mandela: Long Walk to Freedom",  72, 10),
        (3, "Two Stories about Flying",              70,  4),
    ]
    for num, title, pct, days in eng_quizzes:
        ch = _ensure_chapter("english", 10, num, title)
        quiz = _ensure_quiz(ch, "english", 10, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=11))

    _add_tutor_session(
        student, 10, "KARNATAKA", "maths", "Quadratic Equations", "kn",
        [
            ("student", "Quadratic equation endre enu? ax² + bx + c = 0 formula eshtu important?"),
            ("tutor",   "Quadratic equation aade idhu: ax² + bx + c = 0, yalli a ≠ 0. Idu ond standard form. Illi 'a' coefficient of x², 'b' coefficient of x, 'c' constant. Ullekha: 2x² - 5x + 3 = 0 alli a=2, b=-5, c=3."),
            ("student", "Roots hesage find maadbahudu? Factorisation maadoke aagilla andre?"),
            ("tutor",   "Factorisation aagilla andre Quadratic Formula use maadi! x = [-b ± √(b²-4ac)] / 2a. Illi b²-4ac ge 'discriminant' (D) antha kareeyuttare. D>0 aadarey 2 real roots, D=0 aadarey 1 root (equal), D<0 aadarey no real roots."),
            ("student", "x² - 5x + 6 = 0 solve maadi step by step."),
            ("tutor",   "Factorisation method: a=1, b=-5, c=6. -5 = (-2) + (-3) aaguttey, aur (-2)×(-3) = 6 aaguttey. So: (x-2)(x-3) = 0. Therefore x=2 or x=3. Check: 4-10+6=0 ✓ aur 9-15+6=0 ✓. Render roots aaythu!"),
        ],
        ago(14, hour=18),
    )

    _add_tutor_session(
        student, 10, "KARNATAKA", "science", "Chemical Reactions and Equations", "kn",
        [
            ("student", "Chemical equation balanc maaduvudu eshtu kashta? Steps helbekaa?"),
            ("tutor",   "3 steps ide: 1) Unbalanced equation bareyri. 2) Pratiyobba element atoms count maadi both sides. 3) Coefficients adjust maadi (subscripts change maadabeedi). Ullekha: H₂ + O₂ → H₂O — Here O atoms unbalanced (2 vs 1). Solution: 2H₂ + O₂ → 2H₂O."),
            ("student", "Combination reaction aur decomposition reaction naduva difference enu?"),
            ("tutor",   "Combination: Eradu substance seri ondaaguttave. A + B → AB. Ullekha: CaO + H₂O → Ca(OH)₂. Decomposition: Ond substance bereve aaguttade. AB → A + B. Ullekha: 2AgBr → 2Ag + Br₂ (sunlight inda). Photography alli idu use aaguttey!"),
        ],
        ago(9, hour=17),
    )

    return student


def seed_suresh(teacher):
    """Suresh Naik — Grade 5, CBSE, English."""
    user, created = User.objects.get_or_create(
        username="suresh",
        defaults={
            "email": "suresh@demo.ruralsiksha.in",
            "first_name": "Suresh",
            "last_name": "Naik",
            "role": "student",
            "school_name": "Govt. Primary School, Raichur",
        },
    )
    if created:
        user.set_password("demo123")
        user.save()
    student, _ = Student.objects.get_or_create(
        user=user,
        defaults={
            "grade": 5,
            "subjects_interested": "maths,science",
            "attendance": 79.0,
            "total_sessions": 5,
            "total_quiz_attempts": 12,
        },
    )

    # ── Quiz attempts (LOW performer — struggling student demo) ───────────
    maths_quizzes = [
        (1, "The Fish Tale",                      35, 21),
        (2, "Shapes and Angles",                  38, 16),
        (3, "How Many Squares?",                  42, 12),
        (4, "Parts and Wholes",                   40, 7),
        (5, "Be My Multiple, I'll be Your Factor",48, 2),
    ]
    for num, title, pct, days in maths_quizzes:
        ch = _ensure_chapter("maths", 5, num, title)
        quiz = _ensure_quiz(ch, "maths", 5, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=15))

    science_quizzes = [
        (1, "Super Senses",             40, 20),
        (2, "A Snake Charmer's Story",  38, 14),
        (3, "From Tasting to Digesting",44, 9),
        (4, "Mangoes Round the Year",   42, 4),
        (5, "Seeds and Seeds",          50, 1),
    ]
    for num, title, pct, days in science_quizzes:
        ch = _ensure_chapter("science", 5, num, title)
        quiz = _ensure_quiz(ch, "science", 5, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=14))

    english_quizzes = [
        (1, "Ice-Cream Man",    35, 18),
        (2, "Wonderful Waste!", 42, 10),
    ]
    for num, title, pct, days in english_quizzes:
        ch = _ensure_chapter("english", 5, num, title)
        quiz = _ensure_quiz(ch, "english", 5, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=16))

    # Kannada (Grade 5 — low scores, struggling student)
    kn_quizzes = [
        (1, "Nanna Shaale",  35, 17),
        (2, "Aase Magu",     38, 9),
        (3, "Kaalige",       42, 3),
    ]
    for num, title, pct, days in kn_quizzes:
        ch = _ensure_chapter("kannada", 5, num, title)
        quiz = _ensure_quiz(ch, "kannada", 5, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=12))

    _add_tutor_session(
        student, 5, "CBSE", "maths", "Parts and Wholes", "en",
        [
            ("student", "What is a fraction? I don't understand halves and quarters."),
            ("tutor",   "A fraction shows a part of a whole thing! Think of a pizza cut into 4 equal pieces. If you eat 1 piece, you ate 1/4 (one quarter) of the pizza. The bottom number (4) tells how many equal parts total, the top number (1) tells how many parts you have."),
            ("student", "What's bigger, 1/2 or 1/4?"),
            ("tutor",   "1/2 is bigger! Imagine the same pizza: half the pizza (1/2) is 2 big pieces, but one quarter (1/4) is just 1 small piece. When the top number is the same (both are 1), the SMALLER the bottom number, the BIGGER the fraction. It seems backwards but think of sharing: fewer people sharing = bigger piece each!"),
        ],
        ago(11, hour=16),
    )

    _add_tutor_session(
        student, 5, "CBSE", "science", "Super Senses", "en",
        [
            ("student", "How can dogs smell things so much better than us?"),
            ("tutor",   "Dogs have about 300 million smell receptors in their nose — humans have only 6 million! That's 50 times more. Dogs also have a special organ called the Jacobson's organ that detects chemicals we can't even smell. That's why police use dogs to find people and drugs!"),
            ("student", "Can any animal hear sounds we cannot?"),
            ("tutor",   "Yes! Bats can hear ultrasound — sounds too high-pitched for humans. They use this for echolocation: they make sounds and listen for the echo to find objects in the dark. Dolphins do this in water too. Elephants hear infrasound — sounds too low for us — and can communicate over many kilometres!"),
        ],
        ago(8, hour=15),
    )

    _add_scheme_query(
        student, teacher_user=User.objects.filter(role="teacher").first(),
        question="Are there any scholarships for Grade 5 students in government schools?",
        ai_answer=(
            "Yes! Here are scholarships available for primary school students:\n\n"
            "1. NSP PRE-MATRIC SCHOLARSHIP\n"
            "   • For Classes 1-10 in government schools\n"
            "   • Family income < Rs. 1 lakh/year\n"
            "   • Amount: Rs. 600/year + Rs. 500 for books\n"
            "   • Apply: scholarships.gov.in\n\n"
            "2. STATE GOVERNMENT SCHEMES\n"
            "   • Most states have mid-day meal + free textbook schemes\n"
            "   • Ask your school about free uniforms and books\n\n"
            "3. FUTURE: NMMS SCHOLARSHIP\n"
            "   • When you reach Class 8, you can appear for NMMS exam\n"
            "   • Rs. 12,000/year scholarship\n"
            "   • Start preparing now — study Maths and Science well!\n\n"
            "Keep studying hard — you're building the foundation for bigger scholarships later!"
        ),
        days_ago=14,
    )

    return student


def seed_meena(teacher, teacher_user):
    """Meena Patel — Grade 9, Maharashtra State Board, Marathi."""
    user, created = User.objects.get_or_create(
        username="meena",
        defaults={
            "email": "meena@demo.ruralsiksha.in",
            "first_name": "Meena",
            "last_name": "Patel",
            "role": "student",
            "school_name": "Zilla Parishad School, Nashik",
        },
    )
    if created:
        user.set_password("demo123")
        user.save()
    student, _ = Student.objects.get_or_create(
        user=user,
        defaults={
            "grade": 9,
            "subjects_interested": "maths,science,social_science",
            "attendance": 83.0,
            "total_sessions": 7,
            "total_quiz_attempts": 12,
        },
    )

    maths_quizzes = [
        (1,  "Number Systems",                  72, 21),
        (2,  "Polynomials",                      68, 16),
        (3,  "Coordinate Geometry",              75, 12),
        (4,  "Linear Equations in Two Variables",70, 7),
        (5,  "Introduction to Euclid's Geometry",65, 2),
    ]
    for num, title, pct, days in maths_quizzes:
        ch = _ensure_chapter("maths", 9, num, title)
        quiz = _ensure_quiz(ch, "maths", 9, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=16))

    science_quizzes = [
        (1, "Matter in Our Surroundings",    68, 19),
        (2, "Is Matter Around Us Pure?",      65, 14),
        (3, "Atoms and Molecules",            72, 10),
        (4, "Structure of the Atom",          68, 6),
        (5, "The Fundamental Unit of Life",   75, 1),
    ]
    for num, title, pct, days in science_quizzes:
        ch = _ensure_chapter("science", 9, num, title)
        quiz = _ensure_quiz(ch, "science", 9, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=15))

    ss_quizzes = [
        (1, "The French Revolution",      60, 17),
        (2, "Socialism in Europe",         55, 5),
    ]
    for num, title, pct, days in ss_quizzes:
        ch = _ensure_chapter("social_science", 9, num, title)
        quiz = _ensure_quiz(ch, "social_science", 9, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=17))

    # Marathi language quizzes (Maharashtra state board)
    marathi_quizzes = [
        (1, "Aai",                       65, 20),
        (2, "Nagari Manus Gawat Yeto",   68, 14),
        (3, "Marathi Bana",              70,  8),
        (4, "Swapna Banatat",            65,  3),
    ]
    for num, title, pct, days in marathi_quizzes:
        ch = _ensure_chapter("marathi", 9, num, title)
        quiz = _ensure_quiz(ch, "marathi", 9, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=18))

    # English (Beehive — Grade 9 NCERT)
    eng_quizzes = [
        (1, "The Fun They Had",          68, 19),
        (2, "The Sound of Music",         70, 13),
        (3, "The Little Girl",            65,  7),
        (4, "A Truly Beautiful Mind",     72,  2),
    ]
    for num, title, pct, days in eng_quizzes:
        ch = _ensure_chapter("english", 9, num, title)
        quiz = _ensure_quiz(ch, "english", 9, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=11))

    _add_tutor_session(
        student, 9, "MAHARASHTRA", "maths", "Number Systems", "mr",
        [
            ("student", "Irrational numbers kaay aahet? Te rational kadun vegale kase?"),
            ("tutor",   "Irrational numbers te aahet je p/q swarupat likha yet nahi, jyat p ani q integers aahet. Unchi: sqrt(2) = 1.41421356... he kabhi end hot nahi aani kabhi repeat hot nahi. pi = 3.14159... paN irrational ahe. Rational madhye pattern asto — jase 1/3 = 0.333... (repeat hote). Irrational madhye pattern nasato."),
            ("student", "Real numbers madhe kaay kaay yetat?"),
            ("tutor",   "Real numbers = Rational + Irrational. Mhanje: natural numbers (1,2,3...) + whole numbers (0,1,2...) + integers (...-2,-1,0,1,2...) + rational numbers (p/q) + irrational numbers (sqrt, pi) — he sagale milun Real Numbers banatat. Number line varil prateyek bindu ek real number ahe!"),
        ],
        ago(17, hour=18),
    )

    _add_tutor_session(
        student, 9, "MAHARASHTRA", "science", "Atoms and Molecules", "mr",
        [
            ("student", "Atom ani molecule madhye kay fark ahe?"),
            ("tutor",   "Atom he padarthache sabase lahan roop ahe je chemical reaction madhye divided hot nahi. Molecule mhanje 2 kiva jast atoms ek milun banatat. Udaharana: O (oxygen atom) vs O₂ (oxygen molecule, 2 atoms). H₂O (pani) ek molecule ahe jyat 2 Hydrogen atoms ani 1 Oxygen atom aahe."),
            ("student", "Atomic mass ani molecular mass kase calculate karayche?"),
            ("tutor",   "Atomic mass = periodic table madhe dilelay number (grams/mol madhe). Molecular mass = molecule madhye saglya atoms che atomic masses chi bherej. H₂O sathi: H=1, O=16, molecule mass = 2(1)+16 = 18 g/mol. CO₂ sathi: C=12, O=16, molecule mass = 12+2(16) = 44 g/mol."),
        ],
        ago(9, hour=17),
    )

    _add_scheme_query(
        student, teacher_user,
        question=(
            "Mala Maharashtra state madhye Marathi medium school madhe shikanarya "
            "mulisathi scholarship haviyo ahe. Amchi arthik sthiti chaangali nahi. "
            "Kay options aahet?"
        ),
        ai_answer=(
            "Maharashtra madhye mulisathi phukhya scholarships aahet:\n\n"
            "1. MAHARASHTRA PRE-MATRIC SCHOLARSHIP\n"
            "   • Class 1-10 sarkaari shaletil vidyarthy\n"
            "   • Family income < 2 lakh/year\n"
            "   • Abhang: Rs. 800 - 1,200/year\n"
            "   • Apply: mahadbt.maharashtra.gov.in\n\n"
            "2. RAJARSHI CHHATRAPATI SHAHU MAHARAJ SCHOLARSHIP\n"
            "   • OBC category mulisathi\n"
            "   • 8th nantar available\n"
            "   • mahadbt.maharashtra.gov.in var apply kara\n\n"
            "3. SAVITRIBAI PHULE SCHOLARSHIP (mulisathi vishesh)\n"
            "   • Maharashtra sarkaari mulisathi 100% fees maafi\n"
            "   • SC/ST/OBC/NT categories\n\n"
            "4. CENTRAL GOVERNMENT NSP\n"
            "   • scholarships.gov.in var apply kara\n"
            "   • Pre-Matric scholarship available\n\n"
            "Important: MahaDBT portal (mahadbt.maharashtra.gov.in) var EK JAAGI "
            "Maharashtra che sagle scholarships miltat. Register kara ani check kara!"
        ),
        days_ago=13,
    )

    _add_scheme_query(
        student, teacher_user,
        question="What is the EBC scholarship for students who are not SC/ST but still poor?",
        ai_answer=(
            "Great question! EBC stands for Economically Backward Class. Here's what's available:\n\n"
            "1. PRE-MATRIC SCHOLARSHIP FOR EBC STUDENTS (Central Government)\n"
            "   • For students NOT belonging to SC/ST/OBC but with family income < Rs. 1 lakh\n"
            "   • Amount: Rs. 600-1,100/year depending on class\n"
            "   • Apply: scholarships.gov.in → Central Sector Schemes\n\n"
            "2. PM CARES FOR CHILDREN (if parent passed away during COVID)\n"
            "   • Monthly stipend + education support\n"
            "   • pmcaresforchildren.in\n\n"
            "3. CENTRAL SECTOR SCHOLARSHIP FOR COLLEGE (later)\n"
            "   • Top 20 percentile in Class 12\n"
            "   • Rs. 10,000-20,000/year for college\n\n"
            "4. NMMS — when you are in Class 8\n"
            "   • For ALL categories if income < 3.5 lakh\n"
            "   • Rs. 12,000/year — best opportunity!\n\n"
            "Check your school's notice board regularly and ask the headmaster — "
            "many students miss deadlines simply because they didn't know in time."
        ),
        days_ago=5,
    )

    return student


def seed_arjun(teacher, teacher_user):
    """Arjun Singh — Grade 7, CBSE, Hindi."""
    user, created = User.objects.get_or_create(
        username="arjun",
        defaults={
            "email": "arjun@demo.ruralsiksha.in",
            "first_name": "Arjun",
            "last_name": "Singh",
            "role": "student",
            "school_name": "Govt. Boys School, Bidar",
        },
    )
    if created:
        user.set_password("demo123")
        user.save()
    student, _ = Student.objects.get_or_create(
        user=user,
        defaults={
            "grade": 7,
            "subjects_interested": "maths,science,english",
            "attendance": 81.0,
            "total_sessions": 6,
            "total_quiz_attempts": 12,
        },
    )

    maths_quizzes = [
        (1, "Integers",                       62, 21),
        (2, "Fractions and Decimals",          68, 16),
        (3, "Data Handling",                   60, 12),
        (4, "Simple Equations",                70, 7),
        (5, "Lines and Angles",                74, 2),
    ]
    for num, title, pct, days in maths_quizzes:
        ch = _ensure_chapter("maths", 7, num, title)
        quiz = _ensure_quiz(ch, "maths", 7, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=16))

    science_quizzes = [
        (1, "Nutrition in Plants",          68, 20),
        (2, "Nutrition in Animals",          72, 15),
        (3, "Fibre to Fabric",               62, 10),
        (4, "Heat",                          70, 5),
        (5, "Acids, Bases and Salts",         74, 1),
    ]
    for num, title, pct, days in science_quizzes:
        ch = _ensure_chapter("science", 7, num, title)
        quiz = _ensure_quiz(ch, "science", 7, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=15))

    english_quizzes = [
        (1, "Three Questions",        58, 18),
        (2, "A Gift of Chappals",      65, 8),
    ]
    for num, title, pct, days in english_quizzes:
        ch = _ensure_chapter("english", 7, num, title)
        quiz = _ensure_quiz(ch, "english", 7, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=17))

    # Hindi (Vasant Bhag 2) — Grade 7
    hindi_quizzes = [
        (1, "Hum Panchi Unmukt Gagan Ke", 60, 19),
        (2, "Dad Kahe So Kijiye",          64, 14),
        (3, "Himalay Ki Betiyaan",          68,  9),
        (4, "Kathin Nishad",               65,  4),
        (5, "Mithai Wala",                 70,  1),
    ]
    for num, title, pct, days in hindi_quizzes:
        ch = _ensure_chapter("hindi", 7, num, title)
        quiz = _ensure_quiz(ch, "hindi", 7, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=18))

    # Kannada (Grade 7 — moderate scores)
    kn_quizzes = [
        (1, "Vachana Sahitya",       60, 17),
        (2, "Purandaradasa Keertane",64, 10),
        (3, "Karnataka Darshana",    68,  3),
    ]
    for num, title, pct, days in kn_quizzes:
        ch = _ensure_chapter("kannada", 7, num, title)
        quiz = _ensure_quiz(ch, "kannada", 7, f"{title} - Quiz", teacher)
        _record_attempt(student, quiz, pct, ago(days, hour=12))

    _add_tutor_session(
        student, 7, "CBSE", "maths", "Simple Equations", "hi",
        [
            ("student", "Simple equation aur expression mein kya fark hota hai?"),
            ("tutor",   "Expression ek mathematical phrase hai jisme equal sign nahi hota — jaise 3x + 2 ya 5y - 7. Equation mein equal sign hota hai jaise 3x + 2 = 8. Equation hamesha batata hai ki dono side equal hain."),
            ("student", "4x + 7 = 23 ko solve karo mujhe."),
            ("tutor",   "Step 1: 7 dono side se ghataao: 4x + 7 - 7 = 23 - 7, iska matlab 4x = 16. Step 2: Dono taraf 4 se divide karo: x = 16/4 = 4. Verify karein: 4(4) + 7 = 16 + 7 = 23. Sahi hai! Yaad rakho: jo bhi ek side karo, dono sides karo."),
        ],
        ago(11, hour=18),
    )

    _add_tutor_session(
        student, 7, "CBSE", "science", "Nutrition in Plants", "hi",
        [
            ("student", "Plants khud apna khana kaise banate hain? Photosynthesis kya hai?"),
            ("tutor",   "Photosynthesis mein plants 3 cheezein use karte hain: sunlight, water (roots se), aur CO₂ (leaves se stomata se). Chlorophyll ki maujoodgi mein reaction hoti hai: 6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ (glucose) + 6O₂. Plants khud glucose banate hain — isliye unhe 'producers' kehte hain."),
            ("student", "Kya sab plants photosynthesis karte hain? Fungi ke baare mein kya?"),
            ("tutor",   "Nahi! Fungi (jaise mushroom, bread mould) photosynthesis nahi karte — unme chlorophyll nahi hota. Ve dead organic matter se nutrition absorb karte hain — saprotrophic nutrition. Cuscuta (amarbel) jaise parasitic plants dusre plants ka juice peete hain. Insectivorous plants jaise Venus Flytrap insects pakadke khate hain! Plants ki duniya bahut interesting hai."),
        ],
        ago(7, hour=17),
    )

    _add_scheme_query(
        student, teacher_user,
        question=(
            "Main 7th class mein hun aur mere marks achhe hain lekin ghar ki aarthik "
            "sthiti theek nahi hai. Koi scholarship ya government help hai kya?"
        ),
        ai_answer=(
            "Bilkul! Aapke liye kaafi options hain:\n\n"
            "1. NSP PRE-MATRIC SCHOLARSHIP\n"
            "   • Class 1-10 ke liye, government school students\n"
            "   • Family income < 1 lakh/year\n"
            "   • Rs. 1,100/year + Rs. 500 books allowance\n"
            "   • Apply: scholarships.gov.in\n\n"
            "2. OBC/SC/ST PRE-MATRIC SCHOLARSHIP (agar category applicable hai)\n"
            "   • Income limit 2.5 lakh/year\n"
            "   • Zyada amount milega\n\n"
            "3. NMMS (jab Class 8 mein jaao)\n"
            "   • Rs. 12,000/year ka scholarship\n"
            "   • Exam dena padega — abhi se Maths aur Science pakki karo\n\n"
            "4. RAJYA SARKAR KI SCHOLARSHIP\n"
            "   • Karnataka mein: Sanchi Honnamma scholarship, Rajiv Gandhi scholarship\n"
            "   • State education portal check karo\n\n"
            "Aapke achhe marks hain — yeh bahut bada faayda hai! NMMS ke liye abhi se "
            "taiyaari shuru karo. MAT reasoning aur NCERT Maths/Science pakka karo."
        ),
        days_ago=12,
    )

    _add_scheme_query(
        student, teacher_user,
        question="My family wants to know about free coaching for competitive exams. Is there any government scheme?",
        ai_answer=(
            "Yes! Several government schemes provide FREE coaching:\n\n"
            "1. FREE COACHING SCHEME — Ministry of Social Justice\n"
            "   • For SC/OBC students preparing for competitive exams\n"
            "   • Covers UPSC, SSC, Banking, Railways, State PCS\n"
            "   • Apply: coaching.dosje.gov.in\n\n"
            "2. NIOS (National Institute of Open Schooling)\n"
            "   • Free study material for Classes 9-12\n"
            "   • Very affordable exam fees\n"
            "   • Good for students who need flexible timing\n\n"
            "3. PM SHRI SCHOOLS\n"
            "   • Upgraded government schools with modern facilities\n"
            "   • Check if your school is a PM SHRI school\n\n"
            "4. DIKSHA PLATFORM (FREE)\n"
            "   • diksha.gov.in — thousands of free video lessons\n"
            "   • NCERT textbook solutions and practice tests\n"
            "   • Works on mobile phone!\n\n"
            "5. SWAYAM PRABHA (FREE)\n"
            "   • 32 DTH channels with free educational content\n"
            "   • PM eVIDYA channel on TV\n\n"
            "Right now, focus on NMMS when you hit Class 8 — "
            "that Rs. 12,000/year scholarship will help fund your future coaching!"
        ),
        days_ago=6,
    )

    return student


# ── main command ───────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Seed 6 realistic demo students for presentation (safe to re-run)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo student data ...\n")

        # Ensure a demo teacher exists
        teacher_user, created = User.objects.get_or_create(
            username="teacher",
            defaults={
                "email": "teacher@demo.ruralsiksha.in",
                "first_name": "Demo",
                "last_name": "Teacher",
                "role": "teacher",
            },
        )
        if created:
            teacher_user.set_password("teacher123")
            teacher_user.save()

        teacher, _ = Teacher.objects.get_or_create(
            user=teacher_user,
            defaults={
                "assigned_grades": "1,2,3,4,5,6,7,8,9,10",
                "assigned_subjects": "maths,science,english,social_science,kannada",
            },
        )

        results = [
            ("Ravi Kumar   (Grade 8 CBSE)",           lambda: seed_ravi(teacher, teacher_user)),
            ("Priya Sharma (Grade 6 CBSE)",            lambda: seed_priya(teacher, teacher_user)),
            ("Ananya Das   (Grade 10 Karnataka)",      lambda: seed_ananya(teacher)),
            ("Suresh Naik  (Grade 5 CBSE)",            lambda: seed_suresh(teacher)),
            ("Meena Patel  (Grade 9 Maharashtra)",     lambda: seed_meena(teacher, teacher_user)),
            ("Arjun Singh  (Grade 7 CBSE)",            lambda: seed_arjun(teacher, teacher_user)),
        ]

        for label, fn in results:
            try:
                fn()
                self.stdout.write(self.style.SUCCESS(f"   {label}"))
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"   {label} — ERROR: {exc}"))

        self.stdout.write(self.style.SUCCESS("\nDemo data ready.\n"))
        self.stdout.write("Login credentials:")
        self.stdout.write("  ravi   / demo123  (Grade 8 — primary demo)")
        self.stdout.write("  priya  / demo123  (Grade 6 — schemes demo)")
        self.stdout.write("  ananya / demo123  (Grade 10 Karnataka)")
        self.stdout.write("  suresh / demo123  (Grade 5 CBSE)")
        self.stdout.write("  meena  / demo123  (Grade 9 Maharashtra)")
        self.stdout.write("  arjun  / demo123  (Grade 7 CBSE)")
        self.stdout.write("  teacher / teacher123")
