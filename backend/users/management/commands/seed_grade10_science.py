"""
python manage.py seed_grade10_science

Adds 9 more Class 10 Science quizzes covering the remaining NCERT chapters
(Periodic Classification, Reproduction, Heredity, Human Eye, Electricity,
Magnetic Effects, Sources of Energy, Our Environment, Management of Natural
Resources). 6 questions each = 54 new questions.

Uses chapter numbers >= 41 to avoid collisions.
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


# (chap_num, chapter_title, [questions]) — all Grade 10, science
QUIZZES = [

    (41, "Periodic Classification of Elements", [
        _q("Modern periodic table is arranged by:", ["Atomic mass", "Atomic number", "Density", "Colour"], "b", "Moseley's modern periodic law", "easy"),
        _q("Elements in Group 1 (alkali metals) include:", ["Na, K, Li", "F, Cl, Br", "He, Ne, Ar", "Ca, Mg, Sr"], "a", "Lithium, sodium, potassium…", "easy"),
        _q("Elements in Group 18 are:", ["Halogens", "Alkali metals", "Noble (inert) gases", "Transition metals"], "c", "He, Ne, Ar, Kr…", "easy"),
        _q("Mendeleev's periodic table left gaps for:", ["Already known elements", "Yet-to-be-discovered elements", "Compounds", "Ions"], "b", "He predicted Ga, Sc, Ge", "medium"),
        _q("Atomic size ___ down a group:", ["Decreases", "Increases", "Stays same", "Becomes zero"], "b", "More shells = larger atom", "medium"),
        _q("Number of periods in modern periodic table:", ["5", "6", "7", "8"], "c", "7 horizontal periods", "medium"),
    ]),

    (42, "How do Organisms Reproduce?", [
        _q("Reproduction in bacteria is mainly by:", ["Sexual", "Binary fission", "Pollination", "Budding"], "b", "Splitting into two", "easy"),
        _q("Yeast reproduces by:", ["Spore formation", "Budding", "Binary fission", "Fragmentation"], "b", "A small bud grows out and detaches", "medium"),
        _q("In flowering plants, male reproductive part is:", ["Stigma", "Stamen (anther + filament)", "Ovary", "Sepal"], "b", "Stamen produces pollen", "easy"),
        _q("Fertilisation in humans takes place in the:", ["Uterus", "Fallopian tube (oviduct)", "Ovary", "Vagina"], "b", "Sperm + egg meet in oviduct", "medium"),
        _q("Placenta connects the:", ["Heart and lungs", "Foetus and the mother's body", "Brain and kidney", "Eye and ear"], "b", "Exchanges nutrients/gases", "easy"),
        _q("Contraceptives prevent:", ["Disease only", "Unwanted pregnancy", "Hunger", "Sleep"], "b", "Contraception controls fertility", "easy"),
    ]),

    (43, "Heredity and Evolution", [
        _q("Father of genetics:", ["Darwin", "Gregor Mendel", "Watson", "Lamarck"], "b", "Mendel — pea plant experiments", "easy"),
        _q("Genes are made of:", ["Carbohydrate", "DNA", "Fat only", "Salt"], "b", "DNA carries genetic information", "easy"),
        _q("Sex of a baby in humans is determined by:", ["The mother's chromosome", "Father's sperm (X or Y)", "Diet", "Climate"], "b", "Y from father → boy, X → girl", "medium"),
        _q("Theory of natural selection was proposed by:", ["Mendel", "Darwin", "Lamarck", "Aristotle"], "b", "Darwin's 'On the Origin of Species' (1859)", "easy"),
        _q("Vestigial organ in humans:", ["Heart", "Appendix", "Liver", "Stomach"], "b", "Appendix is vestigial", "medium"),
        _q("If both parents have genotype Tt for tallness, children are:", ["All tall", "All short", "3 tall : 1 short ratio", "Always 50:50"], "c", "3:1 monohybrid ratio", "hard"),
    ]),

    (44, "The Human Eye and the Colourful World", [
        _q("Lens of the eye focuses image on the:", ["Iris", "Retina", "Cornea", "Pupil"], "b", "Retina = light-sensitive surface", "easy"),
        _q("Defect of vision: 'short-sightedness' (myopia) is corrected with:", ["Convex lens", "Concave lens", "Plane glass", "Plano-convex"], "b", "Diverging concave lens", "medium"),
        _q("Long-sightedness (hypermetropia) is corrected with:", ["Convex lens", "Concave lens", "Cylindrical lens", "Bifocal"], "a", "Converging convex lens", "medium"),
        _q("Splitting of white light into 7 colours by a prism is called:", ["Reflection", "Refraction", "Dispersion", "Diffraction"], "c", "Dispersion of light", "easy"),
        _q("Sky appears blue because of:", ["Reflection from sea", "Scattering of blue light by air molecules", "Pollution", "Heating"], "b", "Rayleigh scattering", "medium"),
        _q("Sun appears red at sunset because:", ["Earth tilts", "Most of the blue light is scattered away over a long path", "Sun is cooler", "Eyes get tired"], "b", "Long path → blue scattered away", "medium"),
    ]),

    (45, "Electricity", [
        _q("SI unit of electric current:", ["Volt", "Ampere", "Ohm", "Watt"], "b", "Ampere (A)", "easy"),
        _q("Ohm's law states: V = ?", ["I × R", "I + R", "I − R", "I / R"], "a", "V = IR", "easy"),
        _q("In a series circuit, total resistance = ?", ["R₁ + R₂ + R₃", "1/R₁ + 1/R₂", "R₁ × R₂", "R₁ − R₂"], "a", "Resistances add up", "medium"),
        _q("Power dissipated = ?", ["V × I", "V + I", "V − I", "V / I"], "a", "P = VI = I²R", "medium"),
        _q("Fuse wire works on the principle of:", ["Insulation", "Heating effect of current", "Magnetic effect", "Chemical effect"], "b", "Melts when current too high", "easy"),
        _q("1 kWh equals:", ["1000 J", "3600 J", "3.6 × 10⁶ J", "360 J"], "c", "1 kW × 1 hr = 3.6 × 10⁶ J", "hard"),
    ]),

    (46, "Magnetic Effects of Electric Current", [
        _q("Magnetic field around a current-carrying conductor was discovered by:", ["Faraday", "Oersted", "Newton", "Ohm"], "b", "Hans Christian Oersted, 1820", "medium"),
        _q("Direction of magnetic field around a wire is given by:", ["Fleming's left-hand rule", "Right-hand thumb rule", "Ohm's law", "Coulomb's law"], "b", "Maxwell / right-hand thumb", "medium"),
        _q("Force on a current-carrying conductor in a magnetic field is given by:", ["Right-hand rule", "Fleming's left-hand rule", "Ohm's law", "Lenz's law"], "b", "Used in motors", "medium"),
        _q("Electric motor converts:", ["Chemical energy to electrical", "Electrical energy to mechanical", "Heat to electrical", "Magnetic to chemical"], "b", "Electric → mechanical", "easy"),
        _q("Electric generator works on the principle of:", ["Ohm's law", "Electromagnetic induction (Faraday)", "Conduction of heat", "Latent heat"], "b", "Faraday's law of induction", "medium"),
        _q("Domestic AC supply in India has frequency:", ["10 Hz", "50 Hz", "60 Hz", "100 Hz"], "b", "50 Hz, 220 V", "easy"),
    ]),

    (47, "Sources of Energy", [
        _q("Renewable source of energy:", ["Coal", "Petroleum", "Solar", "Diesel"], "c", "Sun is unlimited", "easy"),
        _q("Hydropower is generated from:", ["Wind", "Falling water", "Coal", "Sunlight"], "b", "Water turbines", "easy"),
        _q("Nuclear power plants in India use:", ["Coal", "Uranium", "Wood", "Diesel"], "b", "Uranium fuel rods", "medium"),
        _q("Biogas mainly contains:", ["Carbon monoxide", "Methane (CH₄)", "Helium", "Hydrogen sulphide only"], "b", "~50–75% methane", "medium"),
        _q("Solar cells convert:", ["Heat → electricity", "Light energy directly to electricity", "Wind to electricity", "Water to electricity"], "b", "Photovoltaic effect", "easy"),
        _q("Major non-renewable source still widely used:", ["Wind", "Coal", "Solar", "Tidal"], "b", "Coal — fossil fuel", "easy"),
    ]),

    (48, "Our Environment", [
        _q("Decomposers are organisms that:", ["Eat plants only", "Break down dead organic matter (e.g. bacteria, fungi)", "Eat other animals", "Make food"], "b", "Recycle nutrients", "easy"),
        _q("Food chain begins with:", ["Carnivores", "Herbivores", "Producers (plants)", "Decomposers"], "c", "Plants/producers fix solar energy", "easy"),
        _q("Ozone layer protects us from:", ["X-rays only", "Harmful UV rays from the Sun", "Visible light", "Sound"], "b", "Filters most UV-B", "easy"),
        _q("Main cause of ozone layer depletion:", ["Carbon dioxide", "Chlorofluorocarbons (CFCs)", "Methane only", "Water vapour"], "b", "CFCs release Cl that destroys O₃", "medium"),
        _q("Energy transfer in a food chain follows the:", ["100% rule", "10% rule (only ~10% passes to next level)", "50% rule", "75% rule"], "b", "Lindeman's 10% law", "medium"),
        _q("Biodegradable substance:", ["Plastic", "Paper / vegetable peels", "Glass", "Aluminium can"], "b", "Decomposed by microbes", "easy"),
    ]),

    (49, "Management of Natural Resources", [
        _q("3 R's of resource management are:", ["Read, Reduce, Recycle", "Reduce, Reuse, Recycle", "Run, Read, Reuse", "Reuse, Reach, Refuse"], "b", "Reduce, reuse, recycle", "easy"),
        _q("Khadin / johad systems are examples of:", ["Mining", "Traditional water harvesting (Rajasthan)", "Forestry only", "Wind energy"], "b", "Rainwater harvesting", "medium"),
        _q("Chipko movement was associated with:", ["River cleaning", "Saving forests by hugging trees (Uttarakhand)", "Solar energy", "Education for girls"], "b", "Forest conservation, 1973", "medium"),
        _q("Coal and petroleum should be conserved because they:", ["Are infinite", "Are non-renewable and pollute when burnt", "Are tasty", "Glow in the dark"], "b", "Finite + polluting fossil fuels", "easy"),
        _q("Stakeholders in forest management include:", ["Local people, forest department, industries, conservationists", "Only the government", "Only tourists", "Only animals"], "a", "Many groups have a stake", "medium"),
        _q("Ganga Action Plan was launched to:", ["Build dams", "Reduce river pollution", "Increase tourism only", "Promote fishing only"], "b", "Clean the Ganga", "medium"),
    ]),
]


class Command(BaseCommand):
    help = "Add 9 more Class 10 Science quizzes (remaining NCERT chapters)."

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
            subj, _ = Subject.objects.get_or_create(name="science")
            chapter, _ = Chapter.objects.get_or_create(
                subject=subj, grade=10, chapter_number=chap_num,
                defaults={
                    "title": chap_title,
                    "description": f"Grade 10 Science — {chap_title}",
                },
            )

            quiz_title = f"{chap_title} - Quiz"
            quiz, created = Quiz.objects.get_or_create(
                chapter=chapter,
                title=quiz_title,
                defaults={
                    "subject": "science",
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
            f"\nGrade 10 Science: +{added_quizzes} quizzes, "
            f"+{added_questions} questions ({skipped} duplicates skipped)."
        ))
        self.stdout.write(
            "Coverage: Periodic Classification, Reproduction, Heredity, Human Eye, "
            "Electricity, Magnetic Effects, Sources of Energy, Our Environment, "
            "Management of Natural Resources."
        )
