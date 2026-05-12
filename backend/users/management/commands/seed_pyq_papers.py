"""
python manage.py seed_pyq_papers

Adds 'Previous Year Paper' mock quizzes covering the full syllabus for every
grade and main subject. 8 mixed-difficulty MCQs per paper, 30-minute duration.

Stored as regular Quiz objects with a special chapter (chapter_number = 91)
so the existing QuizModule UI displays them automatically.

Idempotent — safe to re-run.
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


# (grade, subject, year, [questions])
PAPERS = [

    # ─── GRADE 1 ─────────────────────────────────────────────────────────
    (1, "maths", 2024, [
        _q("8 + 5 = ?", ["12", "13", "14", "15"], "b", "8 + 5 = 13", "easy"),
        _q("Number that comes after 19:", ["18", "20", "21", "29"], "b", "19 + 1 = 20", "easy"),
        _q("Which is greater: 7 or 12?", ["7", "12", "Equal", "Cannot tell"], "b", "12 > 7", "easy"),
        _q("How many sides does a triangle have?", ["2", "3", "4", "5"], "b", "Tri = 3", "easy"),
        _q("16 − 9 = ?", ["5", "6", "7", "8"], "c", "16 − 9 = 7", "easy"),
        _q("Skip count by 2: 4, 6, 8, ?", ["9", "10", "11", "12"], "b", "+2 → 10", "easy"),
        _q("How many ₹2 coins make ₹10?", ["3", "4", "5", "10"], "c", "5 × 2 = 10", "medium"),
        _q("Which shape has no corners?", ["Square", "Triangle", "Circle", "Rectangle"], "c", "Circle is round", "easy"),
    ]),
    (1, "english", 2024, [
        _q("Plural of 'box':", ["Box", "Boxs", "Boxes", "Boxen"], "c", "Adds -es after x", "easy"),
        _q("Which is a vowel?", ["b", "c", "e", "f"], "c", "a, e, i, o, u are vowels", "easy"),
        _q("Past tense of 'eat':", ["Eated", "Ate", "Eaten", "Eating"], "b", "Irregular: eat → ate", "medium"),
        _q("Opposite of 'happy':", ["Big", "Sad", "Tall", "Loud"], "b", "Happy ↔ sad", "easy"),
        _q("A word that names a person, place or thing is a:", ["Verb", "Noun", "Adjective", "Pronoun"], "b", "Definition of a noun", "easy"),
        _q("Choose the correct article: ___ apple", ["A", "An", "The (only)", "No article"], "b", "Vowel sound → 'an'", "medium"),
        _q("Animal that says 'meow':", ["Dog", "Cow", "Cat", "Goat"], "c", "Cats meow", "easy"),
        _q("Capital of the letter 'b':", ["B", "P", "D", "G"], "a", "Capital B", "easy"),
    ]),
    (1, "science", 2024, [
        _q("We see with our:", ["Ears", "Eyes", "Mouth", "Nose"], "b", "Eyes are sense organs for sight", "easy"),
        _q("Which animal gives us milk?", ["Dog", "Cow", "Cat", "Hen"], "b", "Cow's milk is common food", "easy"),
        _q("Mango grows on a:", ["Bush", "Creeper", "Tree", "Grass"], "c", "Mango is a tree", "easy"),
        _q("Wheels of a bicycle are usually:", ["Square", "Round", "Triangle", "Long"], "b", "Round wheels roll", "easy"),
        _q("Hot season is called:", ["Winter", "Summer", "Rainy", "Spring"], "b", "Summer = hot", "easy"),
        _q("Which sense organ helps us smell?", ["Eyes", "Nose", "Tongue", "Skin"], "b", "Nose detects smells", "easy"),
        _q("Birds lay:", ["Babies", "Eggs", "Fruits", "Stones"], "b", "Birds lay eggs", "easy"),
        _q("In rainy season we use:", ["Sweater", "Umbrella / raincoat", "Sunglasses only", "Sandals only"], "b", "Umbrella protects from rain", "easy"),
    ]),

    # ─── GRADE 2 ─────────────────────────────────────────────────────────
    (2, "maths", 2024, [
        _q("23 + 17 = ?", ["30", "40", "41", "50"], "b", "23 + 17 = 40", "easy"),
        _q("60 − 24 = ?", ["26", "36", "44", "46"], "b", "60 − 24 = 36", "easy"),
        _q("Skip count by 5: 10, 15, 20, ?", ["22", "25", "30", "50"], "b", "+5 → 25", "easy"),
        _q("How many minutes in 1 hour?", ["30", "45", "60", "90"], "c", "60 minutes", "easy"),
        _q("How many days in February (non-leap)?", ["28", "29", "30", "31"], "a", "Usually 28", "medium"),
        _q("Continue: A, B, A, B, A, ?", ["A", "B", "C", "D"], "b", "Repeating ABAB", "easy"),
        _q("3 × 4 = ?", ["7", "9", "12", "15"], "c", "3 + 3 + 3 + 3 = 12", "easy"),
        _q("Number just before 100:", ["98", "99", "101", "1000"], "b", "Predecessor of 100", "easy"),
    ]),
    (2, "english", 2024, [
        _q("Plural of 'mouse':", ["Mouses", "Mice", "Mouse", "Mices"], "b", "Irregular plural", "medium"),
        _q("Opposite of 'big':", ["Tall", "Small", "Wide", "Long"], "b", "Big ↔ small", "easy"),
        _q("Use 'a' or 'an': ___ orange", ["A", "An", "The", "No article"], "b", "Vowel sound → 'an'", "medium"),
        _q("'Quickly' is a/an:", ["Noun", "Verb", "Adjective", "Adverb"], "d", "Tells how → adverb", "medium"),
        _q("Past tense of 'run':", ["Runned", "Ran", "Runs", "Running"], "b", "Irregular: run → ran", "medium"),
        _q("Word that describes the noun 'apple' in 'red apple':", ["Red (adjective)", "Apple", "Is", "The"], "a", "Adjective", "easy"),
        _q("Word with same sound as 'cat':", ["Sit", "Bat", "Dog", "Fox"], "b", "Rhymes with 'cat'", "easy"),
        _q("Which is a complete sentence?", ["The dog.", "Runs.", "The dog runs.", "Running fast."], "c", "Subject + verb", "medium"),
    ]),
    (2, "science", 2024, [
        _q("Plants make their food using:", ["Soil only", "Sunlight, water and air", "Milk", "Honey"], "b", "Photosynthesis basics", "easy"),
        _q("Animals that eat only plants are called:", ["Carnivores", "Herbivores", "Omnivores", "Insects"], "b", "Cow, goat = herbivores", "easy"),
        _q("Water boils at:", ["50°C", "75°C", "100°C", "200°C"], "c", "100°C at sea level", "medium"),
        _q("Cotton clothes are best for:", ["Cold winter", "Hot summer", "Heavy rain", "Snow"], "b", "Cotton is cool and breathable", "easy"),
        _q("A baby cow is called a:", ["Puppy", "Calf", "Kitten", "Foal"], "b", "Baby cow = calf", "easy"),
        _q("Which is a non-living thing?", ["Tree", "Bird", "Stone", "Cat"], "c", "Stone has no life", "easy"),
        _q("Drinking enough water keeps us:", ["Sick", "Hydrated and healthy", "Sleepy", "Hungry"], "b", "Hydration is essential", "easy"),
        _q("Honey is made by:", ["Cows", "Bees", "Goats", "Hens"], "b", "Bees make honey from nectar", "easy"),
    ]),

    # ─── GRADE 3 ─────────────────────────────────────────────────────────
    (3, "maths", 2024, [
        _q("Place value of 7 in 472:", ["7", "70", "700", "47"], "b", "Tens place", "medium"),
        _q("Successor of 999:", ["998", "1000", "9999", "10000"], "b", "999 + 1 = 1000", "easy"),
        _q("8 × 7 = ?", ["54", "56", "58", "63"], "b", "Times tables: 56", "easy"),
        _q("100 − 47 = ?", ["43", "53", "57", "63"], "b", "100 − 47 = 53", "easy"),
        _q("How many ₹5 coins make ₹50?", ["5", "10", "15", "25"], "b", "10 × 5 = 50", "easy"),
        _q("Most common value in 3, 4, 4, 5, 4, 6:", ["3", "4", "5", "6"], "b", "4 occurs 3 times → mode", "medium"),
        _q("From 8:30 AM to 9:00 AM is:", ["15 min", "20 min", "30 min", "45 min"], "c", "Half an hour", "easy"),
        _q("If 1 box has 12 pencils, 5 boxes have:", ["50", "55", "60", "65"], "c", "5 × 12 = 60", "medium"),
    ]),
    (3, "english", 2024, [
        _q("Past tense of 'go':", ["Goed", "Went", "Gone", "Going"], "b", "Irregular", "easy"),
        _q("Pronoun for 'a girl':", ["He", "She", "It", "They"], "b", "She replaces 'a girl'", "easy"),
        _q("'Quickly' is a/an:", ["Noun", "Adverb", "Adjective", "Pronoun"], "b", "Adverb (how)", "medium"),
        _q("Plural of 'child':", ["Childs", "Children", "Childes", "Childrens"], "b", "Irregular plural", "easy"),
        _q("Synonym of 'big':", ["Small", "Tiny", "Large", "Short"], "c", "Synonym = same meaning", "easy"),
        _q("Antonym of 'fast':", ["Quick", "Slow", "Speedy", "Rapid"], "b", "Opposite of fast", "easy"),
        _q("Which is a question?", ["Run fast.", "What is your name?", "She is happy.", "I like apples."], "b", "Has question mark", "easy"),
        _q("Conjunction in: 'I read books and I play.'", ["read", "books", "and", "play"], "c", "And joins clauses", "medium"),
    ]),
    (3, "science", 2024, [
        _q("Plants release ___ during photosynthesis:", ["Carbon dioxide", "Oxygen", "Hydrogen", "Smoke"], "b", "Plants release O₂", "easy"),
        _q("Tall plants with thick stems are:", ["Herbs", "Shrubs", "Trees", "Grass"], "c", "Trees have woody trunks", "easy"),
        _q("Air that moves is called:", ["Still air", "Wind", "Storm only", "Steam"], "b", "Moving air = wind", "easy"),
        _q("All living things show:", ["No growth", "Growth, reproduction, response", "Static behaviour", "No movement ever"], "b", "Living things have these features", "easy"),
        _q("Which is non-living?", ["Bird", "Tree", "Cloud", "Cat"], "c", "Cloud is non-living", "medium"),
        _q("Healthy snack:", ["Chocolate only", "Fruits like apple, banana", "Stones", "Plastic chips"], "b", "Fresh fruits", "easy"),
        _q("Roots of a plant grow:", ["Up to the sky", "Down into soil", "Sideways only", "On leaves"], "b", "Roots go into soil", "easy"),
        _q("Karnataka's state language is:", ["Tamil", "Kannada", "Hindi", "Marathi"], "b", "Kannada", "easy"),
    ]),

    # ─── GRADE 4 ─────────────────────────────────────────────────────────
    (4, "maths", 2024, [
        _q("How many edges does a cube have?", ["6", "8", "10", "12"], "d", "Cube = 12 edges", "medium"),
        _q("1 km = ___ metres", ["100", "500", "1000", "10000"], "c", "1 km = 1000 m", "easy"),
        _q("12 × 5 = ?", ["50", "55", "60", "65"], "c", "12 × 5 = 60", "easy"),
        _q("48 ÷ 6 = ?", ["7", "8", "9", "10"], "b", "48 ÷ 6 = 8", "easy"),
        _q("1 litre = ___ mL", ["10", "100", "1000", "10000"], "c", "1 L = 1000 mL", "easy"),
        _q("From 9 AM to 11:30 AM is:", ["1 hr", "2 hr", "2 hr 30 min", "3 hr"], "c", "2 hours 30 minutes", "medium"),
        _q("Sum of angles in a triangle:", ["90°", "180°", "270°", "360°"], "b", "Always 180°", "easy"),
        _q("Half of 250:", ["100", "125", "150", "200"], "b", "250 ÷ 2 = 125", "easy"),
    ]),
    (4, "english", 2024, [
        _q("Choose the correct: He ___ to school every day.", ["go", "goes", "going", "gone"], "b", "Singular subject + 's'", "medium"),
        _q("Plural of 'leaf':", ["Leafs", "Leaves", "Leafes", "Leaf"], "b", "f → ves", "medium"),
        _q("Synonym of 'happy':", ["Sad", "Joyful", "Angry", "Tired"], "b", "Same meaning", "easy"),
        _q("Antonym of 'rich':", ["Wealthy", "Poor", "Big", "Tall"], "b", "Opposite", "easy"),
        _q("Which is the proper noun?", ["girl", "Delhi", "school", "happy"], "b", "Names a specific place", "medium"),
        _q("Tense of 'I will go':", ["Past", "Present", "Future", "Continuous"], "c", "'will' = future", "medium"),
        _q("Punctuate: 'where are you going'", ["Where are you going?", "where are you going.", "Where are you going!", "where are you going,"], "a", "Question + capital W", "easy"),
        _q("Person who teaches:", ["Doctor", "Teacher", "Driver", "Painter"], "b", "Teacher teaches", "easy"),
    ]),
    (4, "science", 2024, [
        _q("Honey is collected from:", ["Trees", "Beehives by bees", "Cow", "Goat"], "b", "Bees make honey", "easy"),
        _q("Wheels of a vehicle are usually:", ["Square", "Round (so they roll)", "Triangle", "Long"], "b", "Round wheels roll", "easy"),
        _q("In hilly areas children may walk to school on:", ["Boats", "Narrow paths", "Trains", "Planes"], "b", "Long mountain walks", "easy"),
        _q("Beekeeping is also called:", ["Apiculture", "Sericulture", "Pisciculture", "Horticulture"], "a", "Apiculture", "medium"),
        _q("UNESCO heritage site in Karnataka:", ["Hampi", "Taj Mahal", "Red Fort", "Charminar"], "a", "Hampi ruins", "medium"),
        _q("Folk dance form of Karnataka:", ["Kathakali", "Yakshagana", "Kathak", "Mohiniyattam"], "b", "Yakshagana", "medium"),
        _q("Cauvery river originates at:", ["Talakaveri (Coorg)", "Hampi", "Bengaluru", "Mysuru"], "a", "Talakaveri in Kodagu", "medium"),
        _q("Bishnois are famous for:", ["Building cities", "Protecting nature and life", "Hunting", "Trading"], "b", "Bishnoi protectors of nature", "medium"),
    ]),

    # ─── GRADE 5 ─────────────────────────────────────────────────────────
    (5, "maths", 2024, [
        _q("Place value of 5 in 25,634:", ["5", "50", "500", "5000"], "d", "Thousands place", "easy"),
        _q("Fraction 3/4 in decimal form:", ["0.25", "0.5", "0.75", "1.0"], "c", "3 ÷ 4 = 0.75", "medium"),
        _q("LCM of 4 and 6:", ["10", "12", "18", "24"], "b", "Smallest common multiple", "medium"),
        _q("HCF of 8 and 12:", ["2", "4", "6", "8"], "b", "Greatest common factor", "medium"),
        _q("Area of square with side 7 cm:", ["28", "49", "56", "70"], "b", "7 × 7 = 49", "easy"),
        _q("How many degrees in a right angle?", ["45°", "60°", "90°", "180°"], "c", "Right angle = 90°", "easy"),
        _q("If 1 kg fish costs ₹75, what is 4 kg?", ["₹225", "₹280", "₹300", "₹350"], "c", "4 × 75 = 300", "easy"),
        _q("(-3) × (-4) = ?", ["-12", "-7", "7", "12"], "d", "Neg × neg = pos", "medium"),
    ]),
    (5, "science", 2024, [
        _q("Which animal has the strongest sense of smell?", ["Cat", "Dog", "Cow", "Snake"], "b", "Dogs have ~300M smell receptors", "easy"),
        _q("Tongue's basic tastes:", ["Sweet, sour, hot, cold", "Sweet, sour, salty, bitter", "Spicy, sweet, hot, sour", "Soft, hard, sour, sweet"], "b", "Four basic tastes", "easy"),
        _q("Coconut seeds are mainly dispersed by:", ["Wind", "Water", "Animals", "Explosion"], "b", "Coconuts float across sea", "easy"),
        _q("Mango pickle is preserved by:", ["Sugar and water", "Salt and oil", "Vinegar only", "Honey"], "b", "Salt + oil prevent spoilage", "easy"),
        _q("Snakes hear through:", ["Outer ears", "Mouth", "Vibrations on the ground", "Eyes"], "c", "Sense vibrations", "medium"),
        _q("A leaking tap wastes:", ["A few drops only", "Many litres over time", "Nothing", "Only milk"], "b", "Drips add up significantly", "medium"),
        _q("Bats find their way using:", ["Smell", "Echolocation", "Heat", "Light"], "b", "Sound + echo", "easy"),
        _q("Karnataka's state animal:", ["Tiger", "Indian elephant", "Lion", "Cow"], "b", "Indian elephant", "medium"),
    ]),
    (5, "english", 2024, [
        _q("Plural of 'man':", ["Mans", "Men", "Mens", "Man"], "b", "Irregular plural", "easy"),
        _q("Synonym of 'begin':", ["End", "Stop", "Start", "Pause"], "c", "Begin = start", "easy"),
        _q("Antonym of 'easy':", ["Simple", "Difficult", "Light", "Soft"], "b", "Easy ↔ difficult", "easy"),
        _q("Choose correct: She ___ a doctor.", ["am", "is", "are", "be"], "b", "She/he/it + 'is'", "medium"),
        _q("Past tense of 'sing':", ["Singed", "Sang", "Sung", "Singing"], "b", "Sing → sang → sung", "medium"),
        _q("'Beautifully' is a/an:", ["Noun", "Verb", "Adjective", "Adverb"], "d", "Adverb (how)", "medium"),
        _q("Choose article: ___ honest man", ["A", "An", "The", "No article"], "b", "Silent 'h' → 'an'", "hard"),
        _q("In 'After a Bath', what makes us feel fresh?", ["A bath", "A nap", "A meal", "A walk"], "a", "From the poem", "easy"),
    ]),
    (5, "kannada", 2024, [
        _q("'Naayi' means:", ["Cat", "Dog", "Cow", "Goat"], "b", "Naayi = dog", "easy"),
        _q("'Hannu' means:", ["Vegetable", "Fruit", "Flower", "Tree"], "b", "Hannu = fruit", "easy"),
        _q("'Tayi' means:", ["Father", "Mother", "Brother", "Sister"], "b", "Tayi = mother", "easy"),
        _q("Capital of Karnataka:", ["Mysuru", "Bengaluru", "Hubballi", "Mangaluru"], "b", "Bengaluru is capital", "easy"),
        _q("Number of vowels in Kannada alphabet:", ["10", "13", "16", "20"], "b", "13 swaragalu", "medium"),
        _q("'Mavinahannu' is:", ["Apple", "Mango", "Banana", "Orange"], "b", "Mavu = mango", "easy"),
        _q("Karnataka state language:", ["Tamil", "Kannada", "Hindi", "Marathi"], "b", "Kannada", "easy"),
        _q("Karnataka was unified on:", ["1 Nov 1956", "15 Aug 1947", "26 Jan 1950", "1 Nov 1973"], "a", "States Reorganisation 1956", "medium"),
    ]),
]


PAPERS_6_TO_10 = [

    # ─── GRADE 6 ─────────────────────────────────────────────────────────
    (6, "maths", 2024, [
        _q("Roman numeral for 50:", ["L", "C", "D", "M"], "a", "L = 50", "easy"),
        _q("Smallest prime number:", ["1", "2", "3", "5"], "b", "2 is the smallest (only even) prime", "easy"),
        _q("HCF of 18 and 24:", ["3", "6", "9", "12"], "b", "Greatest common factor", "medium"),
        _q("Sum of angles in a triangle:", ["90°", "180°", "270°", "360°"], "b", "Always 180°", "easy"),
        _q("(-5) + 3 = ?", ["-8", "-2", "2", "8"], "b", "Number-line jump", "easy"),
        _q("Predecessor of 1000:", ["999", "1001", "100", "10"], "a", "1000 − 1", "easy"),
        _q("A polygon with 4 sides:", ["Triangle", "Quadrilateral", "Pentagon", "Hexagon"], "b", "Quad = 4", "easy"),
        _q("Place value of 5 in 25,634:", ["5", "50", "500", "5000"], "d", "Thousands place", "medium"),
    ]),
    (6, "science", 2024, [
        _q("Vitamin C deficiency causes:", ["Rickets", "Scurvy", "Goitre", "Anaemia"], "b", "Bleeding gums = scurvy", "easy"),
        _q("Honey is produced by:", ["Cows", "Bees", "Goats", "Hens"], "b", "Bees from nectar", "easy"),
        _q("Wood is a:", ["Transparent material", "Translucent material", "Opaque material", "Liquid"], "c", "Cannot see through wood", "easy"),
        _q("Silk is obtained from:", ["Sheep", "Silkworm cocoon", "Cotton plant", "Jute plant"], "b", "Silkworm cocoons", "easy"),
        _q("To separate sand from water:", ["Hand-picking", "Filtration", "Magnet", "Sieving"], "b", "Filter paper traps sand", "easy"),
        _q("Number of bones in adult human body:", ["106", "150", "206", "300"], "c", "206 bones", "medium"),
        _q("Ball-and-socket joint is found at:", ["Knee", "Shoulder/hip", "Elbow", "Skull"], "b", "All-direction joint", "medium"),
        _q("Animals that eat both plants and animals are called:", ["Herbivores", "Carnivores", "Omnivores", "Producers"], "c", "Omni = both", "easy"),
    ]),
    (6, "english", 2024, [
        _q("Plural of 'tooth':", ["Tooths", "Teeth", "Toothes", "Teethes"], "b", "Irregular plural", "medium"),
        _q("Synonym of 'small':", ["Big", "Tiny", "Wide", "Long"], "b", "Same meaning", "easy"),
        _q("Antonym of 'cold':", ["Cool", "Hot", "Wet", "Dry"], "b", "Opposite", "easy"),
        _q("Choose the correct verb: She ___ singing.", ["am", "is", "are", "be"], "b", "Singular subject", "medium"),
        _q("Past tense of 'write':", ["Writed", "Wrote", "Written", "Writing"], "b", "Write → wrote → written", "medium"),
        _q("Who saved the baby in 'The Friendly Mongoose'?", ["A bird", "The mongoose", "A dog", "A cat"], "b", "Mongoose killed the snake", "easy"),
        _q("Who took the lift in 'How the Dog Found Himself a Master'?", ["The dog with man", "The wolf", "The bear", "Lion"], "a", "Dog finally chose man", "medium"),
        _q("'Beautifully' is a/an:", ["Noun", "Verb", "Adjective", "Adverb"], "d", "Adverb", "medium"),
    ]),
    (6, "kannada", 2024, [
        _q("'Hasiru' is which colour?", ["Red", "Green", "Blue", "Yellow"], "b", "Hasiru = green", "easy"),
        _q("'Kavi' means:", ["Singer", "Poet", "Dancer", "Painter"], "b", "Kavi = poet", "easy"),
        _q("First Kannada Jnanapeetha winner:", ["Kuvempu", "Bendre", "Karanth", "Masti"], "a", "Kuvempu, 1968", "medium"),
        _q("Famous waterfall on Sharavati river:", ["Niagara", "Jog Falls", "Athirapally", "Hogenakkal"], "b", "Jog Falls", "easy"),
        _q("'Uttara' means:", ["South", "North", "East", "West"], "b", "Uttara = north", "easy"),
        _q("World heritage site in N. Karnataka:", ["Mysuru Palace", "Hampi", "Belur", "Halebidu"], "b", "Hampi UNESCO site", "medium"),
        _q("Karnataka's state animal:", ["Tiger", "Indian elephant", "Lion", "Cow"], "b", "Indian elephant", "medium"),
        _q("'Tarakaari' means:", ["Fruit", "Vegetable", "Grain", "Flower"], "b", "Tarakaari = vegetable", "medium"),
    ]),

    # ─── GRADE 7 ─────────────────────────────────────────────────────────
    (7, "maths", 2024, [
        _q("(-3) × (-4) = ?", ["-12", "-7", "7", "12"], "d", "Neg × neg = pos", "easy"),
        _q("0.25 in fraction form:", ["1/4", "1/2", "2/5", "1/3"], "a", "0.25 = 25/100 = 1/4", "easy"),
        _q("Solve: 2x + 5 = 13", ["x=3", "x=4", "x=5", "x=9"], "b", "2x = 8", "medium"),
        _q("Mean of 4, 6, 8, 10:", ["6", "7", "8", "9"], "b", "(4+6+8+10)/4 = 7", "easy"),
        _q("Two angles whose sum = 90° are:", ["Supplementary", "Complementary", "Vertical", "Right"], "b", "Complementary", "easy"),
        _q("Sum of angles in triangle:", ["90°", "180°", "270°", "360°"], "b", "Always 180°", "easy"),
        _q("In right triangle: legs 3, 4 → hypotenuse:", ["5", "6", "7", "12"], "a", "Pythagoras: √25 = 5", "medium"),
        _q("Equilateral triangle each angle:", ["45°", "60°", "75°", "90°"], "b", "180/3 = 60", "easy"),
    ]),
    (7, "science", 2024, [
        _q("Photosynthesis happens in presence of:", ["Moonlight", "Sunlight", "Heat only", "Water only"], "b", "Sunlight powers it", "easy"),
        _q("Largest gland in human body:", ["Pancreas", "Liver", "Salivary gland", "Thyroid"], "b", "Liver", "medium"),
        _q("Acids turn blue litmus:", ["Green", "Red", "Yellow", "Blue"], "b", "Acid → red", "easy"),
        _q("SI unit of temperature:", ["Joule", "Kelvin", "Newton", "Watt"], "b", "Kelvin", "easy"),
        _q("Cyclones often hit ___ coast of India most:", ["Northern", "Eastern", "Western", "None"], "b", "Bay of Bengal", "medium"),
        _q("Air pressure ___ with height:", ["Increases", "Decreases", "Stays same", "Doubles"], "b", "Less air higher up", "medium"),
        _q("Mushrooms get nutrition by:", ["Photosynthesis", "Saprotrophic mode", "Eating animals", "Drinking sea water"], "b", "Decomposing dead matter", "medium"),
        _q("Sericulture means rearing of:", ["Sheep", "Silkworms", "Goats", "Bees"], "b", "Silk worms", "easy"),
    ]),
    (7, "english", 2024, [
        _q("Past tense of 'eat':", ["Eated", "Ate", "Eaten", "Eating"], "b", "Irregular", "easy"),
        _q("Synonym of 'brave':", ["Cowardly", "Courageous", "Sad", "Lazy"], "b", "Same meaning", "easy"),
        _q("Antonym of 'cruel':", ["Mean", "Kind", "Tough", "Strong"], "b", "Opposite", "easy"),
        _q("Choose article: ___ university", ["A", "An", "The", "No article"], "a", "'University' starts with 'y' sound → 'a'", "hard"),
        _q("In 'Three Questions', author is:", ["Tagore", "Leo Tolstoy", "Premchand", "Narayan"], "b", "Russian writer", "medium"),
        _q("'A Gift of Chappals' shows:", ["Wealth", "Compassion / kindness", "Power", "Knowledge"], "b", "Helping the needy", "easy"),
        _q("Conjunction in 'I came and saw':", ["I", "came", "and", "saw"], "c", "And joins clauses", "easy"),
        _q("'Quickly' is a/an:", ["Noun", "Verb", "Adjective", "Adverb"], "d", "Tells how → adverb", "medium"),
    ]),
    (7, "kannada", 2024, [
        _q("Vachana movement leader (12th century):", ["Pampa", "Basavanna", "Kuvempu", "Bendre"], "b", "Basavanna", "medium"),
        _q("Father of Carnatic music:", ["Kanakadasa", "Purandaradasa", "Tyagaraja", "Annamayya"], "b", "Purandaradasa", "medium"),
        _q("Capital of Karnataka:", ["Mysuru", "Mangaluru", "Bengaluru", "Hubballi"], "c", "Bengaluru", "easy"),
        _q("UNESCO heritage in Karnataka:", ["Hampi", "Taj Mahal", "Red Fort", "Qutub Minar"], "a", "Hampi", "medium"),
        _q("Karnataka's state tree:", ["Banyan", "Sandalwood", "Neem", "Mango"], "b", "Sandalwood (Srigandha)", "medium"),
        _q("Coorg is famous for:", ["Iron mining", "Coffee plantations", "Diamond mining", "Tea only"], "b", "Coffee", "easy"),
        _q("Famous classical dance of Karnataka:", ["Bharatanatyam", "Yakshagana", "Kathak", "Mohiniyattam"], "b", "Yakshagana", "medium"),
        _q("'Kavi' means:", ["Singer", "Poet", "Dancer", "Painter"], "b", "Kavi = poet", "easy"),
    ]),

    # ─── GRADE 8 ─────────────────────────────────────────────────────────
    (8, "maths", 2024, [
        _q("Multiplicative inverse of 4/5:", ["-4/5", "5/4", "-5/4", "1"], "b", "a × 1/a = 1", "easy"),
        _q("Solve: 3(x − 2) = 2x + 1", ["x=5", "x=7", "x=9", "x=11"], "b", "3x − 6 = 2x + 1", "medium"),
        _q("Sum of interior angles of any quadrilateral:", ["180°", "270°", "360°", "540°"], "c", "Always 360°", "easy"),
        _q("Square of 12:", ["122", "124", "144", "164"], "c", "12 × 12", "easy"),
        _q("(a + b)² = ?", ["a² + b²", "a² + 2ab + b²", "a² − 2ab + b²", "ab"], "b", "Standard identity", "medium"),
        _q("Probability of head when fair coin tossed:", ["0", "1/2", "1", "1/4"], "b", "1 of 2 outcomes", "easy"),
        _q("√169 = ?", ["11", "12", "13", "14"], "c", "13 × 13 = 169", "easy"),
        _q("Diagonals of a rectangle:", ["Are unequal", "Bisect at 90°", "Are equal and bisect each other", "Don't intersect"], "c", "Equal diagonals", "medium"),
    ]),
    (8, "science", 2024, [
        _q("Curd is formed by:", ["Yeast", "Lactobacillus bacteria", "Virus", "Algae"], "b", "Lactobacillus", "easy"),
        _q("Hottest part of candle flame:", ["Innermost (dark) zone", "Middle (yellow) zone", "Outer (blue) zone", "All same"], "c", "Outer = complete combustion", "medium"),
        _q("Cutting forests on large scale:", ["Afforestation", "Deforestation", "Reforestation", "Plantation"], "b", "Deforestation", "easy"),
        _q("Friction always opposes:", ["Mass", "Motion", "Time", "Volume"], "b", "Opposes relative motion", "easy"),
        _q("Coal and petroleum are:", ["Renewable", "Fossil fuels (non-renewable)", "Solar fuels", "Bio fuels"], "b", "Formed over millions of years", "easy"),
        _q("Newton's first law is also called law of:", ["Action-reaction", "Inertia", "Gravity", "Friction"], "b", "Inertia", "medium"),
        _q("Penicillin was discovered by:", ["Newton", "Alexander Fleming", "Edison", "Curie"], "b", "1928 discovery", "medium"),
        _q("CNG is preferred over petrol because it:", ["Costs more", "Causes less pollution", "Is heavier", "Is solid"], "b", "Cleaner combustion", "easy"),
    ]),
    (8, "english", 2024, [
        _q("Author of 'Bepin Choudhury's Lapse of Memory':", ["Satyajit Ray", "Tagore", "R K Narayan", "Premchand"], "a", "Satyajit Ray", "medium"),
        _q("In 'The Tsunami', Tilly Smith was about:", ["5 yrs", "10 yrs", "15 yrs", "20 yrs"], "b", "About 10", "medium"),
        _q("Christmas truce of WWI was in:", ["1812", "1914", "1944", "1990"], "b", "1914 truce", "medium"),
        _q("Antonym of 'expand':", ["Stretch", "Contract", "Grow", "Enlarge"], "b", "Contract = opposite", "easy"),
        _q("Synonym of 'enormous':", ["Tiny", "Huge", "Average", "Small"], "b", "Synonym = huge", "easy"),
        _q("Past participle of 'write':", ["Writed", "Wrote", "Written", "Writing"], "c", "Past participle", "medium"),
        _q("'Bus Ki Yatra' is famous for its:", ["Tragedy", "Satire/humour", "Romance", "History only"], "b", "Comic satire", "medium"),
        _q("In 'The Best Christmas Present' the letter was hidden in a:", ["Library", "Roll-top desk", "Museum", "Attic"], "b", "Roll-top desk drawer", "easy"),
    ]),
    (8, "social_science", 2024, [
        _q("Sepoy Mutiny / 1st War of Independence year:", ["1757", "1857", "1907", "1947"], "b", "1857", "easy"),
        _q("Subsistence farming means:", ["Farming for export", "Farming mainly for own use", "Plantation farming", "Tea farming"], "b", "Grown to feed family", "easy"),
        _q("Iron and steel industry is a ___ industry:", ["Light", "Heavy / basic", "Agro-based", "Cottage"], "b", "Heavy industry", "easy"),
        _q("Renewable source of power:", ["Coal", "Petroleum", "Solar", "Natural gas"], "c", "Sun is unlimited", "easy"),
        _q("Sugar, cotton, jute industries are:", ["Mineral-based", "Agro-based", "Heavy", "Service"], "b", "Use farm products", "medium"),
        _q("Doctrine of Lapse used by:", ["Akbar", "Lord Dalhousie", "Gandhi", "Nehru"], "b", "British policy", "medium"),
        _q("Most fertile soil for agriculture:", ["Sandy", "Alluvial", "Rocky", "Salty"], "b", "Alluvial soil", "easy"),
        _q("Bhakra Nangal dam is on river:", ["Ganga", "Sutlej", "Krishna", "Cauvery"], "b", "Sutlej", "hard"),
    ]),
    (8, "kannada", 2024, [
        _q("Akkamahadevi belongs to which century?", ["10th", "12th", "16th", "18th"], "b", "12th century", "medium"),
        _q("She was a follower of:", ["Vishnu", "Shiva (Chenna Mallikarjuna)", "Buddha", "Allah"], "b", "Shiva devotee", "medium"),
        _q("'Baalya' means:", ["Old age", "Childhood", "Adulthood", "Marriage"], "b", "Childhood", "easy"),
        _q("'Bettadakke' means:", ["To the river", "To the hill / mountain", "To the sea", "To the city"], "b", "Betta = hill", "easy"),
        _q("Vachanas were composed mostly between:", ["6-8th c.", "12th c.", "15-16th c.", "19th c."], "b", "12th-c. Veerashaiva movement", "medium"),
        _q("'Aatma-charitre' means:", ["Biography", "Autobiography", "Novel", "Drama"], "b", "Self-written life story", "medium"),
        _q("Kannada Jnanapeetha winners count (~2025):", ["3", "5", "8", "12"], "c", "8 winners", "hard"),
        _q("'Smarane' means:", ["Forgetting", "Memory / recollection", "Sleep", "Anger"], "b", "Memory", "medium"),
    ]),

    # ─── GRADE 9 ─────────────────────────────────────────────────────────
    (9, "maths", 2024, [
        _q("Decimal expansion of 1/3:", ["Terminating", "Non-terminating, repeating", "Non-terminating, non-repeating", "Whole number"], "b", "0.333...", "medium"),
        _q("Degree of 3x² + 5x + 7:", ["1", "2", "3", "0"], "b", "Highest power", "easy"),
        _q("(3, -2) lies in quadrant:", ["I", "II", "III", "IV"], "d", "x+, y- → Q4", "easy"),
        _q("Standard form of linear equation in 2 variables:", ["ax + b = 0", "ax² + bx + c = 0", "ax + by + c = 0", "ax + by = c²"], "c", "ax + by + c = 0", "easy"),
        _q("Euclid's elements has how many books?", ["5", "9", "13", "20"], "c", "13", "medium"),
        _q("SI unit of force:", ["Joule", "Newton", "Watt", "Pascal"], "b", "1 N = 1 kg·m/s²", "easy"),
        _q("Distance of (3, 4) from origin:", ["3", "4", "5", "7"], "c", "√(9+16) = 5", "medium"),
        _q("ASA congruence requires:", ["3 sides", "2 angles + included side", "3 angles", "2 sides + 1 angle"], "b", "Angle-Side-Angle", "medium"),
    ]),
    (9, "science", 2024, [
        _q("Sublimation = ?", ["Solid → liquid", "Solid → gas (no liquid stage)", "Gas → liquid", "Liquid → solid"], "b", "E.g. camphor", "easy"),
        _q("Air is a:", ["Pure substance", "Compound", "Mixture", "Element"], "c", "Mixture of gases", "easy"),
        _q("Atomic mass of oxygen:", ["8", "12", "16", "32"], "c", "O = 16 u", "easy"),
        _q("Powerhouse of the cell:", ["Nucleus", "Mitochondrion", "Ribosome", "Vacuole"], "b", "ATP production", "easy"),
        _q("Force = ?", ["mass + acceleration", "mass × acceleration", "mass / acceleration", "mass − acceleration"], "b", "F = ma", "medium"),
        _q("Discoverer of cells:", ["Robert Hooke", "Newton", "Einstein", "Darwin"], "a", "1665 in cork", "easy"),
        _q("To every action there is equal & opposite ___:", ["Push", "Reaction", "Weight", "Speed"], "b", "Newton's 3rd law", "easy"),
        _q("Symbol for sodium:", ["So", "Sa", "Na", "S"], "c", "Na (Latin Natrium)", "easy"),
    ]),
    (9, "english", 2024, [
        _q("'The Fun They Had' is by:", ["Ruskin Bond", "Isaac Asimov", "Mark Twain", "O Henry"], "b", "Sci-fi writer", "easy"),
        _q("Lesson on Albert Einstein is:", ["My Childhood", "A Truly Beautiful Mind", "The Sound of Music", "The Little Girl"], "b", "About Einstein's life", "easy"),
        _q("Bismillah Khan was famous for:", ["Sitar", "Tabla", "Shehnai", "Flute"], "c", "Shehnai maestro", "easy"),
        _q("Author of 'The Little Girl':", ["Premchand", "Katherine Mansfield", "R K Narayan", "O Henry"], "b", "NZ writer", "medium"),
        _q("Past participle of 'eat':", ["Eated", "Ate", "Eaten", "Eating"], "c", "Past participle", "medium"),
        _q("Synonym of 'reluctant':", ["Eager", "Unwilling", "Quick", "Bold"], "b", "Hesitant / unwilling", "medium"),
        _q("APJ Abdul Kalam grew up in:", ["Hyderabad", "Rameswaram", "Madurai", "Trichy"], "b", "Tamil Nadu town", "medium"),
        _q("Einstein's Nobel was in:", ["Chemistry", "Physics", "Peace", "Literature"], "b", "Physics, 1921", "medium"),
    ]),
    (9, "social_science", 2024, [
        _q("French Revolution started in:", ["1689", "1789", "1889", "1989"], "b", "1789 storming of Bastille", "easy"),
        _q("Slogan of French Revolution:", ["Liberty, Equality, Fraternity", "Power, Wealth, Fame", "Strength, Pride, Honour", "Bread, Land, Peace"], "a", "Liberté, Égalité, Fraternité", "easy"),
        _q("Russian Revolution year:", ["1905", "1917", "1939", "1947"], "b", "Oct Revolution 1917", "easy"),
        _q("Lenin led which party:", ["Tsarists", "Bolsheviks", "Mensheviks", "Liberals"], "b", "Bolshevik party", "medium"),
        _q("Capital of France during revolution:", ["Lyon", "Paris", "Versailles", "Marseille"], "b", "Paris", "easy"),
        _q("King executed in French Revolution:", ["Louis XIV", "Louis XV", "Louis XVI", "Napoleon"], "c", "Louis XVI guillotined", "medium"),
        _q("Marx's famous book:", ["Bible", "Communist Manifesto / Das Kapital", "Wealth of Nations", "Republic"], "b", "Marxist works", "medium"),
        _q("Reign of Terror is associated with:", ["Napoleon", "Robespierre", "Louis XVI", "Mirabeau"], "b", "Robespierre", "medium"),
    ]),

    # ─── GRADE 10 ────────────────────────────────────────────────────────
    (10, "maths", 2024, [
        _q("HCF × LCM of two numbers =", ["Sum", "Product", "Difference", "1"], "b", "HCF × LCM = a × b", "easy"),
        _q("Sum of zeroes of x² − 5x + 6:", ["-5", "5", "6", "-6"], "b", "−b/a = 5", "medium"),
        _q("Discriminant of ax² + bx + c:", ["b² + 4ac", "b² − 4ac", "4ac − b²", "2b − ac"], "b", "D = b² − 4ac", "easy"),
        _q("Roots of x² − 5x + 6 = 0:", ["2 and 3", "1 and 6", "-2 and -3", "0 and 5"], "a", "(x-2)(x-3)", "medium"),
        _q("nth term of AP:", ["a + nd", "a + (n-1)d", "a + (n+1)d", "an + d"], "b", "Standard formula", "easy"),
        _q("sin 30° = ?", ["1/2", "√3/2", "1", "0"], "a", "Standard value", "easy"),
        _q("cos 0°:", ["0", "1/2", "1", "√3/2"], "c", "cos 0° = 1", "easy"),
        _q("sin² θ + cos² θ =", ["0", "1", "tan θ", "Undefined"], "b", "Pythagorean identity", "easy"),
    ]),
    (10, "science", 2024, [
        _q("pH of neutral solution:", ["0", "7", "10", "14"], "b", "Pure water = 7", "easy"),
        _q("Most reactive metal in given list:", ["Iron", "Copper", "Sodium", "Gold"], "c", "Sodium very reactive", "easy"),
        _q("Carbon's valence electrons:", ["2", "3", "4", "6"], "c", "Group 14", "easy"),
        _q("Photosynthesis happens in:", ["Mitochondria", "Chloroplasts", "Nucleus", "Ribosomes"], "b", "Chloroplasts contain chlorophyll", "easy"),
        _q("SI unit of current:", ["Volt", "Ampere", "Ohm", "Watt"], "b", "Ampere (A)", "easy"),
        _q("Father of genetics:", ["Darwin", "Gregor Mendel", "Watson", "Lamarck"], "b", "Pea plant experiments", "easy"),
        _q("Modern periodic table arranged by:", ["Atomic mass", "Atomic number", "Density", "Colour"], "b", "Modern law", "easy"),
        _q("Speed of light in vacuum:", ["3 × 10⁸ m/s", "3 × 10⁵ m/s", "3 × 10⁶ m/s", "3 × 10² m/s"], "a", "~300,000 km/s", "medium"),
    ]),
    (10, "english", 2024, [
        _q("Lencho was a:", ["Doctor", "Farmer", "Soldier", "Teacher"], "b", "Farmer in 'A Letter to God'", "easy"),
        _q("Mandela led freedom in:", ["India", "USA", "South Africa", "Kenya"], "c", "Anti-apartheid movement", "easy"),
        _q("Anne Frank's diary written during:", ["WWI", "WWII", "Cold War", "Indian freedom"], "b", "1942-44, hiding from Nazis", "easy"),
        _q("Mandela's prison years:", ["10", "27", "30", "5"], "b", "27 years", "medium"),
        _q("'His First Flight' is about a:", ["Pilot", "Young seagull", "Plane crash", "Bird-watcher"], "b", "Seagull learning to fly", "easy"),
        _q("Diary's confidante was named:", ["Sophie", "Margot", "Kitty", "Lily"], "c", "Anne addressed letters to 'Kitty'", "medium"),
        _q("Mandela's party:", ["BJP", "Congress", "ANC", "Labour"], "c", "African National Congress", "medium"),
        _q("Anne received the diary on her:", ["12th birthday", "13th birthday", "14th birthday", "15th birthday"], "b", "13th, June 12, 1942", "medium"),
    ]),
    (10, "social_science", 2024, [
        _q("Jallianwala Bagh massacre took place at:", ["Delhi", "Amritsar", "Calcutta", "Bombay"], "b", "13 April 1919", "easy"),
        _q("Salt March (Dandi) year:", ["1919", "1922", "1930", "1942"], "c", "1930", "easy"),
        _q("Quit India Movement:", ["1930", "1939", "1942", "1947"], "c", "Aug 1942 — 'Do or Die'", "easy"),
        _q("Bhakra Nangal dam is on:", ["Ganga", "Sutlej", "Krishna", "Cauvery"], "b", "Sutlej river", "medium"),
        _q("HDI is published by:", ["WHO", "UNDP", "UNESCO", "World Bank"], "b", "UN Development Programme", "medium"),
        _q("Chipko movement was about:", ["River cleaning", "Hugging trees to save forests", "Solar energy", "Girls' education"], "b", "Forest conservation, 1973", "medium"),
        _q("RBI established in:", ["1935", "1947", "1950", "1969"], "a", "1935", "medium"),
        _q("Italian unification leader (Red Shirts):", ["Bismarck", "Garibaldi", "Napoleon III", "Metternich"], "b", "Giuseppe Garibaldi", "medium"),
    ]),
    (10, "kannada", 2024, [
        _q("First Kannada Jnanapeetha winner:", ["Kuvempu", "Bendre", "Karanth", "Masti"], "a", "Kuvempu, 1968", "medium"),
        _q("Karnataka unified on:", ["1 Nov 1956", "15 Aug 1947", "26 Jan 1950", "1 Nov 1973"], "a", "States Reorganisation 1956", "easy"),
        _q("Mysore State renamed Karnataka in:", ["1956", "1969", "1973", "1980"], "c", "1 Nov 1973", "medium"),
        _q("Abbakka Rani fought against:", ["British", "Mughals", "Portuguese", "French"], "c", "Portuguese", "medium"),
        _q("Kavirajamarga is the earliest in:", ["Tamil", "Kannada poetics", "Sanskrit", "Telugu"], "b", "Earliest Kannada poetics", "medium"),
        _q("Kannada writers with Jnanapeetha (~2025):", ["3", "5", "8", "12"], "c", "8 winners", "hard"),
        _q("Bendre's Jnanapeetha for:", ["Naaku Tanti", "Yayati", "Karvalo", "Avalokana"], "a", "'Naaku Tanti' (1973)", "medium"),
        _q("'Manushyatva' means:", ["Wealth", "Humanity / human values", "Power", "Fame"], "b", "Quality of being human", "easy"),
    ]),
]


class Command(BaseCommand):
    help = "Add Past-Year Question (PYQ) mock papers for every grade and main subject."

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

        added_papers = 0
        added_questions = 0
        skipped = 0

        all_papers = list(PAPERS) + list(PAPERS_6_TO_10)

        for grade, subject_code, year, questions in all_papers:
            subj, _ = Subject.objects.get_or_create(name=subject_code)
            chapter, _ = Chapter.objects.get_or_create(
                subject=subj, grade=grade, chapter_number=91,
                defaults={
                    "title": f"Past Year Papers ({subject_code})",
                    "description": f"Grade {grade} previous-year mock papers — {subject_code}",
                },
            )

            quiz_title = f"Past Year Paper {year} — {subject_code.replace('_', ' ').title()}"
            quiz, created = Quiz.objects.get_or_create(
                chapter=chapter,
                title=quiz_title,
                defaults={
                    "subject": subject_code,
                    "grade": grade,
                    "description": f"Mock past-year paper for Grade {grade} {subject_code} ({year}). Covers full syllabus.",
                    "num_questions": len(questions),
                    "duration_minutes": 30,
                    "passing_percentage": 35.0,
                    "is_published": True,
                    "created_by": teacher,
                },
            )
            if created:
                added_papers += 1

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
            f"\nPYQ papers: +{added_papers} new papers, "
            f"+{added_questions} new questions ({skipped} duplicates skipped)."
        ))
