"""
python manage.py seed_questions

Replaces placeholder ('Sample question 1 about ...') questions in every demo
quiz with real curriculum-aligned questions, options, correct answers and
explanations.

Idempotent: only touches quizzes that still have placeholder text. Real
questions added previously are left alone.
"""
from django.core.management.base import BaseCommand
from quizzes.models import Quiz, Question


def _q(text, opts, correct, explanation="", difficulty="medium"):
    """Build a question dict from a list of 4 option strings."""
    keys = ["a", "b", "c", "d"]
    return {
        "text": text,
        "options": [{"key": k, "text": v} for k, v in zip(keys, opts)],
        "correct": correct,
        "explanation": explanation,
        "difficulty": difficulty,
    }


# ─── GRADE 5 ───────────────────────────────────────────────────────────────
QUESTIONS_GRADE_5 = {
    # Maths
    ("The Fish Tale - Quiz", 5): [
        _q("A fisherman catches 24 fish and packs them equally into 4 baskets. How many fish per basket?",
           ["4", "6", "8", "10"], "b", "24 ÷ 4 = 6", "easy"),
        _q("If 1 kg of fish costs ₹75, what is the cost of 4 kg?",
           ["₹225", "₹280", "₹300", "₹350"], "c", "4 × 75 = 300", "easy"),
        _q("A boat travels 8 km per hour. How far does it go in 3 hours?",
           ["11 km", "16 km", "24 km", "32 km"], "c", "Distance = 8 × 3 = 24 km", "medium"),
    ],
    ("Shapes and Angles - Quiz", 5): [
        _q("An angle measuring exactly 90° is called a:",
           ["Acute angle", "Right angle", "Obtuse angle", "Straight angle"], "b", "90° is a right angle", "easy"),
        _q("A complete turn measures:",
           ["90°", "180°", "270°", "360°"], "d", "A full circle = 360°", "easy"),
        _q("How many right angles does a rectangle have?",
           ["2", "3", "4", "6"], "c", "Every corner of a rectangle is 90°", "easy"),
    ],
    ("How Many Squares? - Quiz", 5): [
        _q("Area of a square of side 5 cm?",
           ["10 sq cm", "20 sq cm", "25 sq cm", "30 sq cm"], "c", "Area = side × side = 5 × 5 = 25", "easy"),
        _q("Perimeter of a square of side 6 cm?",
           ["12 cm", "18 cm", "24 cm", "36 cm"], "c", "Perimeter = 4 × 6 = 24 cm", "medium"),
        _q("A rectangle of length 8 cm and width 3 cm has area:",
           ["11 sq cm", "16 sq cm", "22 sq cm", "24 sq cm"], "d", "Area = l × w = 8 × 3 = 24", "medium"),
    ],
    ("Parts and Wholes - Quiz", 5): [
        _q("Which fraction is bigger: 1/2 or 1/4?",
           ["1/2", "1/4", "Both equal", "Cannot tell"], "a", "Halves are bigger pieces than quarters", "easy"),
        _q("3/6 is equivalent to:",
           ["1/2", "1/3", "2/3", "3/4"], "a", "3/6 simplifies to 1/2", "medium"),
        _q("A pizza is cut into 8 equal slices. You eat 3. What fraction did you eat?",
           ["3/5", "3/8", "5/8", "8/3"], "b", "3 of 8 slices = 3/8", "easy"),
    ],
    ("Be My Multiple, I'll be Your Factor - Quiz", 5): [
        _q("Which number is a factor of 12?",
           ["5", "7", "8", "4"], "d", "12 ÷ 4 = 3, so 4 divides 12", "easy"),
        _q("LCM of 4 and 6 is:",
           ["10", "12", "18", "24"], "b", "Smallest number divisible by both 4 and 6 is 12", "medium"),
        _q("HCF of 8 and 12 is:",
           ["2", "4", "6", "8"], "b", "Common factors: 1, 2, 4 — biggest is 4", "medium"),
    ],
    # Science
    ("Super Senses - Quiz", 5): [
        _q("Which animal has the strongest sense of smell?",
           ["Cat", "Dog", "Cow", "Snake"], "b", "Dogs have ~300 million smell receptors vs human 6 million", "easy"),
        _q("Bats find their way in the dark using:",
           ["Smell", "Echolocation (sound)", "Heat", "Light"], "b", "They emit sound and listen for the echo", "easy"),
        _q("Snakes pick up sound through:",
           ["Outer ears", "Mouth", "Vibrations on the ground", "Eyes"], "c", "Snakes have no outer ears — they sense vibrations", "medium"),
    ],
    ("A Snake Charmer's Story - Quiz", 5): [
        _q("Snakes do NOT have:",
           ["Scales", "Outer ears", "A backbone", "Forked tongues"], "b", "Snakes have no external ears", "easy"),
        _q("The instrument played by a snake charmer is called a:",
           ["Sitar", "Been (pungi)", "Tabla", "Flute"], "b", "It is the been or pungi", "easy"),
        _q("A famous snake-killing animal is the:",
           ["Cat", "Mongoose", "Wild boar", "Crocodile"], "b", "Mongooses fight and kill snakes", "medium"),
    ],
    ("From Tasting to Digesting - Quiz", 5): [
        _q("The four basic tastes are:",
           ["Sweet, sour, hot, cold", "Sweet, sour, salty, bitter", "Sweet, hot, salty, spicy", "Sweet, sour, fresh, stale"], "b", "Tongue detects sweet, sour, salty, bitter", "easy"),
        _q("Digestion of food begins in the:",
           ["Stomach", "Mouth", "Liver", "Intestine"], "b", "Saliva starts breaking food in the mouth", "easy"),
        _q("Most absorption of nutrients happens in the:",
           ["Stomach", "Small intestine", "Large intestine", "Throat"], "b", "Small intestine has tiny villi for absorption", "medium"),
    ],
    ("Mangoes Round the Year - Quiz", 5): [
        _q("Mango pickle is preserved using:",
           ["Sugar and water", "Salt and oil", "Vinegar only", "Honey"], "b", "Salt + oil stop bacteria from spoiling food", "easy"),
        _q("Drying food in sunlight removes:",
           ["Salt", "Water", "Sugar", "Air"], "b", "Bacteria can't grow without water", "easy"),
        _q("Which is NOT a method of food preservation?",
           ["Drying", "Pickling", "Leaving cooked food open", "Freezing"], "c", "Open cooked food spoils quickly", "medium"),
    ],
    ("Seeds and Seeds - Quiz", 5): [
        _q("Coconut seeds are mainly dispersed by:",
           ["Wind", "Water", "Animals", "Explosion"], "b", "Coconuts float across the sea", "easy"),
        _q("Cotton seeds are dispersed by:",
           ["Water", "Wind", "Birds", "Insects"], "b", "Light, fluffy fibres carry them on the breeze", "easy"),
        _q("For a seed to germinate it needs:",
           ["Salt and oil", "Water, air and warmth", "Only sunlight", "Only soil"], "b", "Water + air + suitable temperature", "medium"),
    ],
    # English
    ("Ice-Cream Man - Quiz", 5): [
        _q("In the poem, when does the ice-cream man come?",
           ["In winter", "When summer's hot", "On rainy days", "Every morning"], "b", "He comes when summer is hot", "easy"),
        _q("The ice-cream man's cart is described as a:",
           ["School bus", "Wagon of joy", "Boat", "Truck"], "b", "The poem calls it a 'wagon of joy'", "easy"),
        _q("The poem makes children feel:",
           ["Sad", "Happy and excited", "Scared", "Bored"], "b", "Cool ice-cream in summer = joy", "easy"),
    ],
    ("Wonderful Waste! - Quiz", 5): [
        _q("In which Indian state is the story set?",
           ["Punjab", "Kerala (Travancore)", "Bengal", "Rajasthan"], "b", "Travancore is in modern Kerala", "easy"),
        _q("What did the cook prepare from vegetable peels?",
           ["A new curry (avial)", "A sweet", "A drink", "Bread"], "a", "He invented avial — now a famous Kerala dish", "easy"),
        _q("The lesson teaches us:",
           ["To waste food", "Not to waste anything", "To cook only meat", "To eat outside food"], "b", "Even waste can be wonderful when used cleverly", "easy"),
    ],
    # Kannada
    ("Nanna Shaale - Quiz", 5): [
        _q("'Nanna Shaale' means:",
           ["My home", "My school", "My village", "My friend"], "b", "Shaale = school", "easy"),
        _q("In school, students mainly:",
           ["Play only", "Learn and grow", "Sleep", "Eat"], "b", "School is for reading, writing and learning", "easy"),
        _q("Which is a typical school activity?",
           ["Farming", "Reading and writing", "Selling goods", "Cooking food"], "b", "Reading and writing", "easy"),
    ],
    ("Aase Magu - Quiz", 5): [
        _q("'Aase' in Kannada means:",
           ["Anger", "Wish / desire", "Fear", "Happiness"], "b", "Aase = wish or desire", "easy"),
        _q("'Magu' means:",
           ["Adult", "Child / baby", "Old man", "Animal"], "b", "Magu = child", "easy"),
        _q("The lesson teaches the value of:",
           ["Lying", "Hard work and patience", "Greed", "Selfishness"], "b", "Patience and hard work bring rewards", "easy"),
    ],
    ("Kaalige - Quiz", 5): [
        _q("'Kaalu' refers to which body part?",
           ["Hands", "Feet / legs", "Eyes", "Ears"], "b", "Kaalu = leg/foot", "easy"),
        _q("Which body part helps us walk?",
           ["Eyes", "Legs (kaalu)", "Mouth", "Ears"], "b", "Legs help us walk", "easy"),
        _q("The lesson teaches us to:",
           ["Be lazy", "Take care of our body", "Eat less", "Sleep more"], "b", "Care for and respect our body", "easy"),
    ],
    # Generic Grade 5 'Practice Quiz' items (from a separate seed)
    ("Numbers & Place Value - Practice Quiz", 5): [
        _q("Place value of 4 in 3,425?",
           ["4", "40", "400", "4000"], "c", "4 is in hundreds place: 4 × 100 = 400", "easy"),
        _q("Smallest 4-digit number is:",
           ["999", "1000", "1010", "9999"], "b", "1000 is the smallest 4-digit number", "easy"),
        _q("Which is greater: 5,432 or 5,423?",
           ["5,432", "5,423", "Both equal", "Cannot tell"], "a", "Comparing tens: 3 > 2 → 5,432 wins", "medium"),
    ],
    ("Addition & Subtraction - Practice Quiz", 5): [
        _q("345 + 678 = ?",
           ["913", "1023", "1013", "1123"], "b", "345 + 678 = 1023", "easy"),
        _q("1000 − 456 = ?",
           ["444", "544", "554", "654"], "b", "1000 − 456 = 544", "easy"),
        _q("Sum of 234 and 567:",
           ["701", "791", "801", "811"], "c", "234 + 567 = 801", "medium"),
    ],
    ("Multiplication - Practice Quiz", 5): [
        _q("12 × 8 = ?",
           ["86", "96", "106", "112"], "b", "12 × 8 = 96", "easy"),
        _q("25 × 4 = ?",
           ["100", "90", "120", "75"], "a", "25 × 4 = 100", "easy"),
        _q("If 1 box has 24 chocolates, how many in 5 boxes?",
           ["100", "115", "120", "144"], "c", "24 × 5 = 120", "medium"),
    ],
    ("Fractions - Practice Quiz", 5): [
        _q("Which fraction is bigger: 2/3 or 1/3?",
           ["2/3", "1/3", "Equal", "Cannot tell"], "a", "Same denominator → bigger numerator wins", "easy"),
        _q("1/2 + 1/4 = ?",
           ["1/6", "2/6", "3/4", "1/8"], "c", "1/2 = 2/4; 2/4 + 1/4 = 3/4", "medium"),
        _q("4/8 simplified is:",
           ["1/2", "2/4", "1/4", "3/4"], "a", "Divide top & bottom by 4: 1/2", "easy"),
    ],
    ("Living Things - Practice Quiz", 5): [
        _q("Which is a living thing?",
           ["Stone", "Tree", "Chair", "Cup"], "b", "Trees grow, breathe, reproduce", "easy"),
        _q("Living things need:",
           ["Only sunlight", "Food, water and air", "Only food", "Nothing"], "b", "All three are essential", "easy"),
        _q("All living things eventually:",
           ["Stay forever", "Grow and reproduce", "Stop changing", "Become rocks"], "b", "Growth and reproduction are signs of life", "medium"),
    ],
    ("Plants Around Us - Practice Quiz", 5): [
        _q("Plants make their own food by:",
           ["Eating soil", "Photosynthesis (using sunlight)", "Drinking milk", "Sleeping"], "b", "Sunlight + CO₂ + water → food", "easy"),
        _q("Roots of a plant help in:",
           ["Making flowers", "Absorbing water from the soil", "Making seeds", "Producing fruit"], "b", "Roots absorb water and minerals", "easy"),
        _q("Which is a green pigment in leaves?",
           ["Haemoglobin", "Chlorophyll", "Melanin", "Iron"], "b", "Chlorophyll makes leaves green", "medium"),
    ],
    ("Grammar Basics - Practice Quiz", 5): [
        _q("Which is a noun?",
           ["Run", "Quickly", "Apple", "Beautiful"], "c", "Apple is a person/place/thing", "easy"),
        _q("Which is a verb?",
           ["Cat", "Jump", "Tall", "Sweet"], "b", "Jump is an action", "easy"),
        _q("The plural of 'child' is:",
           ["Childs", "Childes", "Children", "Childrens"], "c", "Irregular plural: child → children", "medium"),
    ],
}


