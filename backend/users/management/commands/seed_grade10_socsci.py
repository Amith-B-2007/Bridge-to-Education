"""
python manage.py seed_grade10_socsci

Adds Class 10 Social Science quizzes (History, Geography, Civics, Economics)
with 6 real curriculum questions each, based on NCERT 10th syllabus.

Uses chapter numbers >= 31 to avoid collisions.
Idempotent — re-running is safe.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from users.models import Teacher
from resources.models import Subject, Chapter
from quizzes.models import Quiz, Question

User = get_user_model()


def _q(text, opts, correct, explanation="", difficulty="medium"):
    return {
        "text": text,
        "options": [{"key": k, "text": v} for k, v in zip(["a", "b", "c", "d"], opts)],
        "correct": correct,
        "explanation": explanation,
        "difficulty": difficulty,
    }


# Each entry: (chap_num, chapter_title, [questions])  — all Grade 10, social_science
QUIZZES = [

    # ─── HISTORY (India and the Contemporary World - II) ─────────────────
    (31, "Rise of Nationalism in Europe", [
        _q("French Revolution gave the idea of:", ["Monarchy", "Liberty, equality, fraternity (la patrie)", "Apartheid", "Caste system"], "b", "1789 ideals shaped European nationalism", "easy"),
        _q("Napoleonic Code of 1804:", ["Restored privileges of nobility", "Established equality before law and abolished feudalism", "Brought back slavery in France", "Banned the French language"], "b", "Civil Code abolished feudalism", "medium"),
        _q("'Treaty of Vienna' was signed in:", ["1789", "1815", "1830", "1848"], "b", "Conservative settlement after Napoleon", "medium"),
        _q("Italy was unified largely under the leadership of:", ["Bismarck", "Garibaldi and Cavour (with Victor Emmanuel II)", "Napoleon III", "Metternich"], "b", "Garibaldi led Red Shirts; Cavour the diplomat", "medium"),
        _q("Germany was unified through the policy of:", ["Liberalism", "'Blood and iron' under Bismarck", "Pacifism", "Communism"], "b", "Otto von Bismarck", "medium"),
        _q("Frederic Sorrieu's 1848 prints depict:", ["War only", "Dream of a world made up of democratic and social Republics", "Industrial city", "Slave trade"], "b", "Utopian vision of nations", "hard"),
    ]),
    (32, "Nationalism in India", [
        _q("Rowlatt Act (1919) allowed:", ["Free press", "Detention without trial", "More schools", "Lower taxes"], "b", "Detention of political prisoners without trial", "medium"),
        _q("Jallianwala Bagh massacre took place in:", ["Delhi", "Amritsar", "Calcutta", "Bombay"], "b", "13 April 1919, Amritsar", "easy"),
        _q("Non-Cooperation Movement was launched by Gandhi in:", ["1919", "1920–22", "1930", "1942"], "b", "Begun Sept 1920", "medium"),
        _q("Salt March (Dandi March) took place in:", ["1919", "1922", "1930", "1942"], "c", "12 March – 6 April 1930", "easy"),
        _q("Quit India Movement was launched in:", ["1930", "1939", "1942", "1947"], "c", "August 1942 — 'Do or Die'", "easy"),
        _q("Khilafat Movement aimed to protect the:", ["Hindu kings", "Ottoman Caliph", "British monarch", "French king"], "b", "Indian Muslims supported the Caliph", "medium"),
    ]),
    (33, "The Age of Industrialisation", [
        _q("First country to industrialise was:", ["France", "Britain", "Germany", "USA"], "b", "Industrial Revolution began in Britain ~1760", "easy"),
        _q("Spinning Jenny was invented by:", ["James Watt", "James Hargreaves", "Richard Arkwright", "Edmund Cartwright"], "b", "Hargreaves, 1764", "medium"),
        _q("Steam engine was perfected by:", ["Edison", "James Watt", "Stephenson", "Newton"], "b", "James Watt, 1769", "easy"),
        _q("'Proto-industrialisation' refers to:", ["Modern factories", "Earlier rural / cottage production for international markets", "Steel making", "Software industry"], "b", "Pre-factory rural production", "hard"),
        _q("In India, by early 20th century, ___ was a major industrial city:", ["Madras only", "Bombay (textile mills)", "Patna only", "Bhopal only"], "b", "Bombay had many cotton mills", "easy"),
        _q("First cotton mill in India was set up at:", ["Calcutta", "Bombay (1854)", "Madras", "Surat"], "b", "1854, Bombay", "medium"),
    ]),

    # ─── GEOGRAPHY (Contemporary India - II) ─────────────────────────────
    (34, "Resources and Development", [
        _q("Resources that occur in nature are called:", ["Human-made", "Natural resources", "Cultural", "Imaginary"], "b", "From nature", "easy"),
        _q("Resources that can be used again and again:", ["Non-renewable", "Renewable", "Stock", "Reserve"], "b", "Renewable like solar, wind", "easy"),
        _q("Black soil is most suitable for growing:", ["Wheat", "Rice", "Cotton", "Tea"], "c", "Black soil = 'regur' = cotton soil", "medium"),
        _q("Alluvial soil is found mainly in the:", ["Northern plains", "Deccan plateau", "Thar desert", "Western Ghats"], "a", "Indo-Gangetic plain", "easy"),
        _q("Red soil's red colour is due to:", ["Carbon", "Iron oxide", "Salt", "Calcium"], "b", "Iron oxide gives red tint", "medium"),
        _q("Earth Summit on environment was held in 1992 at:", ["Stockholm", "Rio de Janeiro", "Paris", "Kyoto"], "b", "Rio Earth Summit, 1992", "medium"),
    ]),
    (35, "Water Resources", [
        _q("Largest dam in India:", ["Bhakra Nangal", "Tehri", "Hirakud", "Sardar Sarovar"], "c", "Hirakud is the longest earthen dam", "medium"),
        _q("Bhakra Nangal dam is on river:", ["Ganga", "Sutlej", "Krishna", "Cauvery"], "b", "Sutlej river", "medium"),
        _q("Tehri dam is on river:", ["Bhagirathi", "Yamuna", "Cauvery", "Krishna"], "a", "Bhagirathi (a tributary of Ganga)", "medium"),
        _q("Rainwater harvesting in Rajasthan uses underground tanks called:", ["Tankas", "Khadins", "Johads", "Bhungas"], "a", "Tankas — traditional rainwater storage", "hard"),
        _q("Major dam controversy in India:", ["Tehri", "Sardar Sarovar (Narmada Bachao)", "Hirakud", "Bhakra"], "b", "Narmada Bachao Andolan", "medium"),
        _q("Multipurpose projects provide:", ["Only electricity", "Irrigation, electricity, flood control, water supply", "Only drinking water", "Only fishing"], "b", "Multiple uses combined", "easy"),
    ]),
    (36, "Manufacturing Industries", [
        _q("Iron and steel industry is concentrated in:", ["Western Ghats", "Chota Nagpur plateau (Jharkhand–Odisha)", "Thar desert", "Punjab plains"], "b", "Mineral-rich plateau region", "medium"),
        _q("Cotton textile industry's earliest centre in India:", ["Mumbai (Bombay)", "Delhi", "Chennai", "Kolkata"], "a", "Bombay — 'Cottonopolis of India'", "easy"),
        _q("Sugar industry is mainly located in:", ["Hilly areas", "Sugarcane growing belts (UP, Maharashtra)", "Coastal Tamil Nadu only", "Kerala only"], "b", "Near sugarcane fields (weight-losing raw material)", "medium"),
        _q("Software technology parks in India fall under:", ["Heavy industry", "IT / knowledge-based industry", "Cottage industry", "Mining"], "b", "STPI — knowledge industries", "easy"),
        _q("Pollution of rivers by industries is mainly due to:", ["Music", "Untreated effluents", "Tourism", "Wind"], "b", "Industrial effluent waste", "easy"),
        _q("Bhilai Steel Plant is in:", ["Maharashtra", "Chhattisgarh", "Karnataka", "Bihar"], "b", "Bhilai, Chhattisgarh", "medium"),
    ]),

    # ─── CIVICS (Democratic Politics - II) ───────────────────────────────
    (37, "Federalism", [
        _q("India is a:", ["Unitary state", "Federal democracy with a strong centre", "Confederation", "Monarchy"], "b", "Federal with unitary bias", "easy"),
        _q("Three-tier government in India means:", ["Centre, State, Local", "Centre, State, Court", "PM, CM, Mayor", "Lok Sabha, Rajya Sabha, Vidhan Sabha"], "a", "Union, State, Local self-government", "medium"),
        _q("73rd Constitutional Amendment (1992) gave constitutional status to:", ["Lok Sabha", "Panchayati Raj institutions", "Supreme Court", "Election Commission"], "b", "Strengthened rural local self-government", "medium"),
        _q("In India, official language(s) of the Union are:", ["Only Hindi", "Hindi and English (associate)", "Only English", "Only Sanskrit"], "b", "Hindi + English", "easy"),
        _q("Telangana was carved out as a state in:", ["1956", "2000", "2014", "2019"], "c", "29th state, June 2014", "easy"),
        _q("Concurrent List in Constitution holds subjects on which:", ["Only Centre legislates", "Only states legislate", "Both Centre and States can legislate", "No one can legislate"], "c", "Concurrent List = both", "medium"),
    ]),
    (38, "Political Parties", [
        _q("A political party is needed because it:", ["Causes confusion", "Forms governments and gives policy direction", "Always wins elections", "Hates voters"], "b", "Modern democracy needs parties", "easy"),
        _q("India has a:", ["One-party system", "Two-party system", "Multi-party system", "No-party system"], "c", "Many recognised national + state parties", "easy"),
        _q("National party in India must secure at least:", ["1% in 1 state", "6% votes in 4 states + 4 LS seats (or 2% LS seats from 3 states)", "50% in 1 state", "100% always"], "b", "ECI criteria", "hard"),
        _q("'Anti-defection law' prevents:", ["Voting", "Elected MLAs/MPs from switching parties freely", "Election campaigns", "Coalitions"], "b", "10th Schedule — anti-defection", "medium"),
        _q("Election Commission of India is a:", ["Private body", "Constitutional body", "Court", "Local body"], "b", "Established under Article 324", "medium"),
        _q("BJP and INC are examples of:", ["Regional parties", "National political parties", "Religious organisations", "Industrial bodies"], "b", "Recognised national parties", "easy"),
    ]),

    # ─── ECONOMICS (Understanding Economic Development) ──────────────────
    (39, "Development", [
        _q("Development means different things to different people because:", ["People are foolish", "People have different goals and contexts", "Development is fixed", "It is illegal"], "b", "Diverse goals, contexts", "easy"),
        _q("HDI (Human Development Index) is published by:", ["WHO", "UNDP", "UNESCO", "World Bank"], "b", "United Nations Development Programme", "medium"),
        _q("HDI measures:", ["Only income", "Income, education and health", "Population only", "Forests only"], "b", "Three dimensions", "easy"),
        _q("Per capita income alone is a poor measure of development because it ignores:", ["Distribution and quality of life", "Maths", "Politics", "Sports"], "a", "Hides inequality and quality issues", "medium"),
        _q("Sustainable development refers to development that:", ["Uses up all resources fast", "Meets present needs without harming future generations", "Ignores environment", "Stops growth"], "b", "Brundtland definition", "medium"),
        _q("BMI (Body Mass Index) is used to measure:", ["Wealth", "Nutrition / health status", "Education", "Income"], "b", "Health/nutrition indicator", "easy"),
    ]),
    (40, "Money and Credit", [
        _q("Modern forms of money include:", ["Only gold coins", "Currency notes, coins, deposits", "Only barter", "Only stones"], "b", "Notes, coins and bank deposits", "easy"),
        _q("Money is needed because barter has the problem of:", ["Excess supply", "Double coincidence of wants", "Magnetism", "Speed"], "b", "Each must want what the other has", "medium"),
        _q("Self-Help Groups (SHGs) help mainly with:", ["Building schools only", "Small savings and credit, especially for women", "Manufacturing cars", "Cricket"], "b", "Microfinance via SHGs", "medium"),
        _q("Reserve Bank of India was established in:", ["1935", "1947", "1950", "1969"], "a", "RBI Act 1934, started 1935", "medium"),
        _q("Formal sources of credit include:", ["Banks and cooperatives", "Money-lenders only", "Friends only", "Traders only"], "a", "Regulated by RBI", "easy"),
        _q("High interest rates from money-lenders often:", ["Help borrowers", "Trap poor borrowers in debt", "Are illegal everywhere", "Don't matter"], "b", "Debt-traps among poor borrowers", "medium"),
    ]),
]


class Command(BaseCommand):
    help = "Add Class 10 Social Science quizzes (History, Geography, Civics, Economics)."

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
        skipped = 0

        for chap_num, chap_title, questions in QUIZZES:
            subj, _ = Subject.objects.get_or_create(name="social_science")
            chapter, _ = Chapter.objects.get_or_create(
                subject=subj, grade=10, chapter_number=chap_num,
                defaults={
                    "title": chap_title,
                    "description": f"Grade 10 Social Science — {chap_title}",
                },
            )

            quiz_title = f"{chap_title} - Quiz"
            quiz, created = Quiz.objects.get_or_create(
                chapter=chapter,
                title=quiz_title,
                defaults={
                    "subject": "social_science",
                    "grade": 10,
                    "description": f"Practice quiz on {chap_title}",
                    "num_questions": len(questions),
                    "duration_minutes": 15,
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
                        "difficulty": qd.get("difficulty", "medium"),
                        "marks": 1,
                    },
                )
                if q_created:
                    added_questions += 1
                else:
                    skipped += 1

            quiz.num_questions = quiz.questions.count()
            quiz.save(update_fields=["num_questions"])

        self.stdout.write(self.style.SUCCESS(
            f"\nGrade 10 Social Science: +{added_quizzes} quizzes, "
            f"+{added_questions} questions ({skipped} duplicates skipped)."
        ))
        self.stdout.write("Coverage: History (3), Geography (3), Civics (2), Economics (2)")