# ─── GRADE 6 ───────────────────────────────────────────────────────────────
QUESTIONS_GRADE_6 = {
    # Maths
    ("Knowing Our Numbers - Quiz", 6): [
        _q("Place value of 5 in 25,634?",
           ["5", "50", "500", "5000"], "d", "5 sits in the thousands place: 5 × 1000 = 5000", "easy"),
        _q("The largest 5-digit number is:",
           ["10000", "99999", "100000", "99990"], "b", "All 9s = 99,999", "easy"),
        _q("1 lakh equals how many ten-thousands?",
           ["1", "10", "100", "1000"], "b", "1,00,000 = 10 × 10,000", "medium"),
    ],
    ("Whole Numbers - Quiz", 6): [
        _q("The smallest whole number is:",
           ["-1", "0", "1", "Not defined"], "b", "Whole numbers begin at 0", "easy"),
        _q("Predecessor of 1000?",
           ["999", "1001", "100", "10"], "a", "Predecessor = 1000 - 1 = 999", "easy"),
        _q("Which property states a + b = b + a?",
           ["Associative", "Commutative", "Distributive", "Identity"], "b", "Order doesn't matter in addition", "medium"),
    ],
    ("Playing with Numbers - Quiz", 6): [
        _q("A number divisible by both 2 and 3 is also divisible by:",
           ["4", "5", "6", "9"], "c", "2 × 3 = 6", "easy"),
        _q("Which of these is a prime number?",
           ["9", "15", "21", "23"], "d", "23 has only 1 and 23 as factors", "easy"),
        _q("HCF of 18 and 24?",
           ["3", "6", "9", "12"], "b", "Common factors: 1, 2, 3, 6 → HCF = 6", "medium"),
    ],
    ("Basic Geometrical Ideas - Quiz", 6): [
        _q("A line has:",
           ["2 endpoints", "1 endpoint", "No endpoints", "3 endpoints"], "c", "A line extends infinitely both ways", "easy"),
        _q("A line segment has:",
           ["No endpoints", "1 endpoint", "2 endpoints", "Many endpoints"], "c", "A segment has a fixed start and end", "easy"),
        _q("Two lines that never meet are:",
           ["Intersecting", "Parallel", "Perpendicular", "Curved"], "b", "Parallel lines never intersect", "easy"),
    ],
    ("Understanding Elem. Shapes - Quiz", 6): [
        _q("A triangle with all three sides equal is:",
           ["Scalene", "Isosceles", "Equilateral", "Right-angled"], "c", "Equi = equal, lateral = side", "easy"),
        _q("Sum of all angles of a triangle?",
           ["90°", "180°", "270°", "360°"], "b", "Always 180°", "easy"),
        _q("A polygon with 4 sides is called a:",
           ["Triangle", "Quadrilateral", "Pentagon", "Hexagon"], "b", "Quad = 4", "easy"),
    ],
    # Science
    ("Food: Where Does It Come From? - Quiz", 6): [
        _q("Animals that eat only plants are called:",
           ["Carnivores", "Herbivores", "Omnivores", "Insectivores"], "b", "Herbivores eat plants — e.g. cow, goat", "easy"),
        _q("Honey is produced by:",
           ["Cows", "Bees", "Goats", "Hens"], "b", "Bees collect nectar and convert it to honey", "easy"),
        _q("Humans eat both plants and animals, so we are:",
           ["Herbivores", "Carnivores", "Omnivores", "Producers"], "c", "Omnis = both", "easy"),
    ],
    ("Components of Food - Quiz", 6): [
        _q("Vitamin C deficiency causes:",
           ["Rickets", "Scurvy", "Goitre", "Anaemia"], "b", "Bleeding gums and weakness = scurvy", "easy"),
        _q("Main source of energy in our food is:",
           ["Vitamins", "Carbohydrates", "Minerals", "Water"], "b", "Carbs are the body's main fuel", "easy"),
        _q("Iron deficiency leads to:",
           ["Goitre", "Scurvy", "Anaemia", "Rickets"], "c", "Low iron = low haemoglobin = anaemia", "medium"),
    ],
    ("Fibre to Fabric - Quiz", 6): [
        _q("Which is a natural fibre?",
           ["Nylon", "Polyester", "Cotton", "Acrylic"], "c", "Cotton comes from a plant", "easy"),
        _q("Silk is obtained from the:",
           ["Sheep", "Silkworm", "Goat", "Cotton plant"], "b", "Silkworm cocoons are unwound for silk", "easy"),
        _q("Wool is obtained from:",
           ["Sheep", "Cotton plant", "Silkworm", "Jute plant"], "a", "Sheep's hair becomes wool", "easy"),
    ],
    ("Sorting Materials - Quiz", 6): [
        _q("Materials we can see clearly through are:",
           ["Opaque", "Translucent", "Transparent", "Solid"], "c", "Glass and water are transparent", "easy"),
        _q("Wood is:",
           ["Transparent", "Translucent", "Opaque", "Liquid"], "c", "We cannot see through wood", "easy"),
        _q("A material that dissolves in water is:",
           ["Insoluble", "Soluble", "Opaque", "Magnetic"], "b", "Sugar, salt = soluble", "easy"),
    ],
    ("Separation of Substances - Quiz", 6): [
        _q("To separate stones from rice we use:",
           ["Filtration", "Hand-picking", "Evaporation", "Magnet"], "b", "Pick stones out by hand", "easy"),
        _q("To separate sand from water we use:",
           ["Hand-picking", "Filtration", "Magnet", "Sieving"], "b", "Filter paper traps sand", "easy"),
        _q("To get salt from sea water we use:",
           ["Evaporation", "Sieving", "Magnet", "Hand-picking"], "a", "Water evaporates, salt stays behind", "medium"),
    ],
    # English
    ("Who Did Patrick's Homework? - Quiz", 6): [
        _q("Who actually did Patrick's homework?",
           ["His mother", "A little man (elf)", "His teacher", "His friend"], "b", "A small elf-like creature", "easy"),
        _q("How was the little man caught?",
           ["In a bag", "By the cat", "In a box", "In a net"], "b", "Patrick's cat caught the elf", "easy"),
        _q("By the end of the year Patrick's grades:",
           ["Got worse", "Improved a lot", "Stayed the same", "Disappeared"], "b", "Patrick became a top student", "easy"),
    ],
    ("How the Dog Found Himself a Master - Quiz", 6): [
        _q("Why did the dog leave the wolf?",
           ["Wolf was lazy", "Wolf was afraid of the bear", "Wolf bit him", "Wolf ran away"], "b", "The bear scared the wolf", "easy"),
        _q("Whom did the dog finally choose as his master?",
           ["The wolf", "The bear", "The lion", "Man"], "d", "Man was strongest of all", "easy"),
        _q("The story shows the dog wanted:",
           ["The strongest master", "A loyal friend", "To run away", "To live alone"], "a", "He kept switching for the strongest master", "medium"),
    ],
    ("Taro's Reward - Quiz", 6): [
        _q("Where is the story set?",
           ["India", "Japan", "China", "Korea"], "b", "It is a Japanese folk tale", "easy"),
        _q("What did Taro find flowing in the waterfall?",
           ["Gold", "Sake (rice wine)", "Honey", "Milk"], "b", "A magic waterfall gave sake", "easy"),
        _q("Taro wanted the sake to give to his:",
           ["Wife", "Father", "Friend", "King"], "b", "His old father loved sake", "medium"),
    ],
    ("An Indian-American Woman in Space - Quiz", 6): [
        _q("Who is the lesson about?",
           ["Sunita Williams", "Kalpana Chawla", "Indira Gandhi", "Mary Kom"], "b", "Kalpana Chawla, astronaut", "easy"),
        _q("From which town in India was she?",
           ["Karnal", "Delhi", "Mumbai", "Chennai"], "a", "Karnal, Haryana", "easy"),
        _q("She died in the ___ space shuttle disaster.",
           ["Challenger", "Columbia", "Atlantis", "Discovery"], "b", "Columbia broke up in 2003", "medium"),
    ],
    ("A Different Kind of School - Quiz", 6): [
        _q("Why was Miss Beam's school 'different'?",
           ["No teachers", "Each day a child pretended to have a disability", "It was online", "It was at night"], "b", "Children learned empathy through experience", "easy"),
        _q("Miss Beam's main aim was to teach:",
           ["Maths", "Kindness / empathy", "Singing", "Dance"], "b", "Empathy and care for others", "easy"),
        _q("On 'blind day' children:",
           ["Wore glasses", "Wore bandages over the eyes", "Wore hats", "Wore gloves"], "b", "To experience blindness for a day", "easy"),
    ],
    # Kannada
    ("Shishuvina Haadu - Quiz", 6): [
        _q("'Shishu' means:",
           ["Old man", "Child / baby", "Bird", "Tree"], "b", "Shishu = baby", "easy"),
        _q("'Haadu' means:",
           ["Story", "Song", "Dance", "Game"], "b", "Haadu = song", "easy"),
        _q("The poem mainly describes:",
           ["Sadness", "Innocence and joy of childhood", "Anger", "Fear"], "b", "Joy and innocence of a child", "easy"),
    ],
    ("Namma Uttara Karnataka - Quiz", 6): [
        _q("'Uttara' in Kannada means:",
           ["South", "North", "East", "West"], "b", "Uttara = north", "easy"),
        _q("Which famous river flows through North Karnataka?",
           ["Cauvery", "Krishna / Tungabhadra", "Sharavati", "Netravati"], "b", "Krishna and Tungabhadra rivers", "easy"),
        _q("Which world heritage site is in North Karnataka?",
           ["Mysuru Palace", "Hampi", "Belur", "Halebidu"], "b", "Hampi — capital of the Vijayanagara Empire", "medium"),
    ],
    ("Nanna Priya Kavi - Quiz", 6): [
        _q("'Kavi' in Kannada means:",
           ["Singer", "Poet", "Dancer", "Painter"], "b", "Kavi = poet", "easy"),
        _q("Who was the FIRST Kannada poet to receive the Jnanapeeta Award?",
           ["Kuvempu", "Da Ra Bendre", "Masti", "Karanth"], "a", "Kuvempu won in 1968", "medium"),
        _q("Kuvempu's real name was:",
           ["K V Puttappa", "K S Narasimha Swamy", "Bendre", "Pampa"], "a", "Kuppali Venkatappa Puttappa", "medium"),
    ],
}


# ─── GRADE 7 ───────────────────────────────────────────────────────────────
QUESTIONS_GRADE_7 = {
    # Maths
    ("Integers - Quiz", 7): [
        _q("What is (-5) + 3?",
           ["-8", "-2", "2", "8"], "b", "Move 3 right from -5 → -2", "easy"),
        _q("(-3) × (-4) = ?",
           ["-12", "-7", "7", "12"], "d", "Negative × negative = positive", "easy"),
        _q("Which is the additive inverse of 7?",
           ["1/7", "0", "-7", "7"], "c", "7 + (-7) = 0", "medium"),
    ],
    ("Fractions and Decimals - Quiz", 7): [
        _q("0.25 as a fraction in lowest form is:",
           ["1/4", "1/2", "2/5", "1/3"], "a", "0.25 = 25/100 = 1/4", "easy"),
        _q("1/2 × 3/4 = ?",
           ["1/8", "3/8", "4/8", "3/4"], "b", "Multiply numerators and denominators: 3/8", "easy"),
        _q("Convert 3/5 into a decimal:",
           ["0.3", "0.5", "0.6", "0.8"], "c", "3 ÷ 5 = 0.6", "medium"),
    ],
    ("Data Handling - Quiz", 7): [
        _q("The arithmetic mean of 4, 6, 8, 10 is:",
           ["6", "7", "8", "9"], "b", "(4+6+8+10) / 4 = 28/4 = 7", "easy"),
        _q("The middle value of an ordered set is the:",
           ["Mean", "Median", "Mode", "Range"], "b", "Median = middle value", "easy"),
        _q("The most frequent value is the:",
           ["Mean", "Median", "Mode", "Range"], "c", "Mode = most often", "medium"),
    ],
    ("Simple Equations - Quiz", 7): [
        _q("Solve: 2x + 5 = 13",
           ["x = 3", "x = 4", "x = 5", "x = 9"], "b", "2x = 8 → x = 4", "easy"),
        _q("Solve: x − 7 = 12",
           ["x = 5", "x = 12", "x = 19", "x = 84"], "c", "Add 7 to both sides → x = 19", "easy"),
        _q("Solve: 3(x − 2) = 9",
           ["x = 1", "x = 3", "x = 5", "x = 9"], "c", "3x − 6 = 9 → 3x = 15 → x = 5", "medium"),
    ],
    ("Lines and Angles - Quiz", 7): [
        _q("Sum of angles on a straight line:",
           ["90°", "180°", "270°", "360°"], "b", "Linear pair sums to 180°", "easy"),
        _q("Two angles whose sum is 90° are called:",
           ["Supplementary", "Complementary", "Vertically opposite", "Corresponding"], "b", "Complementary = sum 90°", "easy"),
        _q("Vertically opposite angles are:",
           ["Supplementary", "Equal", "Complementary", "Always 90°"], "b", "Vert. opp. angles are equal", "medium"),
    ],
    # Science
    ("Nutrition in Plants - Quiz", 7): [
        _q("Photosynthesis takes place in the presence of:",
           ["Moonlight", "Sunlight", "Heat only", "Water only"], "b", "Sunlight powers photosynthesis", "easy"),
        _q("Green pigment in leaves is called:",
           ["Haemoglobin", "Chlorophyll", "Melanin", "Xylem"], "b", "Chlorophyll captures light energy", "easy"),
        _q("Plants take in which gas during photosynthesis?",
           ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"], "c", "CO₂ → glucose + O₂", "medium"),
    ],
    ("Nutrition in Animals - Quiz", 7): [
        _q("Which organ produces bile?",
           ["Stomach", "Liver", "Pancreas", "Kidney"], "b", "Liver makes bile", "easy"),
        _q("Digestion of food is completed in the:",
           ["Mouth", "Stomach", "Small intestine", "Large intestine"], "c", "Final digestion in small intestine", "medium"),
        _q("The largest gland in the human body is the:",
           ["Pancreas", "Liver", "Salivary gland", "Thyroid"], "b", "Liver is the largest gland", "medium"),
    ],
    ("Fibre to Fabric - Quiz", 7): [
        _q("Wool is mainly obtained from:",
           ["Sheep", "Silkworm", "Cotton plant", "Jute plant"], "a", "Sheep's hair = wool", "easy"),
        _q("Silk thread comes from:",
           ["Cocoon of silkworm", "Sheep wool", "Cotton bolls", "Jute leaves"], "a", "Cocoon is unwound for silk", "easy"),
        _q("The process of taking out fibre from cocoons is called:",
           ["Spinning", "Reeling", "Weaving", "Knitting"], "b", "Reeling silk", "medium"),
    ],
    ("Heat - Quiz", 7): [
        _q("Heat flows from:",
           ["Cold to hot body", "Hot to cold body", "Equal bodies", "It does not flow"], "b", "Heat moves hot → cold", "easy"),
        _q("Which is the SI unit of temperature?",
           ["Joule", "Kelvin", "Newton", "Watt"], "b", "Kelvin (K) is SI unit", "easy"),
        _q("In which mode does heat travel through liquids?",
           ["Conduction", "Convection", "Radiation", "Reflection"], "b", "Convection in fluids", "medium"),
    ],
    ("Acids, Bases and Salts - Quiz", 7): [
        _q("Acids turn blue litmus paper:",
           ["Green", "Red", "Yellow", "Blue"], "b", "Acid → blue → red", "easy"),
        _q("Bases turn red litmus:",
           ["Red", "Blue", "Green", "Yellow"], "b", "Base → red → blue", "easy"),
        _q("Acid + Base →",
           ["Acid", "Base", "Salt and water", "Gas only"], "c", "Neutralisation gives salt + water", "medium"),
    ],
    # English
    ("Three Questions - Quiz", 7): [
        _q("Who is the author of the story?",
           ["Tagore", "Leo Tolstoy", "Premchand", "R K Narayan"], "b", "Russian writer Leo Tolstoy", "easy"),
        _q("The king's three questions were about:",
           ["Wealth", "Right time, right people, right thing to do", "Health", "War"], "b", "Time, people, action", "easy"),
        _q("Who finally answered all three questions for the king?",
           ["Wise scholars", "The hermit through experience", "His ministers", "His soldiers"], "b", "A simple hermit's lessons", "medium"),
    ],
    ("A Gift of Chappals - Quiz", 7): [
        _q("To whom did the children give the chappals?",
           ["Their teacher", "A barefoot beggar musician", "Their grandfather", "A neighbour"], "b", "Beggar with no shoes", "easy"),
        _q("Where is the story set?",
           ["Delhi", "Chennai (Madras)", "Mumbai", "Bengaluru"], "b", "South Indian setting", "easy"),
        _q("The story shows the value of:",
           ["Wealth", "Compassion / kindness", "Power", "Knowledge"], "b", "Helping those in need", "easy"),
    ],
    # Hindi (Vasant Bhag 2)
    ("Hum Panchi Unmukt Gagan Ke - Quiz", 7): [
        _q("'Hum Panchi Unmukt Gagan Ke' poem is about:",
           ["River", "Free birds in open sky", "Mountains", "Forest"], "b", "Birds want freedom in open sky", "easy"),
        _q("Poet of this poem is:",
           ["Premchand", "Shivmangal Singh Suman", "Tulsidas", "Surdas"], "b", "Shivmangal Singh 'Suman'", "medium"),
        _q("'Unmukt' means:",
           ["Caged", "Free / open", "Closed", "Sad"], "b", "Unmukt = free, open", "easy"),
    ],
    ("Dad Kahe So Kijiye - Quiz", 7): [
        _q("'Dad' in this lesson refers to:",
           ["Father (papa)", "An elder brother", "A teacher", "A grandfather"], "a", "Dad = papa / father", "easy"),
        _q("The lesson teaches us:",
           ["To disobey elders", "To listen to wise advice", "To be greedy", "To stay silent"], "b", "Respect and follow wise advice", "easy"),
        _q("'Kijiye' is a respectful form of:",
           ["Karo", "Kiya", "Karna", "Kara"], "a", "Polite imperative of karna", "medium"),
    ],
    ("Himalay Ki Betiyaan - Quiz", 7): [
        _q("'Betiyaan' here refers to:",
           ["Daughters", "Rivers flowing from Himalayas", "Mountains", "Forests"], "b", "Rivers like Ganga, Yamuna are called Himalaya's daughters", "medium"),
        _q("Which river is NOT a Himalayan river?",
           ["Ganga", "Yamuna", "Cauvery", "Brahmaputra"], "c", "Cauvery is South Indian", "medium"),
        _q("The poet feels Himalayan rivers are:",
           ["Lifeless", "Lively, full of energy", "Useless", "Dangerous only"], "b", "Lively and joyful", "easy"),
    ],
    ("Kathin Nishad - Quiz", 7): [
        _q("'Kathin' means:",
           ["Easy", "Difficult / hard", "Sweet", "Light"], "b", "Kathin = difficult", "easy"),
        _q("The lesson is mainly about:",
           ["A festival", "Overcoming difficulties", "Eating sweets", "Watching TV"], "b", "Theme of overcoming hardship", "easy"),
        _q("Lesson teaches us to face problems with:",
           ["Fear", "Courage and perseverance", "Anger", "Tears"], "b", "Courage and patience", "medium"),
    ],
    ("Mithai Wala - Quiz", 7): [
        _q("Who was the 'Mithaiwala'?",
           ["A rich seller", "A poor father in disguise selling sweets to children", "A king", "A beggar"], "b", "He sold sweets to feel close to children", "medium"),
        _q("Why was he different from other sellers?",
           ["Sold at very low prices", "Sang songs", "Played with children", "All of these"], "d", "All these qualities", "medium"),
        _q("The story is emotional because:",
           ["He had lost his own children", "He was very rich", "He was a king", "He was angry"], "a", "His own children had died — he sold sweets to be near children", "hard"),
    ],
    # Kannada
    ("Vachana Sahitya - Quiz", 7): [
        _q("'Vachana' literally means:",
           ["A song", "A spoken word / saying", "A dance", "A book"], "b", "Vachana = saying", "easy"),
        _q("Vachana movement leader in 12th century was:",
           ["Pampa", "Basavanna", "Kuvempu", "Bendre"], "b", "Basavanna led the Vachana movement", "medium"),
        _q("Vachanas were written mostly in:",
           ["Sanskrit", "Simple spoken Kannada", "Latin", "Tamil"], "b", "Common people's Kannada", "medium"),
    ],
    ("Purandaradasa Keertane - Quiz", 7): [
        _q("Purandaradasa is known as the father of:",
           ["Kannada literature", "Carnatic music", "Bharatanatyam", "Yoga"], "b", "Pitamaha of Carnatic music", "medium"),
        _q("He composed his songs in:",
           ["Sanskrit", "Kannada", "Tamil", "Hindi"], "b", "Devotional Kannada songs (keertanes)", "easy"),
        _q("His songs were mainly devoted to which deity?",
           ["Shiva", "Vitthala / Vishnu", "Ganesha", "Durga"], "b", "Vitthala of Pandharpur", "medium"),
    ],
    ("Karnataka Darshana - Quiz", 7): [
        _q("Capital city of Karnataka:",
           ["Mysuru", "Mangaluru", "Bengaluru", "Hubballi"], "c", "Bengaluru is capital", "easy"),
        _q("Famous waterfall in Karnataka:",
           ["Niagara", "Jog Falls", "Athirappilly", "Hogenakkal"], "b", "Jog Falls on Sharavati", "easy"),
        _q("UNESCO heritage site in Karnataka:",
           ["Hampi", "Taj Mahal", "Red Fort", "Qutub Minar"], "a", "Hampi ruins are UNESCO listed", "medium"),
    ],
}


# ─── GRADE 8 ───────────────────────────────────────────────────────────────
QUESTIONS_GRADE_8 = {
    # Maths
    ("Rational Numbers - Quiz", 8): [
        _q("Which is a rational number?",
           ["√2", "π", "3/4", "√3"], "c", "3/4 fits p/q with q ≠ 0", "easy"),
        _q("0 is:",
           ["Not a rational number", "A rational number (0/1)", "Irrational", "Imaginary"], "b", "0 = 0/1 → rational", "easy"),
        _q("Additive inverse of -5/7 is:",
           ["-7/5", "5/7", "-5/7", "7/5"], "b", "-5/7 + 5/7 = 0", "medium"),
    ],
    ("Linear Equations in One Variable - Quiz", 8): [
        _q("Solve: 2x + 5 = 13",
           ["x = 3", "x = 4", "x = 8", "x = 9"], "b", "2x = 8 → x = 4", "easy"),
        _q("Solve: 3(x − 2) = 2x + 1",
           ["x = 5", "x = 7", "x = 9", "x = 11"], "b", "3x − 6 = 2x + 1 → x = 7", "medium"),
        _q("Solve: x/4 + 1 = 5",
           ["x = 4", "x = 8", "x = 16", "x = 20"], "c", "x/4 = 4 → x = 16", "medium"),
    ],
    ("Understanding Quadrilaterals - Quiz", 8): [
        _q("Sum of interior angles of any quadrilateral?",
           ["180°", "270°", "360°", "540°"], "c", "Always 360°", "easy"),
        _q("A parallelogram with all sides equal is a:",
           ["Rectangle", "Rhombus", "Trapezium", "Kite"], "b", "Equal sides + parallel = rhombus", "easy"),
        _q("Diagonals of a rectangle:",
           ["Are unequal", "Bisect at right angles", "Are equal and bisect each other", "Do not intersect"], "c", "Equal and bisect each other", "medium"),
    ],
    ("Data Handling - Quiz", 8): [
        _q("Probability of getting a head when a fair coin is tossed:",
           ["0", "1/2", "1", "1/4"], "b", "1 of 2 outcomes", "easy"),
        _q("In a die roll, probability of getting an even number:",
           ["1/6", "1/3", "1/2", "2/3"], "c", "Evens: 2,4,6 → 3/6 = 1/2", "medium"),
        _q("Probability of an impossible event:",
           ["0", "1/2", "1", "Cannot say"], "a", "Impossible event = 0", "easy"),
    ],
    ("Squares and Square Roots - Quiz", 8): [
        _q("Square of 12:",
           ["122", "124", "144", "164"], "c", "12 × 12 = 144", "easy"),
        _q("√169 = ?",
           ["11", "12", "13", "14"], "c", "13 × 13 = 169", "easy"),
        _q("Which is a perfect square?",
           ["50", "62", "81", "90"], "c", "9² = 81", "medium"),
    ],
    # Science
    ("Crop Production and Management - Quiz", 8): [
        _q("Crops grown in winter (Oct–Mar) are called:",
           ["Kharif", "Rabi", "Zaid", "Cash crops"], "b", "Rabi = winter crops (wheat, gram)", "easy"),
        _q("Which is a kharif crop?",
           ["Wheat", "Mustard", "Rice", "Gram"], "c", "Rice grows in monsoon (kharif)", "easy"),
        _q("The process of loosening soil before sowing is:",
           ["Levelling", "Ploughing / tilling", "Irrigating", "Harvesting"], "b", "Ploughing breaks and turns soil", "medium"),
    ],
    ("Microorganisms: Friend and Foe - Quiz", 8): [
        _q("Curd is formed from milk by:",
           ["Yeast", "Lactobacillus bacteria", "Virus", "Algae"], "b", "Lactobacillus turns milk → curd", "easy"),
        _q("Bread rises because of:",
           ["Algae", "Yeast", "Bacteria", "Fungi spores"], "b", "Yeast produces CO₂", "easy"),
        _q("Which disease is caused by a virus?",
           ["Cholera", "Tuberculosis", "Common cold", "Typhoid"], "c", "Common cold is viral", "medium"),
    ],
    ("Coal and Petroleum - Quiz", 8): [
        _q("Coal, petroleum and natural gas are:",
           ["Renewable", "Fossil fuels (non-renewable)", "Solar fuels", "Bio fuels"], "b", "Formed from fossils over millions of years", "easy"),
        _q("Petroleum is refined into many products by:",
           ["Distillation (refining)", "Combustion", "Filtration", "Boiling water"], "a", "Fractional distillation", "medium"),
        _q("Which is NOT a petroleum product?",
           ["Petrol", "Diesel", "LPG", "Coal"], "d", "Coal is a separate fossil fuel", "easy"),
    ],
    ("Combustion and Flame - Quiz", 8): [
        _q("Substances which burn easily are called:",
           ["Inflammable", "Non-flammable", "Magnetic", "Acidic"], "a", "Inflammable = catches fire easily", "easy"),
        _q("The hottest part of a candle flame is:",
           ["Innermost (dark) zone", "Middle (yellow) zone", "Outer (blue) zone", "All same"], "c", "Outer zone — complete combustion", "medium"),
        _q("CNG is preferred over petrol because it:",
           ["Costs more", "Causes less pollution", "Is heavier", "Is solid"], "b", "Cleaner combustion", "easy"),
    ],
    ("Conservation of Plants - Quiz", 8): [
        _q("A protected area for animals only is called a:",
           ["National park", "Wildlife sanctuary", "Biosphere reserve", "Botanical garden"], "b", "Sanctuary protects animals", "easy"),
        _q("Cutting down forests on a large scale is called:",
           ["Afforestation", "Deforestation", "Reforestation", "Plantation"], "b", "Deforestation = removal of forests", "easy"),
        _q("A 'red data book' contains:",
           ["List of all species", "List of endangered species", "List of plants only", "List of fishes"], "b", "Records species at risk", "medium"),
    ],
    # Social Science
    ("Resources - Quiz", 8): [
        _q("Air, water and soil are which type of resources?",
           ["Human-made", "Natural", "Cultural", "Imaginary"], "b", "Found in nature", "easy"),
        _q("Coal and oil are:",
           ["Renewable", "Non-renewable", "Biotic", "Cultural"], "b", "Take millions of years to form", "easy"),
        _q("Sunlight is a ___ resource.",
           ["Non-renewable", "Renewable", "Human-made", "Limited"], "b", "Sun gives energy continuously", "easy"),
    ],
    ("Land, Soil, Water - Quiz", 8): [
        _q("The thin top layer that supports plants is:",
           ["Bedrock", "Soil", "Mantle", "Crust"], "b", "Soil is the fertile top layer", "easy"),
        _q("Soil erosion can be reduced by:",
           ["Overgrazing", "Planting trees / contour ploughing", "Cutting forests", "Removing grass"], "b", "Roots hold soil together", "medium"),
        _q("About what % of Earth's water is fresh?",
           ["About 3%", "About 25%", "About 50%", "About 70%"], "a", "Most water is salty seawater", "medium"),
    ],
    ("Mineral and Power - Quiz", 8): [
        _q("A renewable source of power is:",
           ["Coal", "Petroleum", "Solar energy", "Natural gas"], "c", "Sun is unlimited", "easy"),
        _q("Iron is a ___ metallic mineral.",
           ["Non-metallic", "Ferrous", "Non-ferrous", "Precious"], "b", "Ferrous = iron-bearing", "medium"),
        _q("Which is NOT a fossil fuel?",
           ["Coal", "Petroleum", "Natural gas", "Wind"], "d", "Wind is renewable", "easy"),
    ],
    ("Agriculture - Quiz", 8): [
        _q("Subsistence farming means:",
           ["Farming for export", "Farming mainly for own use", "Plantation farming", "Tea farming"], "b", "Grown to feed the family", "easy"),
        _q("Which is a plantation crop?",
           ["Wheat", "Rice", "Tea / Coffee", "Pulses"], "c", "Tea, coffee = plantation", "easy"),
        _q("Use of better seeds, fertilisers and irrigation is called:",
           ["Green Revolution", "Industrial Revolution", "White Revolution", "Blue Revolution"], "a", "Green Revolution boosted yields", "medium"),
    ],
    ("Industries - Quiz", 8): [
        _q("Iron and steel industry is a ___ industry.",
           ["Light", "Heavy / basic", "Agro-based", "Cottage"], "b", "Heavy industry", "easy"),
        _q("Sugar, cotton and jute are examples of:",
           ["Mineral-based industries", "Agro-based industries", "Heavy industries", "Service industries"], "b", "Use farm products as raw material", "medium"),
        _q("Jamshedpur is famous for:",
           ["Cotton textiles", "Iron and steel", "Software", "Tea"], "b", "TATA Steel plant", "easy"),
    ],
    # Hindi (Vasant Bhag 3)
    ("Dhwani - Quiz", 8): [
        _q("'Dhwani' means:",
           ["Light", "Sound / vibration", "Smell", "Taste"], "b", "Dhwani = sound", "easy"),
        _q("Poet of this poem is:",
           ["Premchand", "Suryakant Tripathi 'Nirala'", "Tulsidas", "Mira"], "b", "Suryakant Tripathi 'Nirala'", "medium"),
        _q("Theme of the poem is:",
           ["Sadness", "Hope, new beginnings of spring", "War", "Money"], "b", "Spring brings new life and hope", "easy"),
    ],
    ("Lakh Ki Chudiyan - Quiz", 8): [
        _q("'Lakh ki chudiyan' refers to:",
           ["Glass bangles", "Lac (resin) bangles", "Iron bangles", "Plastic bangles"], "b", "Made of lac/lakh", "easy"),
        _q("The bangle maker's name in the story is:",
           ["Badlu", "Birju", "Bhola", "Banshi"], "a", "Badlu was the bangle maker", "medium"),
        _q("Why did Badlu's craft decline?",
           ["He retired", "Glass and plastic bangles became popular", "He moved away", "Bangles were banned"], "b", "Modern bangles replaced lac ones", "medium"),
    ],
    ("Bus Ki Yatra - Quiz", 8): [
        _q("The lesson is a humorous account of:",
           ["A train trip", "A bus journey", "A plane ride", "A boat ride"], "b", "Funny bus journey", "easy"),
        _q("The condition of the bus was:",
           ["Brand new", "Very old and broken-down", "A racing bus", "An electric bus"], "b", "Very old, falling apart", "easy"),
        _q("The story uses ___ to make the journey funny.",
           ["Drama", "Exaggeration / humour", "Sad poetry", "Songs"], "b", "Comic exaggeration", "medium"),
    ],
    ("Deewanon Ki Hasti - Quiz", 8): [
        _q("'Deewanon Ki Hasti' is a:",
           ["Story", "Poem", "Drama", "Letter"], "b", "It is a poem", "easy"),
        _q("Poet of this poem is:",
           ["Bhagwati Charan Verma", "Premchand", "Tulsidas", "Mahadevi Verma"], "a", "Bhagwati Charan Verma", "medium"),
        _q("'Deewane' here means:",
           ["Mad / passionate free spirits", "Doctors", "Soldiers", "Farmers"], "a", "Carefree, passionate people", "medium"),
    ],
    ("Chitthiyon Ki Anoothi Duniya - Quiz", 8): [
        _q("'Chitthi' means:",
           ["Phone", "Letter", "Email", "Telegram"], "b", "Chitthi = letter", "easy"),
        _q("The lesson celebrates the importance of:",
           ["TV", "Hand-written letters", "Internet only", "Cinema"], "b", "Personal letters as treasured records", "easy"),
        _q("Which famous person was known for many letters to his daughter?",
           ["Gandhi", "Nehru", "Tagore", "Bhagat Singh"], "b", "Nehru's letters from prison to Indira", "medium"),
    ],
    # English (Honeydew)
    ("The Best Christmas Present in the World - Quiz", 8): [
        _q("Where did the narrator find the old letter?",
           ["In a library", "In a roll-top desk", "In a museum", "In an attic"], "b", "Hidden in a roll-top desk drawer", "easy"),
        _q("Who wrote the letter?",
           ["A soldier — Jim", "A teacher", "A king", "A child"], "a", "British soldier Jim, WWI", "easy"),
        _q("The letter is connected to which famous Christmas event of WWI?",
           ["Christmas truce of 1914", "End of war", "Coronation", "A wedding"], "a", "1914 Christmas truce on the Western Front", "medium"),
    ],
    ("The Tsunami - Quiz", 8): [
        _q("The tsunami in the lesson struck on:",
           ["26 Dec 2004", "11 Sep 2001", "15 Aug 1947", "26 Jan 1950"], "a", "Indian Ocean tsunami, 2004", "easy"),
        _q("Tilly Smith saved many lives because she:",
           ["Could swim", "Recognised tsunami signs from a school lesson", "Was a lifeguard", "Was a teacher"], "b", "She remembered her geography lesson", "medium"),
        _q("A tsunami is caused mainly by:",
           ["Rain", "Underwater earthquake", "Strong wind", "Tides"], "b", "Earthquake on sea floor displaces water", "easy"),
    ],
    ("Glimpses of the Past - Quiz", 8): [
        _q("The chapter is presented in the form of a:",
           ["Novel", "Comic strip with pictures", "Poem", "Drama"], "b", "Pictorial / comic-strip narrative", "easy"),
        _q("It covers Indian history from about:",
           ["1750–1857", "1947–1990", "1500–1600", "1900–1947"], "a", "British arrival to first war of independence", "medium"),
        _q("'Sepoy Mutiny / First War of Independence' was in the year:",
           ["1757", "1857", "1907", "1947"], "b", "1857 revolt", "easy"),
    ],
    # Kannada
    ("Bettadakke Hogi Baa - Quiz", 8): [
        _q("'Bettadakke' means:",
           ["To the river", "To the hill / mountain", "To the sea", "To the city"], "b", "Betta = hill", "easy"),
        _q("The lesson encourages students to:",
           ["Stay indoors", "Explore nature", "Watch TV", "Go shopping"], "b", "Enjoy and learn from nature", "easy"),
        _q("'Hogi baa' means:",
           ["Come and go", "Go and return / let's go", "Run away", "Sit down"], "b", "Invitation to go and come back", "medium"),
    ],
    ("Nanna Baalya - Quiz", 8): [
        _q("'Baalya' means:",
           ["Old age", "Childhood", "Adulthood", "Marriage"], "b", "Baalya = childhood", "easy"),
        _q("The author recalls childhood with:",
           ["Anger", "Fondness / nostalgia", "Hatred", "Boredom"], "b", "Nostalgic memories", "easy"),
        _q("This kind of writing is called:",
           ["Fiction", "Autobiography / memoir", "Drama", "Newspaper report"], "b", "Personal recollection = memoir", "medium"),
    ],
    ("Akkamahadevi Vachana - Quiz", 8): [
        _q("Akkamahadevi belonged to which century?",
           ["10th", "12th", "16th", "18th"], "b", "12th-century Kannada poet-saint", "medium"),
        _q("She was a follower of:",
           ["Vishnu", "Shiva (as Chenna Mallikarjuna)", "Buddha", "Allah"], "b", "Devotee of Lord Shiva", "medium"),
        _q("Vachana literature is famous for its:",
           ["Sanskrit verses", "Simple language and social reform", "Battle songs", "Love poems for kings"], "b", "Simple Kannada with reformist themes", "medium"),
    ],
}


# ─── GRADE 9 ───────────────────────────────────────────────────────────────
QUESTIONS_GRADE_9 = {
    # Maths
    ("Number Systems - Quiz", 9): [
        _q("Which is an irrational number?",
           ["1/2", "0.75", "√2", "-3"], "c", "√2 cannot be written as p/q", "easy"),
        _q("Real numbers = ?",
           ["Only rationals", "Only irrationals", "Rational + Irrational", "Only natural numbers"], "c", "All rationals + irrationals = reals", "medium"),
        _q("Decimal expansion of 1/3 is:",
           ["Terminating", "Non-terminating, repeating", "Non-terminating, non-repeating", "Whole number"], "b", "0.333... → repeating", "medium"),
    ],
    ("Polynomials - Quiz", 9): [
        _q("Degree of the polynomial 3x² + 5x + 7?",
           ["1", "2", "3", "0"], "b", "Highest power of x is 2", "easy"),
        _q("Which is NOT a polynomial?",
           ["x² + 1", "5x + 3", "1/x + 2", "7"], "c", "1/x has negative power → not a polynomial", "medium"),
        _q("Zero of polynomial p(x) = x − 5 is:",
           ["0", "1", "5", "-5"], "c", "p(5) = 0", "easy"),
    ],
    ("Coordinate Geometry - Quiz", 9): [
        _q("The point (3, -2) lies in which quadrant?",
           ["I", "II", "III", "IV"], "d", "x positive, y negative → Q4", "easy"),
        _q("The horizontal line is called the:",
           ["x-axis", "y-axis", "z-axis", "Origin"], "a", "x-axis is horizontal", "easy"),
        _q("Coordinates of the origin are:",
           ["(1,1)", "(0,0)", "(0,1)", "(1,0)"], "b", "Origin = (0, 0)", "easy"),
    ],
    ("Linear Equations in Two Variables - Quiz", 9): [
        _q("Standard form of a linear equation in two variables:",
           ["ax + b = 0", "ax² + bx + c = 0", "ax + by + c = 0", "ax + by = c²"], "c", "ax + by + c = 0", "easy"),
        _q("Solution of x + y = 5 when x = 2:",
           ["y = 3", "y = 5", "y = 7", "y = -3"], "a", "2 + y = 5 → y = 3", "easy"),
        _q("Graph of a linear equation in two variables is a:",
           ["Curve", "Parabola", "Straight line", "Circle"], "c", "Always a straight line", "medium"),
    ],
    ("Introduction to Euclid's Geometry - Quiz", 9): [
        _q("'A point is that which has no part' is an example of a:",
           ["Postulate", "Definition", "Theorem", "Proof"], "b", "Definition by Euclid", "easy"),
        _q("Things which are equal to the same thing are equal to one another. This is a/an:",
           ["Postulate", "Axiom", "Theorem", "Construction"], "b", "Euclid's first axiom", "medium"),
        _q("Euclid's elements has how many books?",
           ["5", "9", "13", "20"], "c", "13 books", "medium"),
    ],
    # Science
    ("Matter in Our Surroundings - Quiz", 9): [
        _q("Which is NOT a state of matter?",
           ["Solid", "Liquid", "Gas", "Energy"], "d", "Energy is not a state of matter", "easy"),
        _q("The process of solid → gas (without liquid) is called:",
           ["Melting", "Boiling", "Sublimation", "Condensation"], "c", "E.g. camphor sublimes", "easy"),
        _q("SI unit of temperature:",
           ["°C", "K (Kelvin)", "°F", "J"], "b", "Kelvin is SI unit", "medium"),
    ],
    ("Is Matter Around Us Pure? - Quiz", 9): [
        _q("A substance with only one kind of particle is:",
           ["Pure substance", "Mixture", "Solution", "Suspension"], "a", "Pure substance", "easy"),
        _q("Air is a:",
           ["Pure substance", "Compound", "Mixture", "Element"], "c", "Mixture of gases", "easy"),
        _q("Which technique separates two miscible liquids?",
           ["Filtration", "Distillation", "Hand-picking", "Magnet"], "b", "Distillation by boiling points", "medium"),
    ],
    ("Atoms and Molecules - Quiz", 9): [
        _q("Atomic mass of oxygen is:",
           ["8", "12", "16", "32"], "c", "O = 16 u", "easy"),
        _q("Molecular mass of H₂O:",
           ["16", "17", "18", "20"], "c", "2(1) + 16 = 18", "medium"),
        _q("Symbol for sodium:",
           ["So", "Sa", "Na", "S"], "c", "Na from Latin Natrium", "easy"),
    ],
    ("Structure of the Atom - Quiz", 9): [
        _q("The nucleus of an atom contains:",
           ["Only electrons", "Protons and electrons", "Protons and neutrons", "Only neutrons"], "c", "Nucleus = protons + neutrons", "easy"),
        _q("Charge on a proton is:",
           ["Negative", "Positive", "Neutral", "Variable"], "b", "Proton = positive", "easy"),
        _q("Maximum electrons in K shell:",
           ["2", "8", "18", "32"], "a", "K shell holds 2 electrons (2n² with n=1)", "medium"),
    ],
    ("The Fundamental Unit of Life - Quiz", 9): [
        _q("The basic structural and functional unit of life is the:",
           ["Atom", "Cell", "Tissue", "Organ"], "b", "Cell is the unit of life", "easy"),
        _q("Who discovered cells?",
           ["Robert Hooke", "Newton", "Einstein", "Darwin"], "a", "In 1665 in cork tissue", "easy"),
        _q("The control centre of a cell is:",
           ["Mitochondria", "Nucleus", "Ribosome", "Vacuole"], "b", "Nucleus controls cell activity", "medium"),
    ],
    # Social Science
    ("The French Revolution - Quiz", 9): [
        _q("The French Revolution began in the year:",
           ["1689", "1789", "1889", "1989"], "b", "1789 storming of Bastille", "easy"),
        _q("Slogan of the French Revolution:",
           ["Liberty, Equality, Fraternity", "Power, Wealth, Fame", "Strength, Pride, Honour", "Bread, Land, Peace"], "a", "Liberté, Égalité, Fraternité", "easy"),
        _q("The king of France during the revolution was:",
           ["Louis XIV", "Louis XV", "Louis XVI", "Napoleon"], "c", "Louis XVI was guillotined", "medium"),
    ],
    ("Socialism in Europe - Quiz", 9): [
        _q("Socialism gives importance to:",
           ["Private property", "Common ownership / public welfare", "Royalty", "Caste"], "b", "Public ownership and welfare", "easy"),
        _q("The Russian Revolution took place in the year:",
           ["1905", "1917", "1939", "1947"], "b", "October Revolution 1917", "easy"),
        _q("Lenin led which party in the revolution?",
           ["Tsarists", "Bolsheviks", "Mensheviks", "Liberals"], "b", "Bolsheviks (later Communists)", "medium"),
    ],
    # Marathi
    ("Aai - Quiz", 9): [
        _q("'Aai' means:",
           ["Father", "Mother", "Sister", "Brother"], "b", "Aai = mother in Marathi", "easy"),
        _q("The poem expresses ___ for the mother.",
           ["Anger", "Love and gratitude", "Fear", "Indifference"], "b", "Love, devotion, gratitude", "easy"),
        _q("A common image used to describe Aai is:",
           ["Selfish", "Selfless / sacrificing", "Cruel", "Lazy"], "b", "Selfless love", "easy"),
    ],
    ("Nagari Manus Gawat Yeto - Quiz", 9): [
        _q("'Nagari manus' refers to:",
           ["A villager", "A city dweller", "A farmer", "A child"], "b", "Nagar = city", "easy"),
        _q("'Gawat yeto' means:",
           ["Goes to school", "Comes to the village", "Goes to work", "Sleeps at home"], "b", "Coming to the village", "medium"),
        _q("The lesson contrasts:",
           ["Day and night", "City and village life", "Past and future", "Rich and poor only"], "b", "Urban vs rural life", "medium"),
    ],
    ("Marathi Bana - Quiz", 9): [
        _q("'Bana' here means:",
           ["Forest", "Pride / nature", "River", "Mountain"], "b", "Bana = pride / character", "medium"),
        _q("Lesson promotes:",
           ["Foreign culture", "Marathi pride and culture", "Money", "Power"], "b", "Pride in Marathi heritage", "easy"),
        _q("Marathi is the official language of:",
           ["Goa", "Maharashtra", "Gujarat", "Karnataka"], "b", "Maharashtra", "easy"),
    ],
    ("Swapna Banatat - Quiz", 9): [
        _q("'Swapna' means:",
           ["Hunger", "Dream", "Sleep", "Fear"], "b", "Swapna = dream", "easy"),
        _q("The poem encourages us to:",
           ["Forget dreams", "Dream big and work for them", "Sleep more", "Fear the future"], "b", "Have dreams and pursue them", "easy"),
        _q("'Banatat' is the verb for:",
           ["To break", "To make / become", "To run", "To eat"], "b", "Banane = to make/become", "medium"),
    ],
    # English (Beehive)
    ("The Fun They Had - Quiz", 9): [
        _q("Author of 'The Fun They Had':",
           ["Ruskin Bond", "Isaac Asimov", "Mark Twain", "O Henry"], "b", "Isaac Asimov, sci-fi writer", "easy"),
        _q("In the story, schools of the future have:",
           ["Many teachers", "Mechanical / robot teachers at home", "No teachers at all", "Online classes"], "b", "Each child has a mechanical teacher at home", "easy"),
        _q("Margie hated school because:",
           ["It was easy", "Lessons were given by a robot teacher she disliked", "She had no friends", "It was far"], "b", "She disliked her mechanical teacher", "medium"),
    ],
    ("The Sound of Music - Quiz", 9): [
        _q("The chapter is about Evelyn Glennie who is a:",
           ["Painter", "Deaf percussionist (musician)", "Dancer", "Cricketer"], "b", "She is a deaf solo percussionist", "easy"),
        _q("Bismillah Khan was famous for playing the:",
           ["Sitar", "Tabla", "Shehnai", "Flute"], "c", "Shehnai maestro", "easy"),
        _q("Bismillah Khan played shehnai at the Red Fort on:",
           ["15 Aug 1947", "26 Jan 1950", "26 Jan 1947", "15 Aug 1948"], "a", "First Independence Day", "medium"),
    ],
    ("The Little Girl - Quiz", 9): [
        _q("Author of 'The Little Girl':",
           ["Premchand", "Katherine Mansfield", "R K Narayan", "O Henry"], "b", "Katherine Mansfield, NZ writer", "medium"),
        _q("Kezia was afraid of her:",
           ["Mother", "Father", "Grandmother", "Brother"], "b", "She feared her stern father", "easy"),
        _q("Kezia's view of her father changed when:",
           ["He bought her a toy", "He stayed near her when she was sick / scared", "He scolded her", "He went away"], "b", "She saw his caring side", "medium"),
    ],
    ("A Truly Beautiful Mind - Quiz", 9): [
        _q("The lesson is about:",
           ["Newton", "Albert Einstein", "Darwin", "Tesla"], "b", "Einstein's life", "easy"),
        _q("Einstein's most famous equation:",
           ["F = ma", "E = mc²", "V = IR", "PV = nRT"], "b", "E = mc² (mass–energy equivalence)", "easy"),
        _q("Einstein won the Nobel Prize in:",
           ["Chemistry", "Physics", "Peace", "Literature"], "b", "Physics, 1921", "medium"),
    ],
}


# ─── GRADE 10 ──────────────────────────────────────────────────────────────
QUESTIONS_GRADE_10 = {
    # Maths
    ("Real Numbers - Quiz", 10): [
        _q("HCF × LCM of two numbers equals:",
           ["Their sum", "Their product", "Their difference", "1"], "b", "HCF × LCM = product of numbers", "easy"),
        _q("HCF of 6 and 20 by Euclid's algorithm:",
           ["1", "2", "3", "6"], "b", "20 = 6×3+2; 6 = 2×3+0 → HCF=2", "medium"),
        _q("√2 is a/an:",
           ["Rational number", "Irrational number", "Integer", "Whole number"], "b", "Cannot be written as p/q", "easy"),
    ],
    ("Polynomials - Quiz", 10): [
        _q("Degree of 4x³ − 2x + 7?",
           ["1", "2", "3", "4"], "c", "Highest power = 3", "easy"),
        _q("Sum of zeroes of x² − 5x + 6 is:",
           ["-5", "5", "6", "-6"], "b", "−b/a = −(−5)/1 = 5", "medium"),
        _q("Product of zeroes of x² − 5x + 6 is:",
           ["5", "6", "-6", "-5"], "b", "c/a = 6/1 = 6", "medium"),
    ],
    ("Pair of Linear Equations - Quiz", 10): [
        _q("If two lines have a unique solution, the pair is:",
           ["Inconsistent", "Consistent and dependent", "Consistent and independent", "Parallel"], "c", "Intersecting lines = unique solution", "medium"),
        _q("Lines x + y = 5 and 2x + 2y = 10 are:",
           ["Intersecting", "Parallel", "Coincident (same line)", "Perpendicular"], "c", "Second is just 2 × first", "medium"),
        _q("Solve x + y = 7, x − y = 1:",
           ["x=4, y=3", "x=5, y=2", "x=3, y=4", "x=6, y=1"], "a", "Adding: 2x=8 → x=4; y=3", "easy"),
    ],
    ("Quadratic Equations - Quiz", 10): [
        _q("Standard form of a quadratic equation:",
           ["ax + b = 0", "ax² + bx + c = 0", "ax + by + c = 0", "ax³ + b = 0"], "b", "ax² + bx + c = 0, a ≠ 0", "easy"),
        _q("Discriminant of ax² + bx + c is:",
           ["b² + 4ac", "b² − 4ac", "4ac − b²", "2b − ac"], "b", "D = b² − 4ac", "easy"),
        _q("Roots of x² − 5x + 6 = 0 are:",
           ["2 and 3", "1 and 6", "-2 and -3", "0 and 5"], "a", "(x−2)(x−3) = 0", "medium"),
    ],
    ("Arithmetic Progressions - Quiz", 10): [
        _q("Common difference of 3, 7, 11, 15... is:",
           ["3", "4", "7", "11"], "b", "7 - 3 = 4", "easy"),
        _q("nth term of an AP is:",
           ["a + nd", "a + (n-1)d", "a + (n+1)d", "an + d"], "b", "aₙ = a + (n−1)d", "easy"),
        _q("Sum of first n terms (AP):",
           ["n/2 [2a + (n-1)d]", "n[a + d]", "(a + d)n", "a + nd"], "a", "Sₙ = n/2 [2a + (n−1)d]", "medium"),
    ],
    # Science
    ("Chemical Reactions and Equations - Quiz", 10): [
        _q("Balanced chemical equation obeys the law of:",
           ["Conservation of mass", "Conservation of energy", "Gravity", "Motion"], "a", "Mass is conserved", "easy"),
        _q("Rusting of iron is an example of:",
           ["Combination reaction", "Displacement reaction", "Oxidation reaction", "Reduction reaction"], "c", "Iron + oxygen → iron oxide", "medium"),
        _q("In 2H₂ + O₂ → 2H₂O, the substance reduced is:",
           ["H₂", "O₂", "H₂O", "Nothing"], "b", "Oxygen gains electrons (reduced)", "medium"),
    ],
    ("Acids, Bases and Salts - Quiz", 10): [
        _q("pH of a neutral solution at 25°C is:",
           ["0", "7", "10", "14"], "b", "Pure water = pH 7", "easy"),
        _q("Acids release ___ ions in water.",
           ["OH⁻", "H⁺ (H₃O⁺)", "Na⁺", "Cl⁻"], "b", "Acids → H⁺ ions", "easy"),
        _q("Common name of NaHCO₃:",
           ["Washing soda", "Baking soda", "Bleaching powder", "Plaster of Paris"], "b", "Baking soda = NaHCO₃", "medium"),
    ],
    ("Metals and Non-metals - Quiz", 10): [
        _q("Which is the most reactive metal?",
           ["Iron", "Copper", "Sodium", "Gold"], "c", "Sodium is highly reactive", "easy"),
        _q("Non-metals are generally:",
           ["Good conductors", "Bad conductors of electricity", "Magnetic", "Lustrous"], "b", "Most non-metals do NOT conduct electricity", "easy"),
        _q("Which non-metal conducts electricity?",
           ["Sulphur", "Phosphorus", "Graphite (carbon)", "Iodine"], "c", "Graphite is a conducting non-metal", "medium"),
    ],
    ("Carbon and its Compounds - Quiz", 10): [
        _q("Number of valence electrons of carbon:",
           ["2", "3", "4", "6"], "c", "Carbon = 4 valence electrons", "easy"),
        _q("Methane (CH₄) has how many C–H bonds?",
           ["2", "3", "4", "5"], "c", "Tetrahedral, 4 bonds", "easy"),
        _q("Ethanol's chemical formula:",
           ["CH₄", "C₂H₅OH", "CH₃COOH", "C₆H₁₂O₆"], "b", "C₂H₅OH = ethanol", "medium"),
    ],
    ("Life Processes - Quiz", 10): [
        _q("In humans, oxygen is carried by:",
           ["Plasma", "Haemoglobin in RBCs", "WBCs", "Platelets"], "b", "Haemoglobin in red blood cells", "easy"),
        _q("Photosynthesis happens in:",
           ["Mitochondria", "Chloroplasts", "Nucleus", "Ribosomes"], "b", "Chloroplasts contain chlorophyll", "easy"),
        _q("The basic unit of the kidney is:",
           ["Neuron", "Nephron", "Alveolus", "Villi"], "b", "Nephron filters blood", "medium"),
    ],
    # Kannada
    ("Jnanapeeta Puraskrutha Lekhakaru - Quiz", 10): [
        _q("First Kannada writer to receive the Jnanapeetha award:",
           ["Kuvempu", "Bendre", "Karanth", "Masti"], "a", "Kuvempu, 1968", "medium"),
        _q("How many Kannada writers have won the Jnanapeetha?",
           ["Five", "Six", "Eight", "Ten"], "c", "Eight Kannada Jnanapeetha laureates", "hard"),
        _q("Da Ra Bendre received Jnanapeetha for:",
           ["Naaku Tanti", "Yayati", "Karvalo", "Avalokana"], "a", "'Naaku Tanti' (1973)", "medium"),
    ],
    ("Karnataka Ekikarana - Quiz", 10): [
        _q("Karnataka was unified on:",
           ["1 Nov 1956", "15 Aug 1947", "26 Jan 1950", "1 Nov 1973"], "a", "States Reorganisation, 1 Nov 1956", "easy"),
        _q("The official name 'Karnataka' was adopted on:",
           ["1 Nov 1956", "1 Nov 1973", "15 Aug 1947", "26 Jan 1950"], "b", "1973 — earlier 'Mysore State'", "medium"),
        _q("'Ekikarana' means:",
           ["Division", "Unification", "Independence", "Revolution"], "b", "Eki + karana = unification", "easy"),
    ],
    ("Dheera Naari Abbakka Rani - Quiz", 10): [
        _q("Abbakka Rani fought against the:",
           ["British", "Mughals", "Portuguese", "French"], "c", "Portuguese in coastal Karnataka", "medium"),
        _q("She ruled which kingdom?",
           ["Vijayanagara", "Ullala (near Mangaluru)", "Mysuru", "Belur"], "b", "Ullala on Karnataka coast", "medium"),
        _q("'Dheera' means:",
           ["Lazy", "Brave / fearless", "Sad", "Weak"], "b", "Dheera = brave", "easy"),
    ],
    ("Kavirajamarga - Quiz", 10): [
        _q("Kavirajamarga is the earliest available work in:",
           ["Tamil", "Kannada (literary criticism)", "Sanskrit", "Telugu"], "b", "Earliest Kannada work on poetics", "medium"),
        _q("It was composed during the rule of:",
           ["Hoysalas", "Rashtrakutas (King Nrupatunga)", "Cholas", "Mughals"], "b", "Rashtrakuta King Amoghavarsha I (Nrupatunga)", "hard"),
        _q("Kavirajamarga belongs to which century?",
           ["6th", "9th", "12th", "15th"], "b", "9th century CE", "medium"),
    ],
    ("Manushyatvada Gaana - Quiz", 10): [
        _q("'Manushyatva' means:",
           ["Wealth", "Humanity / human values", "Power", "Fame"], "b", "Quality of being human", "easy"),
        _q("The lesson urges everyone to be:",
           ["Greedy", "Humane and compassionate", "Selfish", "Aggressive"], "b", "Practise humanity above all", "easy"),
        _q("'Gaana' here means:",
           ["Story", "Song / hymn", "Speech", "Letter"], "b", "Gaana = song", "easy"),
    ],
    # English (First Flight)
    ("A Letter to God - Quiz", 10): [
        _q("Lencho was a/an:",
           ["Doctor", "Farmer", "Soldier", "Teacher"], "b", "Lencho was a farmer", "easy"),
        _q("Lencho's crops were destroyed by:",
           ["A flood", "A hailstorm", "Locusts", "A fire"], "b", "Hailstorm wiped out his fields", "easy"),
        _q("Lencho thought the post-office workers were:",
           ["Honest", "A bunch of crooks", "Generous", "Friends"], "b", "He believed they stole part of God's money", "medium"),
    ],
    ("Nelson Mandela: Long Walk to Freedom - Quiz", 10): [
        _q("Nelson Mandela led the freedom movement in:",
           ["India", "USA", "South Africa", "Kenya"], "c", "Anti-apartheid movement, South Africa", "easy"),
        _q("Mandela became president of South Africa in:",
           ["1990", "1994", "1999", "2004"], "b", "1994 first multiracial election", "medium"),
        _q("He spent how many years in prison?",
           ["10", "27", "30", "5"], "b", "27 years before release in 1990", "medium"),
    ],
    ("Two Stories about Flying - Quiz", 10): [
        _q("Story 1 'His First Flight' is about a:",
           ["Pilot", "Young seagull afraid to fly", "Plane crash", "Bird-watcher"], "b", "Young seagull learning to fly", "easy"),
        _q("In 'The Black Aeroplane' the pilot was helped by a:",
           ["Lighthouse", "Mysterious black aeroplane", "Friend", "Radio"], "b", "Mysterious aeroplane led him through storm", "easy"),
        _q("How did the seagull finally take off?",
           ["His parents pushed him", "Hunger forced him to fly to fish offered by mother", "He fell asleep", "He climbed a cliff"], "b", "Hunger drove him to fly for food", "medium"),
    ],
}


QUESTION_BANK = {
    **QUESTIONS_GRADE_5,
    **QUESTIONS_GRADE_6,
    **QUESTIONS_GRADE_7,
    **QUESTIONS_GRADE_8,
    **QUESTIONS_GRADE_9,
    **QUESTIONS_GRADE_10,
}


# ─── command ───────────────────────────────────────────────────────────────
class Command(BaseCommand):
    help = "Replace placeholder quiz questions with real curriculum questions."

    def handle(self, *args, **options):
        replaced = 0
        skipped = 0
        unmatched = []

        for quiz in Quiz.objects.all().order_by('grade', 'subject', 'title'):
            key = (quiz.title, quiz.grade)
            if key not in QUESTION_BANK:
                unmatched.append(f"G{quiz.grade} {quiz.subject}: {quiz.title}")
                continue

            placeholder_qs = quiz.questions.filter(question_text__startswith="Sample question")
            if not placeholder_qs.exists() and quiz.questions.exists():
                # Already has real questions — leave them alone
                skipped += 1
                continue

            placeholder_qs.delete()

            for qdata in QUESTION_BANK[key]:
                Question.objects.create(
                    quiz=quiz,
                    question_text=qdata["text"],
                    options_json=qdata["options"],
                    correct_answer=qdata["correct"],
                    explanation=qdata.get("explanation", ""),
                    difficulty=qdata.get("difficulty", "medium"),
                    marks=1,
                )

            quiz.num_questions = len(QUESTION_BANK[key])
            quiz.save(update_fields=["num_questions"])
            replaced += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nReplaced placeholder questions in {replaced} quizzes."
        ))
        if skipped:
            self.stdout.write(f"  Skipped {skipped} quizzes (already had real questions).")
        if unmatched:
            self.stdout.write(self.style.WARNING(
                f"  No question bank entry for {len(unmatched)} quizzes:"
            ))
            for t in unmatched[:30]:
                self.stdout.write(f"    - {t}")
            if len(unmatched) > 30:
                self.stdout.write(f"    ... and {len(unmatched) - 30} more")
