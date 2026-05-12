"""
python manage.py seed_more_questions

Adds 3 more curriculum questions to every existing quiz across all 10
grades, on top of what seed_questions / seed_lower_grades / seed_extra_quizzes
already produced.

Idempotent: uses get_or_create on (quiz, question_text), so re-running
will not duplicate questions.
"""
from django.core.management.base import BaseCommand
from quizzes.models import Quiz, Question


def _q(text, opts, correct, explanation="", difficulty="medium"):
    return {
        "text": text,
        "options": [{"key": k, "text": v} for k, v in zip(["a", "b", "c", "d"], opts)],
        "correct": correct,
        "explanation": explanation,
        "difficulty": difficulty,
    }


# (quiz_title, grade) -> [extra question dicts]
EXTRA_GRADE_1 = {
    ("Numbers 1 to 9 - Quiz", 1): [
        _q("How many legs does a dog have?", ["2", "3", "4", "5"], "c", "Dog has 4 legs", "easy"),
        _q("Number that comes before 8:", ["6", "7", "9", "10"], "b", "7 is before 8", "easy"),
        _q("Show 'three' fingers means how many?", ["1", "2", "3", "4"], "c", "Three = 3", "easy"),
    ],
    ("Numbers 10 to 20 - Quiz", 1): [
        _q("Which is bigger: 15 or 12?", ["15", "12", "Same", "Cannot tell"], "a", "15 > 12", "easy"),
        _q("16 is just before:", ["14", "15", "17", "18"], "c", "Next number is 17", "easy"),
        _q("Count: 18, 19, ___ ?", ["17", "20", "21", "22"], "b", "After 19 is 20", "easy"),
    ],
    ("Addition - Quiz", 1): [
        _q("3 + 6 = ?", ["7", "8", "9", "10"], "c", "3 + 6 = 9", "easy"),
        _q("5 + 0 = ?", ["0", "1", "5", "10"], "c", "Adding 0 keeps the number same", "easy"),
        _q("If 2 birds join 4 birds on a branch, total =", ["4", "5", "6", "7"], "c", "2 + 4 = 6", "easy"),
    ],
    ("A Happy Child - Quiz", 1): [
        _q("The child in the poem feels:", ["Bored", "Cheerful and content", "Hungry", "Lost"], "b", "He is happy with simple things", "easy"),
        _q("The poem describes the child's:", ["Robot", "Home and surroundings", "Aliens", "Spaceship"], "b", "House, garden, sky etc", "easy"),
        _q("'A Happy Child' helps us learn:", ["To be sad", "To enjoy small things", "To fight", "To run away"], "b", "Joy in small things", "easy"),
    ],
    ("Three Little Pigs - Quiz", 1): [
        _q("Pig 2 built his house from:", ["Straw", "Sticks/wood", "Bricks", "Glass"], "b", "Sticks/wood", "easy"),
        _q("Why did the wolf fail at the brick house?", ["He was too tired", "Bricks were too strong to blow down", "Pigs ran away", "It started raining"], "b", "Brick is strong", "easy"),
        _q("Moral of the story:", ["Be lazy", "Hard work pays off", "Run from problems", "Trust strangers"], "b", "Pig 3 worked hardest and was safe", "easy"),
    ],
    ("After a Bath - Quiz", 1): [
        _q("Soap is used while bathing to:", ["Make us dirty", "Clean germs and dirt", "Smell bad", "Dry clothes"], "b", "Soap removes germs and dirt", "easy"),
        _q("How often should we bathe?", ["Once a year", "Daily", "Once a month", "Never"], "b", "Daily bath is healthy", "easy"),
        _q("After bath we should also:", ["Wear dirty clothes", "Wear clean clothes", "Skip food", "Run in mud"], "b", "Clean clothes after bath", "easy"),
    ],
    ("My Body - Quiz", 1): [
        _q("We chew food using our:", ["Eyes", "Teeth", "Ears", "Hair"], "b", "Teeth chew food", "easy"),
        _q("How many fingers and thumbs total on both hands?", ["8", "10", "12", "20"], "b", "5 + 5 = 10", "easy"),
        _q("We see with our:", ["Ears", "Eyes", "Mouth", "Nose"], "b", "Eyes are for seeing", "easy"),
    ],
    ("My Family - Quiz", 1): [
        _q("Mother's brother is your:", ["Uncle (mama)", "Cousin", "Father", "Aunt"], "a", "Mother's brother = mama/uncle", "easy"),
        _q("Father's sister is your:", ["Sister", "Aunt (bua/atti)", "Cousin", "Niece"], "b", "Father's sister = aunt", "easy"),
        _q("A family without grandparents living together is called:", ["Joint family", "Nuclear / small family", "Big family", "Distant family"], "b", "Nuclear family", "medium"),
    ],
    ("Animals Around Us - Quiz", 1): [
        _q("A baby cow is called a:", ["Puppy", "Calf", "Kitten", "Foal"], "b", "Baby cow = calf", "easy"),
        _q("Birds use their ___ to eat:", ["Wings", "Beaks", "Tails", "Feet"], "b", "Beaks pick food", "easy"),
        _q("Which animal carries its baby in a pouch?", ["Cow", "Kangaroo", "Dog", "Horse"], "b", "Kangaroo has a pouch", "medium"),
    ],
    ("Aksharagalu - Quiz", 1): [
        _q("How many consonants (vyanjanagalu) in Kannada?", ["20", "25", "34", "40"], "c", "About 34 consonants", "medium"),
        _q("ಕ in Kannada is pronounced:", ["ka", "ga", "cha", "ta"], "a", "ಕ = ka", "easy"),
        _q("ಮ is pronounced:", ["ma", "na", "pa", "ya"], "a", "ಮ = ma", "easy"),
    ],
    ("Bannagalu (Colours) - Quiz", 1): [
        _q("'Belli bannada' means ___ colour:", ["Black", "Silver", "Gold", "Brown"], "b", "Belli = silver", "medium"),
        _q("'Kappu' is which colour?", ["White", "Black", "Yellow", "Red"], "b", "Kappu = black", "easy"),
        _q("'Bilibanna / Bili' means:", ["White", "Yellow", "Green", "Pink"], "a", "Bili = white", "easy"),
    ],
    ("Praaningalu (Animals) - Quiz", 1): [
        _q("'Aane' means:", ["Lion", "Elephant", "Camel", "Goat"], "b", "Aane = elephant", "easy"),
        _q("'Kudure' means:", ["Horse", "Donkey", "Camel", "Bull"], "a", "Kudure = horse", "easy"),
        _q("'Mola' means:", ["Mouse / hare", "Lion", "Bear", "Tiger"], "a", "Mola = hare/rabbit", "medium"),
    ],
    ("Subtraction - Quiz", 1): [
        _q("7 − 3 = ?", ["3", "4", "5", "6"], "b", "7 − 3 = 4", "easy"),
        _q("10 − 0 = ?", ["0", "1", "10", "11"], "c", "Subtracting 0 keeps it same", "easy"),
        _q("If 6 balloons and 2 burst, how many left?", ["3", "4", "5", "6"], "b", "6 − 2 = 4", "easy"),
    ],
    ("Shapes - Quiz", 1): [
        _q("A rectangle has how many sides?", ["3", "4", "5", "6"], "b", "Rectangle = 4 sides", "easy"),
        _q("A 'star' shape has how many points usually?", ["3", "4", "5", "10"], "c", "5-pointed star is most common", "easy"),
        _q("Which shape can roll easily?", ["Square", "Triangle", "Circle", "Rectangle"], "c", "Circles roll", "easy"),
    ],
    ("One Little Kitten - Quiz", 1): [
        _q("Kittens have:", ["Feathers", "Fur", "Scales", "Shells"], "b", "Cats are covered in fur", "easy"),
        _q("Kittens say:", ["Bow-wow", "Meow", "Moo", "Quack"], "b", "Cats say meow", "easy"),
        _q("The poem makes us feel:", ["Sad", "Loving / cute", "Angry", "Scared"], "b", "Kittens are cute", "easy"),
    ],
    ("Birds Around Us - Quiz", 1): [
        _q("Which bird is famous for its colourful feathers and dance?", ["Crow", "Peacock", "Sparrow", "Owl"], "b", "Peacock is colourful", "easy"),
        _q("Owls are usually active at:", ["Day", "Night", "Both", "Never"], "b", "Owls are nocturnal", "medium"),
        _q("Which bird cannot fly?", ["Eagle", "Pigeon", "Penguin", "Sparrow"], "c", "Penguins swim, do not fly", "medium"),
    ],
}


EXTRA_GRADE_2 = {
    ("What is Long, What is Round? - Quiz", 2): [
        _q("Which of these is long?", ["Coin", "Rope", "Ring", "Egg"], "b", "Rope is long", "easy"),
        _q("Which is round?", ["Door", "Coin", "Pencil", "Ladder"], "b", "Coin is round", "easy"),
        _q("Wheel of a bus is:", ["Square", "Round", "Triangle", "Long line"], "b", "Wheels are round", "easy"),
    ],
    ("Counting in Groups - Quiz", 2): [
        _q("Skip count by 5: 5, 10, 15, ?", ["18", "20", "25", "30"], "b", "Add 5 → 20", "easy"),
        _q("How many tens make 50?", ["3", "4", "5", "6"], "c", "10 × 5 = 50", "easy"),
        _q("4 + 4 + 4 = ?", ["8", "10", "12", "16"], "c", "Three 4s = 12", "easy"),
    ],
    ("Addition and Subtraction - Quiz", 2): [
        _q("25 + 14 = ?", ["29", "39", "41", "45"], "b", "25 + 14 = 39", "easy"),
        _q("50 − 23 = ?", ["17", "27", "37", "47"], "b", "50 − 23 = 27", "easy"),
        _q("Which sign means take away?", ["+", "−", "×", "÷"], "b", "Minus = subtraction", "easy"),
    ],
    ("First Day at School - Quiz", 2): [
        _q("On the first day, the teacher usually:", ["Scolds the child", "Welcomes new students", "Sends them home", "Punishes them"], "b", "Welcoming environment", "easy"),
        _q("New friends at school help us feel:", ["Lonely", "Comfortable / happy", "Angry", "Tired"], "b", "Friends ease nervousness", "easy"),
        _q("In school we should be:", ["Rude", "Polite and respectful", "Lazy", "Loud"], "b", "Politeness is important", "easy"),
    ],
    ("I am Lucky - Quiz", 2): [
        _q("If the speaker were a butterfly, they would:", ["Fly with colourful wings", "Stay in a pond", "Dig holes", "Live underwater"], "a", "Butterflies fly with wings", "easy"),
        _q("The poem celebrates:", ["Wealth", "Diversity of creatures", "School only", "Toys"], "b", "Many creatures, each special", "medium"),
        _q("'Lucky' means feeling:", ["Unhappy", "Fortunate / blessed", "Sleepy", "Hungry"], "b", "Fortunate", "easy"),
    ],
    ("Mr. Nobody - Quiz", 2): [
        _q("Mr. Nobody is blamed for:", ["Doing chores", "Breaking and spilling things", "Cooking food", "Reading books"], "b", "Mishaps in the house", "easy"),
        _q("Mr. Nobody represents:", ["A real visitor", "An imaginary scapegoat children invent", "A teacher", "A pet"], "b", "Imaginary excuse", "medium"),
        _q("Real lesson of the poem:", ["Blame others", "Own up to your mistakes", "Hide always", "Stay silent"], "b", "Take responsibility", "medium"),
    ],
    ("Plants Around Us - Quiz", 2): [
        _q("A plant's food is made in its:", ["Roots", "Leaves", "Flowers", "Soil"], "b", "Leaves do photosynthesis", "easy"),
        _q("Which is a fruit-bearing tree?", ["Pine", "Mango", "Cactus", "Bamboo"], "b", "Mango trees give fruit", "easy"),
        _q("Plants release ___ during photosynthesis:", ["CO₂", "O₂ (oxygen)", "Helium", "Smoke"], "b", "Plants release oxygen", "medium"),
    ],
    ("Animals - Quiz", 2): [
        _q("Animals that fly mostly are:", ["Fish", "Birds and insects", "Reptiles", "Whales"], "b", "Birds and insects fly", "easy"),
        _q("A camel can survive in deserts because it:", ["Has gills", "Stores fat in its hump", "Has wings", "Hibernates"], "b", "Hump stores fat for energy", "medium"),
        _q("Animals that come out only at night are called:", ["Diurnal", "Nocturnal", "Aquatic", "Aerial"], "b", "Nocturnal = active at night", "medium"),
    ],
    ("Water - Quiz", 2): [
        _q("We must drink at least ___ glasses of water daily:", ["1 or 2", "6 to 8", "20", "None"], "b", "About 6-8 glasses recommended", "easy"),
        _q("Water boils at:", ["50°C", "75°C", "100°C", "200°C"], "c", "Water boils at 100°C", "medium"),
        _q("Source of clean water at home:", ["Pond", "Tap with treated water / filter", "Drain", "Puddle"], "b", "Treated tap water/filter", "easy"),
    ],
    ("Hannugalu (Fruits) - Quiz", 2): [
        _q("'Drakshi' is which fruit?", ["Banana", "Grapes", "Pomegranate", "Apple"], "b", "Drakshi = grapes", "easy"),
        _q("'Dalimba' is:", ["Pomegranate", "Mango", "Banana", "Apple"], "a", "Dalimba = pomegranate", "easy"),
        _q("'Tenginkayi' is:", ["Lemon", "Coconut", "Tamarind", "Sapota"], "b", "Tengin = coconut", "medium"),
    ],
    ("Tarakaarigalu (Vegetables) - Quiz", 2): [
        _q("'Carrot' in Kannada:", ["Gajjari", "Meerchi", "Kosu", "Bende"], "a", "Gajjari = carrot", "easy"),
        _q("'Bende' is:", ["Brinjal", "Lady's finger / okra", "Cabbage", "Potato"], "b", "Bende = okra", "easy"),
        _q("'Kosu' is:", ["Cabbage", "Cauliflower", "Onion", "Tomato"], "a", "Kosu = cabbage", "easy"),
    ],
    ("Naadina Geethe - Quiz", 2): [
        _q("Author of Karnataka's state anthem:", ["Bendre", "Kuvempu", "Karanth", "Pampa"], "b", "Kuvempu wrote 'Jaya Bharata Jananiya Tanujate'", "medium"),
        _q("National song of India:", ["Jana Gana Mana", "Vande Mataram", "Saare Jahan Se Achha", "Jai Hind"], "b", "Vande Mataram", "easy"),
        _q("National anthem composer:", ["Tagore", "Kabir", "Tulsidas", "Mira"], "a", "Rabindranath Tagore", "easy"),
    ],
    ("Patterns - Quiz", 2): [
        _q("Continue: 1, 3, 5, 7, ?", ["8", "9", "10", "11"], "b", "Odd numbers, +2", "easy"),
        _q("Pattern: ★ ◆ ★ ◆ ★ ?", ["★", "◆", "○", "△"], "b", "Star, diamond, alternating", "easy"),
        _q("Continue: 100, 90, 80, 70, ?", ["50", "60", "75", "80"], "b", "Subtract 10", "easy"),
    ],
    ("Time - Quiz", 2): [
        _q("How many days in February (non-leap)?", ["28", "29", "30", "31"], "a", "Normally 28 days", "medium"),
        _q("First month of the year:", ["December", "January", "March", "June"], "b", "January", "easy"),
        _q("Day after Sunday is:", ["Saturday", "Friday", "Monday", "Tuesday"], "c", "Monday follows Sunday", "easy"),
    ],
    ("Storm in the Garden - Quiz", 2): [
        _q("Strong winds in a storm can:", ["Be quiet", "Bend trees and break branches", "Make plants grow taller", "Build houses"], "b", "Wind damages trees", "easy"),
        _q("After heavy rain, gardens have:", ["No water", "Puddles and wet soil", "Snow only", "Dust everywhere"], "b", "Wet ground after rain", "easy"),
        _q("Lightning during a storm should make us:", ["Stay outside", "Go indoors safely", "Climb trees", "Run in fields"], "b", "Indoors is safe", "medium"),
    ],
    ("Things We Wear - Quiz", 2): [
        _q("During rain we use a/an:", ["Sweater", "Umbrella / raincoat", "Sunglasses", "Slippers"], "b", "Protects from rain", "easy"),
        _q("Sandals are used in:", ["Snow", "Hot weather", "Heavy rain", "Floods"], "b", "Sandals keep feet cool", "easy"),
        _q("People in cold places wear:", ["Cotton clothes", "Layers of warm woollen clothes", "No clothes", "Swimsuits"], "b", "Wool retains heat", "easy"),
    ],
}


EXTRA_GRADE_3 = {
    ("Numbers 100 to 1000 - Quiz", 3): [
        _q("Number after 599 is:", ["598", "600", "699", "601"], "b", "599 + 1 = 600", "easy"),
        _q("Largest 3-digit number:", ["100", "999", "1000", "100000"], "b", "All 9s", "easy"),
        _q("Place value of 7 in 472:", ["7", "70", "700", "47"], "b", "Tens place", "medium"),
    ],
    ("Give and Take (Subtraction) - Quiz", 3): [
        _q("125 − 78 = ?", ["37", "47", "57", "67"], "b", "125 − 78 = 47", "medium"),
        _q("If a pencil costs ₹15, change from ₹50 is:", ["₹15", "₹25", "₹35", "₹45"], "c", "50 − 15 = 35", "easy"),
        _q("999 − 1 = ?", ["888", "989", "998", "997"], "c", "999 − 1 = 998", "easy"),
    ],
    ("Multiplication - Quiz", 3): [
        _q("8 × 9 = ?", ["64", "72", "81", "90"], "b", "8 × 9 = 72", "easy"),
        _q("6 × 0 = ?", ["0", "1", "6", "12"], "a", "Anything × 0 = 0", "easy"),
        _q("If 1 box has 12 pencils, 5 boxes have:", ["50", "55", "60", "65"], "c", "5 × 12 = 60", "medium"),
    ],
    ("Good Morning - Quiz", 3): [
        _q("Sunrise is in the:", ["West", "East", "North", "South"], "b", "Sun rises in the east", "easy"),
        _q("In the poem, mornings bring a feeling of:", ["Tiredness", "Freshness and joy", "Sadness", "Anger"], "b", "Morning is fresh", "easy"),
        _q("Greeting 'Good morning' shows:", ["Rudeness", "Politeness", "Anger", "Fear"], "b", "Polite greeting", "easy"),
    ],
    ("The Magic Garden - Quiz", 3): [
        _q("Children in the story were:", ["Cruel to the garden", "Kind to the garden", "Afraid of plants", "Lazy"], "b", "Took good care", "easy"),
        _q("Magic in the garden could be:", ["Real spells", "How nature changes when cared for", "TV magic", "Trick photography"], "b", "Care = magical results", "medium"),
        _q("This story teaches that:", ["Plants don't matter", "Nature responds to love and care", "Use chemicals only", "Cut all flowers"], "b", "Nurture nature", "easy"),
    ],
    ("Bird Talk - Quiz", 3): [
        _q("Birds in poems often represent:", ["Heavy machines", "Freedom and joy", "Anger", "Cars"], "b", "Birds = freedom", "medium"),
        _q("Birds talk in their:", ["English only", "Own chirps and songs", "Hindi", "Sign language"], "b", "Their own sounds", "easy"),
        _q("Poet uses ___ to make birds 'talk':", ["Imagination", "A microphone", "A computer", "Books"], "a", "Imagination/personification", "medium"),
    ],
    ("Living and Non-living - Quiz", 3): [
        _q("All living things ___ over time:", ["Stay the same", "Grow and change", "Become smaller forever", "Turn to stone"], "b", "Growth is a sign of life", "easy"),
        _q("Reproduction means:", ["Eating", "Producing young / offspring", "Sleeping", "Walking"], "b", "Living things make new ones", "medium"),
        _q("Which is non-living?", ["Bird", "Tree", "Cloud", "Cat"], "c", "Cloud is non-living", "medium"),
    ],
    ("Foods We Eat - Quiz", 3): [
        _q("A balanced diet includes:", ["Only sweets", "All food groups in proper amounts", "Only meat", "No water"], "b", "Variety in right proportion", "easy"),
        _q("Junk food gives us:", ["Lots of nutrients", "Mostly empty calories and fat", "Vitamins only", "Pure protein"], "b", "Empty calories", "easy"),
        _q("Drinking enough water keeps us:", ["Sick", "Hydrated and healthy", "Sleepy", "Hungry"], "b", "Hydration is essential", "easy"),
    ],
    ("Plants Around Us - Quiz", 3): [
        _q("Stem of a plant supports:", ["Roots only", "Leaves, flowers and fruits", "Worms", "Birds only"], "b", "Stem holds them up", "easy"),
        _q("Coconut tree is a:", ["Herb", "Shrub", "Tree", "Creeper"], "c", "Tall tree with woody trunk", "easy"),
        _q("Pumpkin plant is a:", ["Tree", "Creeper", "Herb", "Shrub"], "b", "It creeps along the ground", "medium"),
    ],
    ("Belakhinaha (Dawn) - Quiz", 3): [
        _q("'Suryodaya' means:", ["Sunset", "Sunrise", "Noon", "Midnight"], "b", "Surya = sun, udaya = rising", "medium"),
        _q("In the morning, birds usually:", ["Sleep", "Sing / chirp", "Hide", "Stop flying"], "b", "Birds sing at dawn", "easy"),
        _q("Dawn brings:", ["Darkness", "First light of day", "Heavy rain", "Storms"], "b", "First sunlight", "easy"),
    ],
    ("Karnataka Hesarugalu (Famous places) - Quiz", 3): [
        _q("Karnataka's IT capital is:", ["Mysuru", "Bengaluru", "Belagavi", "Davanagere"], "b", "Bengaluru is IT hub", "easy"),
        _q("'Sandalwood city':", ["Mangaluru", "Mysuru", "Tumakuru", "Hubballi"], "b", "Mysore sandalwood is famous", "medium"),
        _q("Hampi ruins are near:", ["Bengaluru", "Hospet (Vijayanagara)", "Mysuru", "Mangaluru"], "b", "Hampi is near Hospet", "medium"),
    ],
    ("Naadu Naadina Heggalike (Country pride) - Quiz", 3): [
        _q("Karnataka's state flower:", ["Rose", "Lotus", "Jasmine", "Marigold"], "b", "Lotus", "medium"),
        _q("Karnataka's state bird:", ["Peacock", "Indian Roller / Neelakanta", "Sparrow", "Eagle"], "b", "Indian roller (Neelkanth)", "hard"),
        _q("Karnataka Rajyotsava is celebrated on:", ["1 November", "26 January", "15 August", "2 October"], "a", "Karnataka formation day", "easy"),
    ],
    ("Time and Money - Quiz", 3): [
        _q("How many minutes in half an hour?", ["15", "20", "30", "45"], "c", "Half of 60 = 30", "easy"),
        _q("₹50 + ₹25 = ?", ["₹65", "₹70", "₹75", "₹100"], "c", "50 + 25 = 75", "easy"),
        _q("How many ₹5 coins make ₹50?", ["5", "10", "15", "25"], "b", "10 × 5 = 50", "easy"),
    ],
    ("Smart Charts (Data) - Quiz", 3): [
        _q("Bar charts use ___ to compare values:", ["Words", "Bars / rectangles", "Faces", "Lines on a map"], "b", "Heights of bars compare values", "easy"),
        _q("In a class survey, fewest students chose orange juice. The bar for orange will be:", ["Tallest", "Shortest", "Same as others", "Invisible"], "b", "Smallest count = shortest bar", "easy"),
        _q("A pictograph uses ___ to represent data:", ["Numbers only", "Pictures / icons", "Sentences", "Music notes"], "b", "Pictures stand for amounts", "medium"),
    ],
    ("Little by Little - Quiz", 3): [
        _q("In the poem, who speaks?", ["A bird", "A growing acorn / oak", "A boy", "A river"], "b", "Acorn growing into oak", "medium"),
        _q("'Steady effort' is the theme. It means:", ["Quitting easily", "Continuous, patient work", "Never starting", "Sleeping"], "b", "Patient continuous work", "easy"),
        _q("Birds and insects in the poem help to:", ["Cut the tree", "Spread its seeds / give shelter", "Burn it", "Move it"], "b", "Help acorn/tree thrive", "medium"),
    ],
    ("Air Around Us - Quiz", 3): [
        _q("Air pollution is caused by:", ["Trees", "Smoke from vehicles and factories", "Clean rivers", "Sunlight"], "b", "Smoke is a major pollutant", "easy"),
        _q("Wind helps to:", ["Stop kites", "Fly kites and turn windmills", "Burn fires", "Boil water"], "b", "Moving air rotates and lifts", "easy"),
        _q("Plants help by:", ["Polluting air", "Releasing oxygen we breathe", "Eating sunlight only", "Drinking blood"], "b", "Plants give oxygen", "easy"),
    ],
}


EXTRA_GRADE_4 = {
    ("Building with Bricks (Shapes) - Quiz", 4): [
        _q("How many vertices (corners) does a cube have?", ["4", "6", "8", "12"], "c", "Cube = 8 corners", "medium"),
        _q("A solid with circular base and pointed top is a:", ["Cube", "Cone", "Cylinder", "Sphere"], "b", "Cone (like an ice-cream cone)", "easy"),
        _q("A football is shaped like a:", ["Cube", "Sphere", "Cone", "Cylinder"], "b", "Sphere", "easy"),
    ],
    ("Long and Short (Measurement) - Quiz", 4): [
        _q("1 cm = ___ mm", ["1", "10", "100", "1000"], "b", "1 cm = 10 mm", "easy"),
        _q("Best instrument to measure length of a notebook:", ["Weighing scale", "Ruler / scale", "Clock", "Thermometer"], "b", "Ruler in cm/mm", "easy"),
        _q("250 cm equals ___ m:", ["0.25", "2.5", "25", "250"], "b", "250 ÷ 100 = 2.5", "medium"),
    ],
    ("Multiplication and Division - Quiz", 4): [
        _q("15 × 6 = ?", ["80", "85", "90", "95"], "c", "15 × 6 = 90", "easy"),
        _q("72 ÷ 8 = ?", ["7", "8", "9", "10"], "c", "72 ÷ 8 = 9", "easy"),
        _q("If 100 sweets are shared by 5 children equally, each gets:", ["10", "15", "20", "25"], "c", "100 ÷ 5 = 20", "medium"),
    ],
    ("Wake Up - Quiz", 4): [
        _q("In the poem, who calls the child to wake up?", ["Father", "Mother", "Friend", "Teacher"], "b", "Mother gently wakes child", "easy"),
        _q("Birds in the poem are:", ["Flying away forever", "Singing in the morning", "Sleeping", "Hiding"], "b", "Singing morning songs", "easy"),
        _q("Sunshine in the poem brings:", ["Sadness", "Warmth and energy", "Storms", "Snow"], "b", "Warmth and brightness", "easy"),
    ],
    ("Neha's Alarm Clock - Quiz", 4): [
        _q("Neha kept oversleeping in the:", ["Afternoon", "Morning", "Night", "Evening"], "b", "She slept past sunrise", "easy"),
        _q("Why didn't grandmother wake her up daily?", ["Grandma overslept too", "Neha needed self-discipline", "Grandma was angry", "Grandma travelled"], "b", "Goal was self-reliance", "medium"),
        _q("In the end, Neha learns to:", ["Depend on others", "Wake herself up on time", "Skip school", "Sleep more"], "b", "Self-discipline", "easy"),
    ],
    ("Helen Keller - Quiz", 4): [
        _q("Helen Keller could not see or hear from a young age. Despite this she:", ["Gave up", "Learned to read, write, speak", "Stayed silent forever", "Hid at home"], "b", "She mastered language", "easy"),
        _q("Anne Sullivan taught Helen by:", ["Writing on a board", "Spelling words on Helen's hand", "Sending letters", "Showing pictures"], "b", "Finger-spelling on the palm", "medium"),
        _q("Helen Keller became a famous:", ["Singer", "Author and activist", "Painter", "Athlete"], "b", "She wrote books and gave lectures", "medium"),
    ],
    ("Going to School - Quiz", 4): [
        _q("Children in deserts may travel to school on:", ["Boats", "Camels", "Trains", "Planes"], "b", "Camel rides in deserts", "easy"),
        _q("In Kashmir, in winter, children may use:", ["Bicycles", "Sledges / walking on snow", "Boats", "Buses always"], "b", "Snowy paths", "medium"),
        _q("Most children worldwide reach school by:", ["Plane", "Walking, cycling or bus", "Rocket", "Submarine"], "b", "Common everyday transport", "easy"),
    ],
    ("The Story of Amrita (Trees) - Quiz", 4): [
        _q("How did Amrita Devi protect the trees?", ["She fenced them", "She hugged them, refusing to leave", "She watered them", "She moved them"], "b", "She and her community hugged trees", "medium"),
        _q("This event later inspired which famous movement?", ["Quit India", "Chipko Movement", "Salt March", "Swadeshi"], "b", "Chipko = hug movement", "medium"),
        _q("Bishnois follow rules of:", ["Eating meat", "Protecting all life and nature", "Building cities", "Hunting"], "b", "Non-violence and nature protection", "medium"),
    ],
    ("Anita and the Honeybees - Quiz", 4): [
        _q("Drones in a beehive are:", ["Female workers", "Male bees", "Soldier bees", "Queen bees"], "b", "Drones are male", "medium"),
        _q("Worker bees collect:", ["Salt", "Nectar from flowers", "Sand", "Plastic"], "b", "Nectar → honey", "easy"),
        _q("Beekeeping is also called:", ["Apiculture", "Sericulture", "Pisciculture", "Horticulture"], "a", "Apiculture = bee-keeping", "medium"),
    ],
    ("Karnataka Sampada (Heritage) - Quiz", 4): [
        _q("Belur and Halebidu temples were built by:", ["Cholas", "Hoysalas", "Mughals", "Mauryas"], "b", "Hoysala dynasty", "medium"),
        _q("Mysuru is famous for which festival?", ["Onam", "Dasara", "Diwali only", "Pongal"], "b", "Mysuru Dasara", "easy"),
        _q("Bidri art is metalwork from:", ["Bidar (Karnataka)", "Bengaluru", "Mangaluru", "Mysuru"], "a", "Bidri ware originated in Bidar", "medium"),
    ],
    ("Janapada Geethegalu (Folk Songs) - Quiz", 4): [
        _q("Folk songs are usually:", ["Written in Sanskrit", "Passed down orally", "Found only in books", "Sung only by kings"], "b", "Oral tradition", "easy"),
        _q("Folk songs may be sung during:", ["Weddings, harvest, festivals", "Sleep only", "Wars only", "Maths class"], "a", "Many community occasions", "easy"),
        _q("Karnataka's famous folk theatre form:", ["Kathakali", "Yakshagana", "Bharatanatyam", "Kuchipudi"], "b", "Yakshagana from coastal Karnataka", "medium"),
    ],
    ("Nadigalu (Rivers of Karnataka) - Quiz", 4): [
        _q("Tungabhadra dam is in Karnataka near:", ["Hospet / Hampi", "Mysuru", "Bengaluru", "Mangaluru"], "a", "Hospet area", "medium"),
        _q("Cauvery river originates at:", ["Talakaveri (Coorg)", "Hampi", "Bengaluru", "Mysuru"], "a", "Talakaveri in Kodagu", "medium"),
        _q("Sharavati river is famous for:", ["Cauvery dam", "Jog Falls", "Elephants", "Tea gardens"], "b", "Jog Falls", "easy"),
    ],
    ("Tick-Tick-Tick (Time) - Quiz", 4): [
        _q("From 8:15 AM to 9:00 AM is:", ["15 min", "30 min", "45 min", "1 hour"], "c", "60 − 15 = 45 min", "medium"),
        _q("How many hours from 6 PM to 6 AM next morning?", ["6", "12", "18", "24"], "b", "12 hours", "medium"),
        _q("Number of minutes in 2 hours:", ["60", "100", "120", "180"], "c", "2 × 60 = 120 min", "easy"),
    ],
    ("Jugs and Mugs (Capacity) - Quiz", 4): [
        _q("Half a litre = ___ mL:", ["50", "250", "500", "750"], "c", "1/2 of 1000 mL = 500 mL", "easy"),
        _q("A water tank holds 500 L. In mL:", ["50", "5000", "500000", "5000000"], "c", "500 × 1000 = 500,000 mL", "medium"),
        _q("Best unit to measure petrol in a tank:", ["mL", "L", "km", "m"], "b", "Litres for petrol", "easy"),
    ],
    ("Why? (Poem) - Quiz", 4): [
        _q("'Why?' questions help us:", ["Confuse others", "Discover and learn", "Stay quiet", "Forget"], "b", "Curiosity drives learning", "easy"),
        _q("Famous scientists started with:", ["Reading TV", "Asking many questions", "Sleeping", "Avoiding books"], "b", "Inquiry leads to discovery", "easy"),
        _q("Children should be ___ to ask questions:", ["Discouraged", "Encouraged", "Punished", "Ignored"], "b", "Encouragement helps growth", "easy"),
    ],
    ("From Market to Home - Quiz", 4): [
        _q("Vegetables stay fresh in a:", ["Hot oven", "Cool refrigerator", "Open sun", "Open dustbin"], "b", "Cold slows spoilage", "easy"),
        _q("Buying directly from a farmer is called:", ["Wholesale", "Direct / farm-to-home", "Retail in mall", "Online from abroad"], "b", "Farm-to-home", "medium"),
        _q("Why should we wash vegetables?", ["To make them sweet", "To remove dirt and pesticides", "To freeze them", "To make them sour"], "b", "Hygiene + remove chemicals", "easy"),
    ],
}


EXTRA_GRADE_5 = {
    ("The Fish Tale - Quiz", 5): [
        _q("A fishing net catches 36 fish. If 9 are released back, how many kept?", ["18", "21", "27", "30"], "c", "36 − 9 = 27", "easy"),
        _q("Fish breathe through their:", ["Lungs", "Gills", "Skin", "Mouth only"], "b", "Gills extract oxygen from water", "easy"),
        _q("If 1 boat carries 6 fishermen, 5 boats carry:", ["20", "25", "30", "36"], "c", "5 × 6 = 30", "medium"),
    ],
    ("Shapes and Angles - Quiz", 5): [
        _q("An angle less than 90° is called:", ["Acute", "Right", "Obtuse", "Reflex"], "a", "Acute < 90°", "easy"),
        _q("An angle greater than 90° but less than 180° is:", ["Acute", "Right", "Obtuse", "Reflex"], "c", "Obtuse > 90°", "easy"),
        _q("A triangle with one 90° angle is a:", ["Equilateral", "Right-angled triangle", "Isosceles", "Scalene"], "b", "Right triangle", "medium"),
    ],
    ("How Many Squares? - Quiz", 5): [
        _q("Perimeter of a rectangle 5 cm × 3 cm:", ["8 cm", "15 cm", "16 cm", "30 cm"], "c", "2(5+3) = 16 cm", "medium"),
        _q("Area of a rectangle 10 m × 5 m:", ["15 sq m", "30 sq m", "50 sq m", "100 sq m"], "c", "10 × 5 = 50 sq m", "easy"),
        _q("If side of a square doubles, its area becomes ___ times:", ["1", "2", "3", "4"], "d", "(2s)² = 4s²", "hard"),
    ],
    ("Parts and Wholes - Quiz", 5): [
        _q("If a chocolate bar is divided into 6 equal parts and you eat 4, fraction eaten:", ["1/6", "2/6", "4/6 (or 2/3)", "6/4"], "c", "4 of 6 = 4/6 = 2/3", "medium"),
        _q("Which fraction equals 1?", ["1/2", "3/4", "5/5", "0/1"], "c", "Whole = 5/5 = 1", "easy"),
        _q("Compare: 1/4 + 1/4 = ?", ["1/2", "1/8", "2/8 only", "Not equal to anything"], "a", "1/4 + 1/4 = 2/4 = 1/2", "medium"),
    ],
    ("Be My Multiple, I'll be Your Factor - Quiz", 5): [
        _q("Multiples of 7: 7, 14, 21, ?", ["27", "28", "29", "30"], "b", "7 × 4 = 28", "easy"),
        _q("Common factor of 6 and 9:", ["1 and 3", "Only 6", "Only 9", "Only 1"], "a", "Both share 1 and 3", "medium"),
        _q("LCM of 3 and 5:", ["8", "15", "30", "45"], "b", "3 × 5 = 15 (since coprime)", "medium"),
    ],
    ("Super Senses - Quiz", 5): [
        _q("Eagles have very sharp:", ["Hearing", "Sight / vision", "Smell", "Taste"], "b", "Eagles can spot prey from far above", "easy"),
        _q("Ants follow each other using:", ["Magic", "Chemical trail (pheromones)", "Voice calls", "Maps"], "b", "Pheromone trails", "medium"),
        _q("Bees see colours including:", ["Only black & white", "Ultraviolet that humans cannot see", "Only red", "Only blue"], "b", "Bees see UV light", "hard"),
    ],
    ("A Snake Charmer's Story - Quiz", 5): [
        _q("Snakes are mostly:", ["Friendly to humans always", "Shy and prefer to escape", "Aggressive always", "Tame from birth"], "b", "Most snakes avoid humans", "easy"),
        _q("Anti-snake-bite medicine is called:", ["Antibiotic", "Anti-venom serum", "Vaccine", "Painkiller"], "b", "Anti-venom", "medium"),
        _q("Snake skin is covered in:", ["Fur", "Feathers", "Scales", "Slime only"], "c", "Reptile scales", "easy"),
    ],
    ("From Tasting to Digesting - Quiz", 5): [
        _q("Saliva starts breaking down:", ["Fats only", "Carbohydrates / starch", "Proteins only", "Bones"], "b", "Salivary amylase digests starch", "medium"),
        _q("The food pipe is also called the:", ["Trachea", "Esophagus", "Larynx", "Pharynx"], "b", "Esophagus carries food to stomach", "medium"),
        _q("Undigested food leaves the body through:", ["Mouth", "Anus", "Skin", "Hair"], "b", "Anus = exit point", "easy"),
    ],
    ("Mangoes Round the Year - Quiz", 5): [
        _q("Refrigeration preserves food by:", ["Adding sugar", "Slowing bacterial growth (cold)", "Increasing heat", "Adding water"], "b", "Cold slows decay", "easy"),
        _q("Pickle jars are kept tightly closed to:", ["Save space", "Keep out air, water, and germs", "Make pickle sour", "Look pretty"], "b", "Air-tight prevents spoilage", "easy"),
        _q("Mango peak season in India is:", ["Winter", "Summer (Apr–Jun)", "Monsoon", "Spring only"], "b", "Mangoes ripen in summer", "easy"),
    ],
    ("Seeds and Seeds - Quiz", 5): [
        _q("Burrs (sticky seeds) are dispersed by:", ["Wind", "Water", "Animal fur", "Explosion"], "c", "They cling to fur and clothes", "medium"),
        _q("Maple seeds spin like helicopters because:", ["They are heavy", "Wings let wind carry them", "They have engines", "They roll"], "b", "Wings catch wind", "medium"),
        _q("First step of germination:", ["Flowering", "Absorbing water", "Producing fruit", "Falling leaves"], "b", "Seed swells with water", "easy"),
    ],
    ("Ice-Cream Man - Quiz", 5): [
        _q("Ice-cream is best stored:", ["At room temperature", "In the freezer", "In the sun", "In water"], "b", "Freezer keeps it solid", "easy"),
        _q("Ice-cream is mostly made of:", ["Water and air", "Milk, cream, sugar, flavours", "Only ice", "Only fruit"], "b", "Dairy + sugar + flavour", "easy"),
        _q("The poem describes the ice-cream man as bringing:", ["Worry", "Joy / happiness to children", "Anger", "Fear"], "b", "Joy with cool treats", "easy"),
    ],
    ("Wonderful Waste! - Quiz", 5): [
        _q("'Avial' is a:", ["Sweet", "Mixed-vegetable curry from Kerala", "Drink", "Bread"], "b", "Famous Kerala vegetable curry", "easy"),
        _q("The cook used vegetable peels because:", ["He had no other food", "He couldn't waste them; turned waste to food", "He was lazy", "King ordered him"], "b", "Creative no-waste cooking", "medium"),
        _q("This story shows ___ in cooking:", ["Carelessness", "Resourcefulness / creativity", "Greed", "Pride"], "b", "Resourceful, creative use of waste", "easy"),
    ],
    ("Nanna Shaale - Quiz", 5): [
        _q("'Shikshana' (education) helps us:", ["Stay ignorant", "Become knowledgeable and useful", "Sleep more", "Avoid jobs"], "b", "Knowledge for life", "easy"),
        _q("'Shikshakaru' refers to:", ["Students", "Teachers", "Parents", "Friends"], "b", "Teachers (gurus)", "easy"),
        _q("'Vidyaarthi' means:", ["Teacher", "Student / learner", "Director", "Driver"], "b", "Vidya + arthi = student", "medium"),
    ],
    ("Aase Magu - Quiz", 5): [
        _q("'Shrama' means:", ["Laziness", "Hard work", "Sleep", "Food"], "b", "Shrama = labour/effort", "medium"),
        _q("The lesson promotes:", ["Quick fixes", "Patience and persistence", "Cheating", "Borrowing"], "b", "Patient persistent effort", "easy"),
        _q("'Kanasu' means:", ["Story", "Dream", "Song", "Fight"], "b", "Kanasu = dream", "easy"),
    ],
    ("Kaalige - Quiz", 5): [
        _q("'Aroghya' means:", ["Wealth", "Health", "Fame", "Fear"], "b", "Aroghya = health", "medium"),
        _q("Daily exercise keeps us:", ["Sick", "Fit and healthy", "Lazy", "Sleepy"], "b", "Exercise = fitness", "easy"),
        _q("'Vyaayama' means:", ["Eating", "Exercise", "Sleeping", "Reading"], "b", "Vyaayama = exercise", "medium"),
    ],
    ("Numbers & Place Value - Practice Quiz", 5): [
        _q("Place value of 8 in 1,800:", ["8", "80", "800", "8000"], "c", "8 in hundreds = 800", "easy"),
        _q("Number 'one lakh' has how many zeros?", ["3", "4", "5", "6"], "c", "1,00,000 has 5 zeros", "medium"),
        _q("Successor of 9999:", ["9998", "10000", "10001", "99999"], "b", "9999 + 1 = 10000", "easy"),
    ],
    ("Addition & Subtraction - Practice Quiz", 5): [
        _q("789 + 211 = ?", ["900", "999", "1000", "1100"], "c", "789 + 211 = 1000", "medium"),
        _q("1500 − 750 = ?", ["650", "750", "850", "950"], "b", "1500 − 750 = 750", "easy"),
        _q("Sum of 234, 167 and 99:", ["400", "500", "550", "600"], "b", "234+167+99 = 500", "medium"),
    ],
    ("Multiplication - Practice Quiz", 5): [
        _q("11 × 11 = ?", ["111", "121", "131", "141"], "b", "11 × 11 = 121", "easy"),
        _q("0 × 999 = ?", ["0", "1", "999", "9990"], "a", "Anything × 0 = 0", "easy"),
        _q("If 1 dozen = 12, then 5 dozens = ?", ["48", "55", "60", "65"], "c", "5 × 12 = 60", "medium"),
    ],
    ("Fractions - Practice Quiz", 5): [
        _q("3/4 of 20 = ?", ["10", "12", "15", "16"], "c", "3/4 × 20 = 15", "medium"),
        _q("Decimal form of 1/4 is:", ["0.25", "0.5", "0.75", "1.0"], "a", "1/4 = 0.25", "easy"),
        _q("2/3 + 1/3 = ?", ["1", "1/3", "2/3", "3/6"], "a", "Sum equals 3/3 = 1", "easy"),
    ],
    ("Living Things - Practice Quiz", 5): [
        _q("Living things show:", ["No growth", "Growth, reproduction, response", "No movement ever", "Static behaviour"], "b", "All life processes", "easy"),
        _q("Plants are different from animals because plants:", ["Move freely", "Make their own food", "Don't grow", "Don't reproduce"], "b", "Photosynthesis", "easy"),
        _q("Bacteria are:", ["Always dead", "Microscopic living organisms", "Stones", "Plants only"], "b", "Tiny living organisms", "medium"),
    ],
    ("Plants Around Us - Practice Quiz", 5): [
        _q("Photosynthesis produces:", ["CO₂", "Glucose and oxygen", "Salt", "Plastic"], "b", "Sugar + O₂", "medium"),
        _q("The roots usually grow:", ["Above the soil", "Below into the soil", "Sideways only", "On leaves"], "b", "Roots go down into soil", "easy"),
        _q("A flower's main job is:", ["Look pretty only", "Reproduction (make seeds)", "Make food", "Hold water"], "b", "Reproduction", "easy"),
    ],
    ("Grammar Basics - Practice Quiz", 5): [
        _q("A word that describes a noun is a/an:", ["Verb", "Adjective", "Pronoun", "Preposition"], "b", "Adjectives describe nouns", "easy"),
        _q("'He' is a/an:", ["Noun", "Verb", "Pronoun", "Adjective"], "c", "Pronouns replace nouns", "easy"),
        _q("Past tense of 'go':", ["Goed", "Went", "Gone", "Going"], "b", "Irregular: go → went", "medium"),
    ],
    ("The Junk Seller (Money) - Quiz", 5): [
        _q("If 2 kg newspaper sells at ₹6/kg, total = ?", ["₹6", "₹8", "₹10", "₹12"], "d", "2 × 6 = 12", "easy"),
        _q("From ₹500, after spending ₹278, balance = ?", ["₹212", "₹222", "₹232", "₹272"], "b", "500 − 278 = 222", "medium"),
        _q("Recycling old paper helps to:", ["Cut more trees", "Save trees and reduce waste", "Make money disappear", "Pollute rivers"], "b", "Saves trees and energy", "easy"),
    ],
    ("Every Drop Counts (Water) - Quiz", 5): [
        _q("A leaking tap can waste ___ litres of water per day:", ["A few drops only", "Many litres (10+) over time", "100,000 L", "Nothing"], "b", "Drips add up significantly", "medium"),
        _q("Best practice while brushing teeth:", ["Keep tap running", "Use a glass of water; close tap", "Use sea water", "Use no water"], "b", "Save water", "easy"),
        _q("Recharging groundwater is helped by:", ["Concrete everywhere", "Open soil & rainwater pits", "Sealed roads only", "Plastic sheets"], "b", "Soil and pits absorb rainwater", "medium"),
    ],
    ("My Shadow (Poem) - Quiz", 5): [
        _q("A shadow is formed when:", ["Wind blows", "Light is blocked by an object", "It rains", "It snows"], "b", "Opaque object blocks light", "easy"),
        _q("Shadow looks longest:", ["At noon", "Early morning or evening", "At midnight", "Underwater"], "b", "Low sun = long shadow", "medium"),
        _q("Why doesn't a shadow have colour?", ["Light is missing in that area", "It is painted", "It has no eyes", "It hates colour"], "a", "Absence of light", "easy"),
    ],
}


EXTRA_GRADE_6 = {
    ("Knowing Our Numbers - Quiz", 6): [
        _q("How many zeros in 1 crore?", ["5", "6", "7", "8"], "c", "1,00,00,000 has 7 zeros", "medium"),
        _q("Roman numeral for 50:", ["L", "C", "D", "M"], "a", "L = 50", "easy"),
        _q("Round 4,789 to nearest hundred:", ["4,700", "4,800", "4,900", "5,000"], "b", "789 → 800 → 4,800", "medium"),
    ],
    ("Whole Numbers - Quiz", 6): [
        _q("Successor of 99 is:", ["98", "100", "999", "9999"], "b", "99 + 1 = 100", "easy"),
        _q("Identity element for addition:", ["0", "1", "-1", "10"], "a", "a + 0 = a", "easy"),
        _q("Identity element for multiplication:", ["0", "1", "10", "100"], "b", "a × 1 = a", "easy"),
    ],
    ("Playing with Numbers - Quiz", 6): [
        _q("Smallest prime number is:", ["1", "2", "3", "5"], "b", "2 is the smallest (only even) prime", "easy"),
        _q("LCM of 12 and 18:", ["6", "24", "36", "72"], "c", "Common multiples of 12 and 18 → 36", "medium"),
        _q("A number divisible by 9 has digit sum divisible by:", ["3", "5", "7", "9"], "d", "Divisibility rule of 9", "medium"),
    ],
    ("Basic Geometrical Ideas - Quiz", 6): [
        _q("Two lines intersecting at 90° are called:", ["Parallel", "Perpendicular", "Skew", "Curved"], "b", "Perpendicular = 90° intersection", "easy"),
        _q("A ray has:", ["No endpoints", "1 endpoint, extends in 1 direction", "2 endpoints", "Infinite endpoints"], "b", "Ray starts at a point and extends one way", "medium"),
        _q("A polygon with 5 sides is a:", ["Pentagon", "Hexagon", "Octagon", "Nonagon"], "a", "Penta = 5", "easy"),
    ],
    ("Understanding Elem. Shapes - Quiz", 6): [
        _q("Sum of angles in a quadrilateral:", ["180°", "270°", "360°", "540°"], "c", "Always 360°", "easy"),
        _q("A regular hexagon has each interior angle of:", ["60°", "90°", "120°", "180°"], "c", "(6-2)×180/6 = 120°", "medium"),
        _q("Isosceles triangle has:", ["All sides different", "Two equal sides", "Three equal sides", "Right angle only"], "b", "Iso = 'same'", "easy"),
    ],
    ("Food: Where Does It Come From? - Quiz", 6): [
        _q("Eggs come from:", ["Cows", "Goats", "Hens / birds", "Fish"], "c", "Hens lay eggs", "easy"),
        _q("Sugar is mainly made from:", ["Wheat", "Sugarcane / sugar beet", "Salt water", "Honey only"], "b", "Sugar from cane/beet", "easy"),
        _q("Vegetables we eat from underground:", ["Tomato", "Potato / onion", "Cabbage", "Banana"], "b", "Roots/tubers like potato, onion", "easy"),
    ],
    ("Components of Food - Quiz", 6): [
        _q("Roughage / fibre helps in:", ["Energy", "Digestion / bowel movement", "Bone strength", "Eyesight"], "b", "Helps move food and waste", "medium"),
        _q("Vitamin A keeps our ___ healthy:", ["Bones", "Eyes / vision", "Hair only", "Nails"], "b", "Vitamin A → eyes", "easy"),
        _q("Calcium-rich food:", ["Sugar", "Milk and dairy", "Salt", "Oil"], "b", "Milk = calcium", "easy"),
    ],
    ("Fibre to Fabric - Quiz", 6): [
        _q("Synthetic fibre example:", ["Cotton", "Wool", "Nylon / polyester", "Silk"], "c", "Man-made fibres", "easy"),
        _q("Jute fibre is obtained from:", ["Stem of jute plant", "Sheep wool", "Worms", "Soil"], "a", "Bast fibre from jute stem", "medium"),
        _q("Khadi cloth is hand-spun and hand-woven:", ["From silk", "Usually from cotton/wool by hand", "From plastic", "From iron"], "b", "Khadi = hand-spun cotton/wool", "medium"),
    ],
    ("Sorting Materials - Quiz", 6): [
        _q("Frosted glass is:", ["Transparent", "Translucent", "Opaque", "Magnetic"], "b", "Light passes but image not clear", "medium"),
        _q("Iron is attracted to:", ["Plastic", "Magnet", "Wood", "Paper"], "b", "Iron is magnetic", "easy"),
        _q("Insoluble substance example:", ["Sugar", "Salt", "Sand", "Lemon juice"], "c", "Sand does not dissolve in water", "easy"),
    ],
    ("Separation of Substances - Quiz", 6): [
        _q("To separate husk from grain we use:", ["Magnet", "Winnowing (wind)", "Filtration", "Boiling"], "b", "Wind blows lighter husk away", "medium"),
        _q("To separate iron pins from sand:", ["Filtration", "Magnet", "Hand-picking", "Sieving"], "b", "Iron is attracted to magnet", "easy"),
        _q("To remove tea leaves from tea:", ["Sieving / strainer", "Magnet", "Boiling", "Hand-picking"], "a", "Strainer / filter", "easy"),
    ],
    ("Who Did Patrick's Homework? - Quiz", 6): [
        _q("The little man's wish was to:", ["Stay forever", "Go free / not be caught", "Eat sweets", "Travel"], "b", "Wanted his freedom", "easy"),
        _q("To be set free, the little man:", ["Cried", "Did Patrick's homework", "Ran away", "Slept"], "b", "He helped with school work in exchange", "easy"),
        _q("Patrick learned:", ["To cheat always", "That hard work itself is the real magic", "To be lazy", "To trust strangers"], "b", "Lesson on effort and learning", "medium"),
    ],
    ("How the Dog Found Himself a Master - Quiz", 6): [
        _q("The wolf was scared of:", ["A cat", "A bear", "A rabbit", "Children"], "b", "Bear was bigger and stronger", "easy"),
        _q("The bear was scared of:", ["Eagle", "Lion", "Man (humans)", "Birds"], "c", "Man's intelligence/weapons", "easy"),
        _q("The dog's choice of master was based on:", ["Looks", "Strength", "Money", "Voice"], "b", "He kept choosing the stronger one", "medium"),
    ],
    ("Taro's Reward - Quiz", 6): [
        _q("Taro was a:", ["King", "Poor woodcutter", "Soldier", "Doctor"], "b", "Poor but loving son", "easy"),
        _q("Taro's reward came because of his:", ["Greed", "Love and devotion to his father", "Strength", "Cunning"], "b", "Selfless love rewarded", "easy"),
        _q("The story is from:", ["China", "Japan", "Korea", "Vietnam"], "b", "Japanese folktale", "easy"),
    ],
    ("An Indian-American Woman in Space - Quiz", 6): [
        _q("Kalpana Chawla studied:", ["Medicine", "Aerospace engineering", "Music", "Painting"], "b", "Aerospace engineering in USA", "medium"),
        _q("She made how many space flights before her death?", ["1", "2", "3", "5"], "b", "Two flights — second was Columbia STS-107", "hard"),
        _q("She was an inspiration for:", ["Boys only", "Girls and aspiring scientists everywhere", "Pilots only", "Doctors only"], "b", "Inspiration for all young dreamers", "easy"),
    ],
    ("A Different Kind of School - Quiz", 6): [
        _q("Children at Miss Beam's school learnt mostly about:", ["Maths", "Empathy and other people's feelings", "Science only", "Sports only"], "b", "Empathy lessons", "easy"),
        _q("On 'lame day' children pretended to be:", ["Deaf", "Limping with one leg tied", "Blind", "Dumb"], "b", "Limping with one leg tied", "medium"),
        _q("This kind of teaching is called:", ["Lecture", "Experiential / hands-on learning", "Online", "Distance"], "b", "Experiential learning", "medium"),
    ],
    ("Shishuvina Haadu - Quiz", 6): [
        _q("'Tayi' means:", ["Father", "Mother", "Sister", "Friend"], "b", "Tayi = mother", "easy"),
        _q("'Aata' means:", ["Story", "Game / play", "Song", "Food"], "b", "Aata = play", "easy"),
        _q("Children love:", ["Sleeping all day", "Playing and singing", "Working in fields", "Studying only"], "b", "Play is natural", "easy"),
    ],
    ("Namma Uttara Karnataka - Quiz", 6): [
        _q("Hubballi-Dharwad is a famous twin city of:", ["South Karnataka", "North Karnataka", "Coastal Karnataka", "Andhra"], "b", "North Karnataka", "easy"),
        _q("Famous Jowar (great millet) crop is grown in:", ["Coastal", "North Karnataka", "Western Ghats only", "Sea"], "b", "Jowar is staple in N. Karnataka", "medium"),
        _q("North Karnataka cuisine staple is:", ["Rice", "Jolada rotti (jowar roti)", "Dosa only", "Pasta"], "b", "Jolada rotti", "medium"),
    ],
    ("Nanna Priya Kavi - Quiz", 6): [
        _q("Da Ra Bendre wrote in which language?", ["Hindi", "Kannada", "Tamil", "Sanskrit"], "b", "Kannada poet", "easy"),
        _q("'Naaku Tanti' is a famous work by:", ["Kuvempu", "Da Ra Bendre", "Karanth", "Pampa"], "b", "Bendre's collection won Jnanapeetha", "medium"),
        _q("Number of Kannada Jnanapeetha winners as of 2025:", ["3", "5", "8", "12"], "c", "8 Kannada winners", "hard"),
    ],
    ("Integers - Quiz", 6): [
        _q("(-5) + (-3) = ?", ["-8", "-2", "2", "8"], "a", "Same sign add: -(5+3) = -8", "easy"),
        _q("Number line: integer to the left of −2:", ["-1", "0", "1", "-3"], "d", "Left = smaller; -3 < -2", "easy"),
        _q("Absolute value of −7:", ["-7", "0", "7", "14"], "c", "|−7| = 7", "medium"),
    ],
    ("Body Movements - Quiz", 6): [
        _q("Ball-and-socket joint is found at the:", ["Knee", "Shoulder / hip", "Elbow", "Skull"], "b", "Allows movement in all directions", "medium"),
        _q("Number of bones in adult human body:", ["106", "150", "206", "300"], "c", "Adults have 206 bones", "medium"),
        _q("Earthworms move by:", ["Wings", "Bristles and muscles", "Legs", "Wheels"], "b", "Bristles + muscles", "medium"),
    ],
    ("The Friendly Mongoose - Quiz", 6): [
        _q("Where is the story set?", ["A farm", "A village house", "A jungle", "A school"], "b", "Farmer's village home", "easy"),
        _q("The mongoose was treated like a:", ["Wild animal", "Family member / pet", "Enemy", "Stranger"], "b", "Friend of the family", "easy"),
        _q("Moral:", ["Hate animals", "Don't act in haste; gather facts first", "Always blame mongoose", "Run away"], "b", "Don't judge in haste", "medium"),
    ],
}


EXTRA_GRADE_7 = {
    ("Integers - Quiz", 7): [
        _q("(-12) ÷ 4 = ?", ["-3", "3", "-4", "4"], "a", "Negative ÷ positive = negative", "easy"),
        _q("Product of two negatives is:", ["Negative", "Positive", "Zero", "One"], "b", "(−)(−) = +", "easy"),
        _q("(-7) − (-3) = ?", ["-10", "-4", "4", "10"], "b", "−7 + 3 = −4", "medium"),
    ],
    ("Fractions and Decimals - Quiz", 7): [
        _q("0.6 + 0.25 = ?", ["0.81", "0.85", "0.95", "0.9"], "b", "0.60 + 0.25 = 0.85", "easy"),
        _q("3/5 ÷ 2 = ?", ["3/10", "6/5", "5/3", "1/10"], "a", "3/5 × 1/2 = 3/10", "medium"),
        _q("0.125 as a fraction:", ["1/4", "1/8", "1/16", "1/2"], "b", "0.125 = 125/1000 = 1/8", "medium"),
    ],
    ("Data Handling - Quiz", 7): [
        _q("Range of 5, 9, 12, 4, 8:", ["4", "8", "9", "12"], "b", "Max − Min = 12 − 4 = 8", "easy"),
        _q("Median of 3, 7, 9, 12, 14:", ["7", "9", "10", "12"], "b", "Middle value = 9", "easy"),
        _q("Bar graphs are best for:", ["Showing fractions only", "Comparing categorical data", "Drawing maps", "Telling stories"], "b", "Comparison across groups", "medium"),
    ],
    ("Simple Equations - Quiz", 7): [
        _q("Solve: 5x = 30", ["5", "6", "25", "150"], "b", "x = 30/5 = 6", "easy"),
        _q("Solve: x/3 = 4", ["1", "4", "7", "12"], "d", "x = 4 × 3 = 12", "easy"),
        _q("Solve: 2x + 3 = 11", ["2", "3", "4", "5"], "c", "2x = 8 → x = 4", "medium"),
    ],
    ("Lines and Angles - Quiz", 7): [
        _q("If two lines intersect, opposite angles are:", ["Always 90°", "Always equal (vertically opposite)", "Supplementary", "Different always"], "b", "Vertically opposite angles equal", "easy"),
        _q("Sum of angles around a point:", ["180°", "270°", "360°", "540°"], "c", "Full turn = 360°", "easy"),
        _q("Two angles whose sum is 180° are:", ["Complementary", "Supplementary", "Vertical", "Right"], "b", "Supplementary", "medium"),
    ],
    ("Nutrition in Plants - Quiz", 7): [
        _q("Stomata are:", ["Plant roots", "Tiny pores in leaves", "Flowers", "Tree barks"], "b", "Stomata exchange gases", "medium"),
        _q("Insectivorous plants like Venus flytrap eat insects to get:", ["Carbon", "Nitrogen", "Oxygen", "Water"], "b", "Nitrogen from insect bodies", "hard"),
        _q("Mushrooms get food by:", ["Photosynthesis", "Saprotrophic mode (absorbing decaying matter)", "Eating animals", "Drinking sea water"], "b", "Saprotrophs absorb dead matter", "medium"),
    ],
    ("Nutrition in Animals - Quiz", 7): [
        _q("Cattle have a special stomach with how many compartments?", ["1", "2", "3", "4"], "d", "Ruminants have 4-chamber stomachs", "medium"),
        _q("Amoeba digests food in a:", ["Stomach", "Food vacuole", "Mouth", "Liver"], "b", "Food vacuole inside cell", "medium"),
        _q("Tongue helps in:", ["Hearing", "Tasting and mixing food with saliva", "Smelling", "Seeing"], "b", "Tasting and mixing", "easy"),
    ],
    ("Fibre to Fabric - Quiz", 7): [
        _q("Sericulture is rearing of:", ["Sheep", "Silkworms", "Goats", "Bees"], "b", "Silk worms produce silk", "easy"),
        _q("Wool is mostly:", ["A plant fibre", "An animal fibre (sheep, goat)", "Synthetic", "Mineral"], "b", "Animal fibre", "easy"),
        _q("Pashmina shawls come from:", ["Cotton", "Pashmina goat hair", "Silkworms", "Polyester"], "b", "Cashmere/Pashmina goat", "medium"),
    ],
    ("Heat - Quiz", 7): [
        _q("Mercury thermometer reads:", ["Heat in joules", "Temperature", "Wind speed", "Sound"], "b", "Thermometer = temperature", "easy"),
        _q("Heat travels in metals by:", ["Convection", "Conduction", "Radiation", "Evaporation"], "b", "Conduction through solids", "medium"),
        _q("Sun's heat reaches Earth by:", ["Conduction", "Convection", "Radiation", "Refraction"], "c", "Radiation through space", "medium"),
    ],
    ("Acids, Bases and Salts - Quiz", 7): [
        _q("Lemon juice is:", ["Acid (citric acid)", "Base", "Neutral", "Salt"], "a", "Citric acid = sour", "easy"),
        _q("Soap is:", ["Acid", "Base", "Salt only", "Neutral always"], "b", "Soap is basic/alkaline", "easy"),
        _q("Indicator that turns red in acid and blue in base:", ["Litmus", "Sugar", "Water", "Salt"], "a", "Litmus paper indicator", "medium"),
    ],
    ("Three Questions - Quiz", 7): [
        _q("Tolstoy was from:", ["England", "Russia", "France", "Germany"], "b", "Famous Russian writer", "easy"),
        _q("The king disguised himself as a:", ["Prince", "Common man / pilgrim", "Soldier", "Farmer"], "b", "Disguised to find the hermit", "easy"),
        _q("The right time to do anything is:", ["Tomorrow", "Now / the present moment", "Next year", "Never"], "b", "Now is the only time", "medium"),
    ],
    ("A Gift of Chappals - Quiz", 7): [
        _q("The mridangam tutor was:", ["Rich", "Old / poor and barefoot man", "A king", "A child"], "b", "Old, poor music tutor", "medium"),
        _q("The children's father reacted:", ["Happily", "Slightly angrily but understood later", "By beating them", "By laughing only"], "b", "Mild anger then understanding", "medium"),
        _q("The chappals were given out of:", ["Compassion", "Trade", "Fear", "Greed"], "a", "Kind compassion", "easy"),
    ],
    ("Hum Panchi Unmukt Gagan Ke - Quiz", 7): [
        _q("Birds in this poem refuse to live in:", ["Open sky", "Cages of gold", "Forests", "Mountains"], "b", "Even gold cages = no freedom", "easy"),
        _q("The poem stresses the value of:", ["Wealth", "Freedom (swatantrata)", "Sleep", "Anger"], "b", "Freedom over comfort", "easy"),
        _q("'Gagan' means:", ["Earth", "Sky", "River", "Forest"], "b", "Gagan = sky", "easy"),
    ],
    ("Dad Kahe So Kijiye - Quiz", 7): [
        _q("Lesson is in the form of:", ["A long story", "A poem advising children", "A debate", "An essay"], "b", "Advice in poetic form", "easy"),
        _q("Children should respect:", ["Strangers only", "Elders and parents", "Wild animals", "Cars"], "b", "Respect parents/elders", "easy"),
        _q("Following good advice helps in:", ["Failure", "Building good character and life", "Becoming sad", "Being lazy"], "b", "Good values build life", "easy"),
    ],
    ("Himalay Ki Betiyaan - Quiz", 7): [
        _q("Most Himalayan rivers flow towards:", ["South / east into the plains", "Underground", "Up the mountains", "Stand still"], "a", "Down to the plains", "medium"),
        _q("These rivers provide ___ to North Indian plains:", ["Sand", "Fresh water and fertile soil", "Salt only", "Stones only"], "b", "Water + alluvium = fertile fields", "medium"),
        _q("Glacier-fed rivers flow even in:", ["Heavy rains only", "Summer (when ice melts)", "Winter only", "Never"], "b", "Summer ice melt feeds them", "medium"),
    ],
    ("Kathin Nishad - Quiz", 7): [
        _q("'Nishad' here suggests:", ["Failure / despair", "An adventure with hardships", "A festival", "A market"], "b", "Tough journey/situation", "medium"),
        _q("People who succeed have:", ["Easy lives", "Faced and overcome difficulties", "Cheated", "Slept a lot"], "b", "Resilience builds success", "easy"),
        _q("Lesson teaches:", ["Avoid problems", "Face them with courage", "Cry only", "Blame others"], "b", "Courage to face problems", "easy"),
    ],
    ("Mithai Wala - Quiz", 7): [
        _q("The Mithaiwala once was a:", ["Beggar", "Wealthy man with a family", "King", "Soldier"], "b", "He had been wealthy with a family", "medium"),
        _q("He sold sweets cheaply because:", ["He wanted profit", "He wanted to be near children (his joy)", "He hated rich people", "He had to"], "b", "Children reminded him of his lost ones", "hard"),
        _q("This story is about:", ["Greed", "Hidden grief and love for children", "Anger", "Politics"], "b", "Hidden personal loss", "medium"),
    ],
    ("Vachana Sahitya - Quiz", 7): [
        _q("Vachanas were composed mostly between:", ["6th–8th century", "12th century", "15th–16th century", "19th century"], "b", "Veerashaiva movement, 12th c.", "medium"),
        _q("Akkamahadevi was a famous female:", ["Painter", "Vachanakara (composer of vachanas)", "Soldier", "Builder"], "b", "Pioneer woman vachana poet", "medium"),
        _q("Vachanas typically address:", ["A king", "Lord Shiva (Linga)", "An emperor", "A teacher only"], "b", "Mostly Shiva-bhakti", "medium"),
    ],
    ("Purandaradasa Keertane - Quiz", 7): [
        _q("Purandaradasa lived in the:", ["12th century", "15th–16th century", "19th century", "21st century"], "b", "Around 1484-1564 CE", "medium"),
        _q("He composed about how many devotional songs (popularly):", ["1,000", "10,000", "475,000", "Just 50"], "c", "Tradition says ~4.75 lakh kirtanas", "hard"),
        _q("His real name was:", ["Tukaram", "Srinivasa Nayaka", "Annamayya", "Mira"], "b", "Srinivasa Nayaka before initiation", "hard"),
    ],
    ("Karnataka Darshana - Quiz", 7): [
        _q("State animal of Karnataka:", ["Tiger", "Indian elephant", "Lion", "Cow"], "b", "Indian elephant", "medium"),
        _q("State tree of Karnataka:", ["Banyan", "Sandalwood", "Neem", "Mango"], "b", "Sandalwood (Srigandha)", "medium"),
        _q("Coorg is famous for:", ["Iron mining", "Coffee plantations", "Diamond mining", "Tea only"], "b", "Coffee from Coorg/Kodagu", "easy"),
    ],
    ("The Triangle and its Properties - Quiz", 7): [
        _q("Exterior angle of a triangle = sum of:", ["Adjacent two angles", "Two opposite interior angles", "All three angles", "Right angles"], "b", "Exterior angle property", "medium"),
        _q("Pythagoras theorem applies to:", ["All triangles", "Right-angled triangles only", "Squares only", "Circles only"], "b", "Right triangles only", "medium"),
        _q("In a right triangle with legs 3 and 4, the hypotenuse =", ["5", "6", "7", "12"], "a", "√(9+16) = √25 = 5", "medium"),
    ],
    ("Wind, Storms and Cyclones - Quiz", 7): [
        _q("Air pressure decreases with:", ["Height", "Cold", "Humidity only", "Sound"], "a", "At high altitudes pressure drops", "medium"),
        _q("Tornadoes are most common in:", ["India", "USA (Tornado Alley)", "Antarctica", "Sahara"], "b", "Central US", "medium"),
        _q("'Eye' of a cyclone is:", ["Most violent part", "Calm centre with low pressure", "Outer ring only", "A literal eye"], "b", "Calm low-pressure centre", "hard"),
    ],
    ("The Ashes That Made Trees Bloom - Quiz", 7): [
        _q("Magic ashes were found:", ["In an attic", "Near a dog's burial spot", "Under the sea", "In a cave"], "b", "Where the dog was buried", "medium"),
        _q("The greedy old man was punished because:", ["He was old", "He misused magic for greed", "He was kind", "He laughed too much"], "b", "Greed leads to punishment", "easy"),
        _q("The good old man's tree bloomed because:", ["He prayed", "Magic ashes were sprinkled", "He sang", "He was rich"], "b", "Magic ashes from his beloved dog", "easy"),
    ],
}


EXTRA_GRADE_8 = {
    ("Rational Numbers - Quiz", 8): [
        _q("Multiplicative inverse of 4/5:", ["-4/5", "5/4", "-5/4", "1"], "b", "a × 1/a = 1, so 5/4", "easy"),
        _q("Sum of two rational numbers is always:", ["Irrational", "Rational", "Negative", "Zero"], "b", "Closure under addition", "medium"),
        _q("Between 1/2 and 1, a rational number is:", ["3/4", "0", "2", "1/4"], "a", "1/2 < 3/4 < 1", "medium"),
    ],
    ("Linear Equations in One Variable - Quiz", 8): [
        _q("Solve: (x − 1)/2 = 3", ["5", "6", "7", "8"], "c", "x − 1 = 6 → x = 7", "medium"),
        _q("Solve: 4x − 7 = 9", ["3", "4", "5", "6"], "b", "4x = 16 → x = 4", "easy"),
        _q("If 5 is added to twice a number, result is 19. Number is:", ["5", "7", "9", "12"], "b", "2x + 5 = 19 → x = 7", "medium"),
    ],
    ("Understanding Quadrilaterals - Quiz", 8): [
        _q("A square is a special:", ["Triangle", "Rectangle and rhombus", "Trapezium", "Pentagon"], "b", "Square = rectangle + rhombus properties", "medium"),
        _q("Each angle of a regular pentagon:", ["72°", "90°", "108°", "120°"], "c", "(5-2)×180/5 = 108°", "hard"),
        _q("Diagonals of a parallelogram:", ["Are equal always", "Bisect each other", "Are perpendicular always", "Don't intersect"], "b", "They bisect each other", "medium"),
    ],
    ("Data Handling - Quiz", 8): [
        _q("Probability of getting a number > 6 on a die:", ["0", "1/6", "1/2", "1"], "a", "Impossible event = 0", "easy"),
        _q("In a deck of 52 cards, P(red card):", ["1/4", "1/2", "3/4", "1/13"], "b", "26 red of 52 = 1/2", "medium"),
        _q("Probability of any sure event:", ["0", "1/2", "1", "Cannot say"], "c", "Sure event = 1", "easy"),
    ],
    ("Squares and Square Roots - Quiz", 8): [
        _q("√225 = ?", ["12", "13", "14", "15"], "d", "15 × 15 = 225", "easy"),
        _q("Square of −9:", ["-81", "0", "81", "18"], "c", "(-9)² = 81", "easy"),
        _q("Number of digits in square root of 1024:", ["1", "2", "3", "4"], "b", "√1024 = 32 (2 digits)", "medium"),
    ],
    ("Crop Production and Management - Quiz", 8): [
        _q("Tilling improves soil by:", ["Removing nutrients", "Loosening it for water and air", "Hardening it", "Killing all roots"], "b", "Loosening helps roots and water", "easy"),
        _q("Manure is:", ["Plastic", "Decomposed organic matter (compost)", "Salt", "Concrete"], "b", "Natural decomposed organic fertilizer", "easy"),
        _q("Storing grains needs:", ["Moisture", "Dry conditions and pest control", "Hot water", "Open air only"], "b", "Dry, pest-free storage", "medium"),
    ],
    ("Microorganisms: Friend and Foe - Quiz", 8): [
        _q("Antibiotics are used to fight:", ["Viruses", "Bacterial infections", "Plants", "Stones"], "b", "Bacterial infections", "medium"),
        _q("Penicillin was discovered by:", ["Newton", "Alexander Fleming", "Edison", "Curie"], "b", "Fleming, 1928", "medium"),
        _q("Vaccines protect us by:", ["Causing illness", "Building immunity (training the body)", "Removing blood", "Adding sugar"], "b", "Train immune system", "medium"),
    ],
    ("Coal and Petroleum - Quiz", 8): [
        _q("Coal is formed over:", ["Days", "Millions of years from buried plants", "Hours", "A few months"], "b", "Geologic time from plant remains", "medium"),
        _q("LPG mainly contains:", ["Methane", "Butane / propane", "Hydrogen", "CO₂"], "b", "Liquefied butane/propane", "medium"),
        _q("Bitumen is used for:", ["Making bread", "Road surfaces / tarring", "Drinking", "Cooking"], "b", "Roads and roofing", "medium"),
    ],
    ("Combustion and Flame - Quiz", 8): [
        _q("Three things needed for combustion:", ["Fuel only", "Fuel, air (oxygen), heat", "Water and salt", "Plastic and ice"], "b", "The 'fire triangle'", "easy"),
        _q("Forest fires can be controlled by:", ["Pouring petrol", "Removing fuel / cutting fire breaks", "Adding wood", "Doing nothing"], "b", "Cut off fuel supply", "easy"),
        _q("Calorific value is measured in:", ["Metres", "kJ/kg", "Litres", "Seconds"], "b", "Energy per kilogram", "hard"),
    ],
    ("Conservation of Plants - Quiz", 8): [
        _q("Soil eroded due to deforestation makes the land:", ["Fertile", "Less fertile / barren", "Wet always", "Magnetic"], "b", "Top soil washed away", "easy"),
        _q("Endemic species are those:", ["Found everywhere", "Native to a specific region only", "Extinct", "From other planets"], "b", "Limited geographic range", "medium"),
        _q("Reforestation means:", ["Cutting more trees", "Planting trees in deforested land", "Building cities", "Burning forests"], "b", "Re-planting trees", "easy"),
    ],
    ("Resources - Quiz", 8): [
        _q("Coal is a ___ resource:", ["Renewable", "Non-renewable", "Cultural", "Imaginary"], "b", "Takes ages to form", "easy"),
        _q("'Patent' is a way to protect:", ["Money", "Inventions / human knowledge", "Animals", "Sand"], "b", "Intellectual property protection", "medium"),
        _q("'Stocks' as a resource means:", ["Resources known but not usable yet", "Banknotes", "Cattle", "Clothes"], "a", "Known but not currently usable", "hard"),
    ],
    ("Land, Soil, Water - Quiz", 8): [
        _q("Most fertile soil for agriculture:", ["Sandy", "Alluvial", "Rocky", "Salty"], "b", "Alluvial soil = very fertile", "easy"),
        _q("Water cycle is also called the:", ["Carbon cycle", "Hydrological cycle", "Nitrogen cycle", "Rock cycle"], "b", "Hydrological cycle", "medium"),
        _q("Rainwater harvesting helps to:", ["Waste water", "Recharge groundwater", "Pollute lakes", "Heat the air"], "b", "Replenishes underground aquifers", "easy"),
    ],
    ("Mineral and Power - Quiz", 8): [
        _q("Bauxite is the ore of:", ["Iron", "Aluminium", "Copper", "Gold"], "b", "Bauxite → aluminium", "medium"),
        _q("Hydroelectricity is generated using:", ["Wind", "Falling water", "Coal", "Sunlight"], "b", "Moving water turns turbines", "easy"),
        _q("Petroleum is found:", ["On mountain tops", "Underground in sedimentary rocks", "On glaciers", "In trees"], "b", "Trapped in rock layers", "medium"),
    ],
    ("Agriculture - Quiz", 8): [
        _q("Wheat is a:", ["Kharif crop", "Rabi crop", "Plantation crop", "Cash crop only"], "b", "Rabi (winter) crop", "easy"),
        _q("Mixed farming is:", ["Just crops", "Crops + livestock together", "Just animals", "Only fruit"], "b", "Crops together with cattle", "medium"),
        _q("Bhakra Nangal dam is on which river?", ["Ganga", "Sutlej", "Krishna", "Cauvery"], "b", "Sutlej river", "hard"),
    ],
    ("Industries - Quiz", 8): [
        _q("Cottage industry uses:", ["Big machines", "Hand tools at home / small scale", "Rockets", "Heavy trucks"], "b", "Small-scale household setup", "easy"),
        _q("Silicon Valley of India:", ["Mumbai", "Bengaluru", "Delhi", "Kolkata"], "b", "Bengaluru — IT hub", "easy"),
        _q("Manchester of India:", ["Surat", "Ahmedabad / Mumbai", "Delhi", "Kolkata"], "b", "Ahmedabad / Mumbai for textiles", "medium"),
    ],
    ("Dhwani - Quiz", 8): [
        _q("Theme of 'Dhwani':", ["Despair", "Hope and new life of spring", "Loneliness", "War"], "b", "Optimistic spring imagery", "easy"),
        _q("Nirala is also known as:", ["Father of Hindi cinema", "Mahapran (great soul) of Hindi poetry", "Painter", "Statesman"], "b", "Honorific 'Mahapran'", "hard"),
        _q("Spring season in Hindi is:", ["Sharad", "Vasant", "Hemant", "Greeshm"], "b", "Vasant ritu", "easy"),
    ],
    ("Lakh Ki Chudiyan - Quiz", 8): [
        _q("Bangle making is a/an:", ["Modern factory job", "Traditional artisan craft", "Software job", "Banking job"], "b", "Traditional handicraft", "easy"),
        _q("'Manihari' refers to:", ["Soldier", "Bangle seller / maker", "Doctor", "Teacher"], "b", "One who makes/sells bangles", "medium"),
        _q("Story shows the loss of traditional crafts due to:", ["Better health", "Mass-produced goods replacing them", "Better roads", "More schools"], "b", "Mass production wipes out artisans", "medium"),
    ],
    ("Bus Ki Yatra - Quiz", 8): [
        _q("Author Harishankar Parsai is known for:", ["Tragedy", "Satire / humour", "Romance", "History only"], "b", "Famous Hindi satirist", "medium"),
        _q("On the bus, passengers were:", ["Comfortable always", "Worried about safety", "Sleeping happily", "Eating food"], "b", "Bus was unsafe", "easy"),
        _q("The story criticises:", ["Trains", "Old, badly maintained public transport", "Cars", "Cycles"], "b", "Negligent transport", "medium"),
    ],
    ("Deewanon Ki Hasti - Quiz", 8): [
        _q("'Deewane' here are:", ["Mad people", "Free-spirited dreamers / wanderers", "Doctors", "Soldiers only"], "b", "Carefree, idealistic people", "medium"),
        _q("They give to the world:", ["Sadness", "Joy, dreams and inspiration", "Money only", "Anger"], "b", "Joy and inspiration", "easy"),
        _q("'Hasti' means:", ["Power", "Existence / being", "Anger", "Friendship"], "b", "Hasti = existence", "medium"),
    ],
    ("Chitthiyon Ki Anoothi Duniya - Quiz", 8): [
        _q("'Anoothi' means:", ["Common", "Unique / extraordinary", "Painful", "Cheap"], "b", "Anoothi = unique", "medium"),
        _q("Hand-written letters give us:", ["Speed only", "A personal touch and lasting memory", "Wealth only", "Worry"], "b", "Personal, intimate touch", "easy"),
        _q("Famous letter-writing pairs include:", ["Nehru–Indira", "Mickey–Donald", "Ram–Sita only", "None"], "a", "Nehru wrote 'Letters from a Father to His Daughter'", "medium"),
    ],
    ("The Best Christmas Present in the World - Quiz", 8): [
        _q("The narrator returns the letter to:", ["The author", "His wife (now elderly Mrs Macpherson)", "The post office", "A museum"], "b", "Returned to Jim's wife", "medium"),
        _q("The Christmas truce was between:", ["Russian and Japanese troops", "British and German troops in WWI", "Indian and British", "French and Spanish"], "b", "British and German soldiers, 1914", "medium"),
        _q("The story celebrates:", ["War", "Peace and humanity even in war", "Greed", "Anger"], "b", "Brief shared humanity in trenches", "easy"),
    ],
    ("The Tsunami - Quiz", 8): [
        _q("Tilly Smith was about ___ years old at the time:", ["5", "10", "15", "20"], "b", "She was about 10", "medium"),
        _q("Animals (e.g. elephants) often sense disasters by:", ["Reading newspapers", "Picking up vibrations and infrasound", "Watching TV", "Magic"], "b", "Sensitive to subtle vibrations", "medium"),
        _q("Tsunamis can be detected today by:", ["Smell", "Seismograph + ocean buoys", "Just looking", "TV"], "b", "Earthquake sensors and DART buoys", "hard"),
    ],
    ("Glimpses of the Past - Quiz", 8): [
        _q("Battle of Plassey (1757) was won by:", ["Marathas", "British East India Company", "Mughals", "French"], "b", "Robert Clive's victory", "medium"),
        _q("Rani Lakshmibai of Jhansi fought in:", ["1857 First War of Independence", "Battle of Panipat", "Kalinga war", "Battle of Plassey"], "a", "Heroine of 1857", "easy"),
        _q("Doctrine of Lapse was used by:", ["Akbar", "Lord Dalhousie", "Gandhi", "Nehru"], "b", "British Governor-General Dalhousie", "medium"),
    ],
    ("Bettadakke Hogi Baa - Quiz", 8): [
        _q("Hill stations in Karnataka include:", ["Hampi", "Nandi Hills, Kemmangundi", "Bengaluru", "Mysuru"], "b", "Famous hill stations", "easy"),
        _q("'Hudugaru' (boys) usually love:", ["Sleeping", "Adventures and outdoor play", "Sitting still", "Eating only"], "b", "Adventure and play", "easy"),
        _q("Spending time in nature helps to:", ["Pollute", "Refresh mind and body", "Cut trees", "Build cities"], "b", "Nature is rejuvenating", "easy"),
    ],
    ("Nanna Baalya - Quiz", 8): [
        _q("Childhood memories often include:", ["Office work", "Friends, school, festivals", "Stock markets", "Bills"], "b", "Friends, school, festivals", "easy"),
        _q("'Aatma-charitre' means:", ["Biography", "Autobiography", "Novel", "Drama"], "b", "Self-written life story", "medium"),
        _q("'Smarane' means:", ["Forgetting", "Memory / recollection", "Sleep", "Anger"], "b", "Smarane = memory", "medium"),
    ],
    ("Akkamahadevi Vachana - Quiz", 8): [
        _q("Akkamahadevi addresses Shiva as:", ["Linga", "Chenna Mallikarjuna", "Vitthala", "Krishna"], "b", "Her ishta-devata = Chenna Mallikarjuna", "medium"),
        _q("She is celebrated for:", ["Wars", "Spiritual courage and women's liberation", "Cooking", "Painting"], "b", "Pioneering woman saint", "medium"),
        _q("She walked away from worldly life at a young age in search of:", ["Wealth", "Spiritual realization (Shiva)", "Power", "Throne"], "b", "Spiritual quest", "medium"),
    ],
    ("Algebraic Expressions and Identities - Quiz", 8): [
        _q("(a − b)² = ?", ["a² + b²", "a² − 2ab + b²", "a² + 2ab + b²", "a² − b²"], "b", "Identity (a−b)²", "medium"),
        _q("a² − b² = ?", ["(a−b)(a+b)", "(a+b)²", "(a−b)²", "ab"], "a", "Difference of squares", "medium"),
        _q("If x + y = 5 and x − y = 3, then x = ?", ["1", "2", "3", "4"], "d", "Adding: 2x=8 → x=4", "medium"),
    ],
    ("Friction - Quiz", 8): [
        _q("Sliding friction is ___ static friction:", ["Greater than", "Less than", "Equal to", "Twice"], "b", "Sliding friction < static friction", "medium"),
        _q("Ball bearings are used to:", ["Increase friction", "Reduce friction in machines", "Heat machines", "Slow them down"], "b", "Roll → less friction", "medium"),
        _q("Friction produces:", ["Cold only", "Heat (e.g. rubbing hands)", "Light only", "Magnetism"], "b", "Friction → heat", "easy"),
    ],
    ("Bepin Choudhury's Lapse of Memory - Quiz", 8): [
        _q("Bepin Babu loved reading:", ["Magazines", "Detective / mystery novels", "Cookbooks", "Newspapers only"], "b", "Loves crime fiction", "medium"),
        _q("Chunilal had a complaint that Bepin:", ["Bullied him", "Refused to help him in his bad time", "Lent him money", "Was generous"], "b", "Refused help when needed", "medium"),
        _q("The story warns against:", ["Memory itself", "Indifference / arrogance towards old friends", "Reading books", "Being rich"], "b", "Don't be arrogant with old friends", "medium"),
    ],
}


EXTRA_GRADE_9 = {
    ("Number Systems - Quiz", 9): [
        _q("Decimal expansion of √2 is:", ["Terminating", "Repeating", "Non-terminating non-repeating", "Whole number"], "c", "Irrational number", "easy"),
        _q("Every integer is a:", ["Irrational", "Rational number", "Imaginary", "Negative"], "b", "Integers ⊂ Rationals", "easy"),
        _q("Smallest natural number:", ["0", "1", "-1", "Does not exist"], "b", "Natural numbers start at 1", "easy"),
    ],
    ("Polynomials - Quiz", 9): [
        _q("p(x) = x² − 4. Then p(2) = ?", ["0", "2", "4", "8"], "a", "4 − 4 = 0", "easy"),
        _q("Number of zeroes a quadratic polynomial can have at most:", ["1", "2", "3", "Many"], "b", "Degree 2 → at most 2 zeros", "medium"),
        _q("(x + y)² = ?", ["x² + y²", "x² + 2xy + y²", "x² − 2xy + y²", "xy"], "b", "Standard identity", "easy"),
    ],
    ("Coordinate Geometry - Quiz", 9): [
        _q("Point on x-axis has y-coordinate:", ["1", "0", "-1", "Any value"], "b", "On x-axis y=0", "easy"),
        _q("Distance of (3,4) from origin:", ["3", "4", "5", "7"], "c", "√(9+16) = 5", "medium"),
        _q("Quadrant of (-2, -3):", ["I", "II", "III", "IV"], "c", "Both negative → Q3", "easy"),
    ],
    ("Linear Equations in Two Variables - Quiz", 9): [
        _q("Number of solutions of x + y = 4:", ["0", "1", "2", "Infinitely many"], "d", "Many (x,y) satisfy this", "medium"),
        _q("Form of every point on the y-axis:", ["(x, 0)", "(0, y)", "(x, y)", "(0, 0)"], "b", "x-coord is 0", "easy"),
        _q("If 3x + 2y = 12, when x = 2, y = ?", ["2", "3", "4", "5"], "b", "6 + 2y = 12 → y = 3", "medium"),
    ],
    ("Introduction to Euclid's Geometry - Quiz", 9): [
        _q("Through 2 distinct points there is:", ["No line", "Exactly one line", "Two lines", "Many lines"], "b", "Exactly one straight line", "easy"),
        _q("Parallel postulate is the:", ["First", "Third", "Fifth postulate", "Sixth"], "c", "Famous 5th postulate", "medium"),
        _q("'Whole is greater than the part' is a/an:", ["Theorem", "Axiom (common notion)", "Postulate", "Definition"], "b", "Common notion / axiom", "medium"),
    ],
    ("Matter in Our Surroundings - Quiz", 9): [
        _q("Particles in a solid have:", ["Maximum freedom", "Least freedom; vibrate in place", "Random fast motion", "No motion"], "b", "Strong forces; particles vibrate", "easy"),
        _q("Boiling point of water at sea level:", ["50°C", "75°C", "100°C", "200°C"], "c", "100°C at 1 atm", "easy"),
        _q("Plasma is found in:", ["Lakes", "Stars / lightning", "Sand", "Wood"], "b", "Stars and lightning are plasma", "hard"),
    ],
    ("Is Matter Around Us Pure? - Quiz", 9): [
        _q("Brass is an example of:", ["Pure compound", "Alloy / homogeneous mixture", "Element", "Suspension"], "b", "Copper + zinc alloy", "medium"),
        _q("Tyndall effect is shown by:", ["Solutions", "Colloids", "Pure water", "Ice cubes"], "b", "Colloid scatters light", "medium"),
        _q("Salt + water is a:", ["Suspension", "Colloid", "Solution", "Compound"], "c", "Homogeneous solution", "easy"),
    ],
    ("Atoms and Molecules - Quiz", 9): [
        _q("Symbol for potassium:", ["P", "Po", "K", "Pt"], "c", "K (Kalium)", "medium"),
        _q("Atomic mass of carbon:", ["6", "12", "14", "16"], "b", "C = 12 u", "easy"),
        _q("Avogadro number ≈:", ["6.022 × 10²³", "3.14", "9.8", "1000"], "a", "Particles in 1 mole", "medium"),
    ],
    ("Structure of the Atom - Quiz", 9): [
        _q("Electron was discovered by:", ["Newton", "J J Thomson", "Bohr", "Rutherford"], "b", "Thomson, 1897", "medium"),
        _q("Atomic number = number of:", ["Neutrons", "Protons", "Electrons + protons", "Atoms"], "b", "Protons in nucleus", "easy"),
        _q("Bohr proposed that electrons revolve in:", ["Random paths", "Fixed orbits / shells", "Straight lines", "Triangular paths"], "b", "Quantised orbits", "medium"),
    ],
    ("The Fundamental Unit of Life - Quiz", 9): [
        _q("Plant cells differ from animal cells by having:", ["No DNA", "Cell wall and chloroplasts", "No nucleus", "Nothing different"], "b", "Cell wall + chloroplasts", "easy"),
        _q("Powerhouse of the cell:", ["Nucleus", "Mitochondrion", "Ribosome", "Vacuole"], "b", "Mitochondria produce ATP", "easy"),
        _q("Site of protein synthesis:", ["Nucleus only", "Ribosome", "Lysosome", "Golgi"], "b", "Ribosomes assemble proteins", "medium"),
    ],
    ("The French Revolution - Quiz", 9): [
        _q("Bastille was a:", ["Palace", "Royal prison-fortress", "Church", "Park"], "b", "Symbol of royal tyranny", "easy"),
        _q("Estates-General consisted of:", ["1 estate", "2 estates", "3 estates", "5 estates"], "c", "Clergy, Nobles, Commoners", "medium"),
        _q("'Reign of Terror' is associated with:", ["Napoleon", "Robespierre", "Louis XVI", "Mirabeau"], "b", "Robespierre led the Terror", "medium"),
    ],
    ("Socialism in Europe - Quiz", 9): [
        _q("Karl Marx co-wrote the:", ["Das Kapital and Communist Manifesto", "Bible", "Quran", "Wealth of Nations"], "a", "With Friedrich Engels", "medium"),
        _q("Russia changed its capital under Lenin to:", ["St Petersburg", "Moscow", "Kiev", "Minsk"], "b", "Capital moved to Moscow", "medium"),
        _q("Czar Nicholas II was overthrown in:", ["1905", "Feb 1917", "Oct 1917", "1924"], "b", "February Revolution", "hard"),
    ],
    ("Aai - Quiz", 9): [
        _q("'Aaichi maya' literally means:", ["Father's anger", "Mother's love / affection", "Family wealth", "School discipline"], "b", "Mother's love", "easy"),
        _q("In Indian culture, 'Aai' is associated with:", ["Wars", "Care, sacrifice and gentleness", "Politics", "Markets"], "b", "Loving caregiver", "easy"),
        _q("'Vaatsalya' means:", ["Anger", "Motherly affection", "Greed", "Power"], "b", "Tender parental love", "medium"),
    ],
    ("Nagari Manus Gawat Yeto - Quiz", 9): [
        _q("Village life in the lesson is:", ["Stressful", "Slower and rooted in nature", "Hi-tech", "Modern only"], "b", "Calm, nature-rooted", "easy"),
        _q("City life is shown as:", ["Calm", "Fast-paced and stressful", "Boring", "Empty"], "b", "Hectic, stressful", "easy"),
        _q("Theme of the piece is:", ["Hating villages", "Cultural contrast", "Politics only", "Cooking"], "b", "City vs village contrast", "medium"),
    ],
    ("Marathi Bana - Quiz", 9): [
        _q("Maharashtra is bordered by:", ["Pakistan", "Karnataka, Goa, Telangana, MP, Gujarat", "Nepal", "Bangladesh"], "b", "Multi-state borders", "medium"),
        _q("Sant Tukaram and Dnyaneshwar were:", ["Mathematicians", "Marathi saint-poets (bhakti)", "Soldiers", "Architects"], "b", "Bhakti saints of Maharashtra", "medium"),
        _q("Marathi script is:", ["Tamil", "Devanagari", "Latin", "Arabic"], "b", "Devanagari (like Hindi)", "easy"),
    ],
    ("Swapna Banatat - Quiz", 9): [
        _q("Dreams without effort remain:", ["Reality", "Just dreams (un-realised)", "Money", "Songs"], "b", "Effort makes dreams real", "easy"),
        _q("'Aakaanksha' means:", ["Fear", "Aspiration / desire", "Sleep", "Anger"], "b", "Aakaanksha = aspiration", "medium"),
        _q("Lesson encourages:", ["Day-dreaming", "Positive ambition with hard work", "Quitting", "Fear of future"], "b", "Aim high + work hard", "easy"),
    ],
    ("The Fun They Had - Quiz", 9): [
        _q("In the story, books are:", ["Common", "Almost extinct", "Banned", "Eaten"], "b", "They print on screens, paper books are old curiosities", "easy"),
        _q("Tommy found an old book that was:", ["About maths", "About a school of long ago", "Fiction", "A magazine"], "b", "About old physical schools", "easy"),
        _q("Asimov was a master of:", ["Romance", "Science fiction", "History", "Cooking"], "b", "Sci-fi genre", "easy"),
    ],
    ("The Sound of Music - Quiz", 9): [
        _q("Evelyn Glennie became deaf at age:", ["8", "11", "16", "20"], "b", "Profoundly deaf by 11", "medium"),
        _q("She feels music through:", ["Just ears", "Vibrations in her body", "Smell", "Sight only"], "b", "Vibrations through bare feet, body", "medium"),
        _q("Bismillah Khan made the shehnai famous:", ["Only at home", "On all auspicious occasions internationally", "Only at parties", "Never publicly"], "b", "World-famous shehnai", "easy"),
    ],
    ("The Little Girl - Quiz", 9): [
        _q("The 'little girl' in the story is:", ["Margie", "Kezia", "Anne", "Helen"], "b", "Kezia is the protagonist", "easy"),
        _q("The story is set in:", ["India", "New Zealand", "Russia", "USA"], "b", "Mansfield wrote about NZ life", "medium"),
        _q("The father seemed harsh because he was:", ["Cruel always", "Tired and stressed from work", "A criminal", "Very young"], "b", "Stress, not cruelty", "medium"),
    ],
    ("A Truly Beautiful Mind - Quiz", 9): [
        _q("Einstein moved from Germany to:", ["China", "USA", "Brazil", "Australia"], "b", "Fled Nazi Germany to USA, 1933", "easy"),
        _q("Einstein wrote a famous letter to ___ warning about atomic weapons:", ["Hitler", "President Roosevelt", "Stalin", "Churchill"], "b", "F D Roosevelt, 1939", "medium"),
        _q("Einstein worked tirelessly later for:", ["Wars", "World peace and disarmament", "More bombs", "Politics only"], "b", "Peace and disarmament", "easy"),
    ],
    ("Triangles - Quiz", 9): [
        _q("ASA congruence requires:", ["3 sides", "2 angles + included side", "3 angles", "2 sides + 1 angle"], "b", "Angle-Side-Angle", "medium"),
        _q("Two triangles with all 3 angles equal are:", ["Always congruent", "Similar (not necessarily congruent)", "Identical sized always", "Different always"], "b", "Equal angles → similar", "medium"),
        _q("In triangle inequality, side c is:", ["≥ a + b", "= a + b", "< a + b", "Doesn't matter"], "c", "Sum of two sides > third side", "medium"),
    ],
    ("Force and Laws of Motion - Quiz", 9): [
        _q("SI unit of force:", ["Joule", "Newton", "Watt", "Pascal"], "b", "1 N = 1 kg·m/s²", "easy"),
        _q("Momentum = ?", ["mass × velocity", "force × time", "Both a and b", "mass × acceleration"], "c", "p = m·v; impulse = F·Δt = Δp", "medium"),
        _q("A jet plane moves forward as it pushes air ___:", ["Forward", "Backward", "Sideways", "Up"], "b", "Newton's 3rd law: opposite reaction", "easy"),
    ],
    ("My Childhood (Abdul Kalam) - Quiz", 9): [
        _q("Kalam's first job at age 9-10 was:", ["Selling milk", "Distributing newspapers", "Tailoring", "Driving"], "b", "Sold newspapers to support family", "medium"),
        _q("His friend Ramanadha Sastry's father was a:", ["Soldier", "Hindu priest (head of temple)", "Doctor", "Farmer"], "b", "Pakshi Lakshmana Sastry", "medium"),
        _q("Lesson teaches that India's strength is in:", ["War", "Unity in diversity", "Greed", "Isolation"], "b", "Communal harmony", "easy"),
    ],
}


EXTRA_GRADE_10 = {
    ("Real Numbers - Quiz", 10): [
        _q("Fundamental Theorem of Arithmetic states every composite number can be uniquely written as product of:", ["Even numbers", "Primes", "Squares", "Cubes"], "b", "Unique prime factorisation", "easy"),
        _q("HCF(96, 404) = ?", ["2", "4", "8", "16"], "b", "Euclid: gives 4", "hard"),
        _q("LCM(12, 15, 21) = ?", ["210", "180", "420", "60"], "c", "12=2²·3; 15=3·5; 21=3·7 → 2²·3·5·7=420", "hard"),
    ],
    ("Polynomials - Quiz", 10): [
        _q("If α and β are zeroes of x² − 7x + 12, α + β = ?", ["7", "-7", "12", "-12"], "a", "Sum of zeroes = -b/a = 7", "medium"),
        _q("Zero of p(x) = 2x − 6 is:", ["1", "2", "3", "6"], "c", "2x = 6 → x = 3", "easy"),
        _q("A polynomial of degree 3 is called:", ["Linear", "Quadratic", "Cubic", "Biquadratic"], "c", "Cubic = degree 3", "easy"),
    ],
    ("Pair of Linear Equations - Quiz", 10): [
        _q("If a₁/a₂ = b₁/b₂ ≠ c₁/c₂, the lines are:", ["Intersecting", "Parallel (no solution)", "Coincident", "Curved"], "b", "Inconsistent → no solution", "medium"),
        _q("Solve 3x + y = 9; x + y = 5:", ["x=2, y=3", "x=3, y=2", "x=4, y=1", "x=1, y=4"], "a", "Subtract: 2x=4 → x=2; y=3", "medium"),
        _q("Solving by 'elimination' means:", ["Removing a variable", "Multiplying equations only", "Adding once", "Plotting graphs"], "a", "Eliminate one variable", "easy"),
    ],
    ("Quadratic Equations - Quiz", 10): [
        _q("Nature of roots if discriminant D > 0:", ["No real roots", "Two distinct real roots", "Equal real roots", "Imaginary"], "b", "D > 0 → 2 distinct real", "easy"),
        _q("If D = 0, roots are:", ["Distinct real", "Equal real", "Imaginary", "Negative only"], "b", "Repeated/equal real roots", "easy"),
        _q("Roots of 2x² − 7x + 3 = 0:", ["1, 3", "3, 1/2", "2, 3", "3/2, 1"], "b", "Factor: (2x-1)(x-3) → x=1/2,3", "hard"),
    ],
    ("Arithmetic Progressions - Quiz", 10): [
        _q("First term a=2, common difference d=3. Find a₁₀:", ["29", "30", "31", "32"], "a", "a + 9d = 2 + 27 = 29", "medium"),
        _q("Sum of first 5 natural numbers:", ["10", "12", "15", "20"], "c", "5·6/2 = 15", "easy"),
        _q("Is 0, 4, 8, 12, ... an AP? Common difference?", ["Yes, 0", "Yes, 4", "No", "Yes, 2"], "b", "Constant difference 4", "easy"),
    ],
    ("Chemical Reactions and Equations - Quiz", 10): [
        _q("Mg + 2HCl → ?", ["MgCl₂ + H₂", "MgCl + 2H", "Mg + Cl₂ + H₂", "Mg(OH)₂"], "a", "Single displacement", "medium"),
        _q("Decomposition reaction example:", ["2HgO → 2Hg + O₂", "Na + Cl → NaCl", "C + O₂ → CO₂", "Mg + O₂ → MgO"], "a", "AB → A + B", "medium"),
        _q("Endothermic reaction ___ heat:", ["Releases", "Absorbs", "Ignores", "Burns"], "b", "Endo = takes in heat", "medium"),
    ],
    ("Acids, Bases and Salts - Quiz", 10): [
        _q("Vinegar contains:", ["HCl", "Acetic acid", "Citric acid", "Sulphuric acid"], "b", "CH₃COOH (~5%)", "easy"),
        _q("Plaster of Paris formula:", ["CaSO₄·½H₂O", "CaCO₃", "NaOH", "NaCl"], "a", "Hemihydrate of CaSO₄", "hard"),
        _q("Common salt is also called:", ["Washing soda", "Baking soda", "Rock salt", "Sodium chloride (NaCl)"], "d", "NaCl is common salt", "easy"),
    ],
    ("Metals and Non-metals - Quiz", 10): [
        _q("Most malleable metal:", ["Iron", "Gold", "Copper", "Aluminium"], "b", "Gold can be hammered into thin sheets", "medium"),
        _q("Best conductors of electricity:", ["Silver and copper", "Iron only", "Sulphur", "Sodium only"], "a", "Silver is best, copper close", "medium"),
        _q("Reactivity series: most reactive at top is:", ["Gold", "Sodium / potassium", "Copper", "Iron"], "b", "K > Na > Ca > Mg ...", "medium"),
    ],
    ("Carbon and its Compounds - Quiz", 10): [
        _q("Compound CH₃COOH is:", ["Methane", "Ethanoic acid (acetic acid)", "Ethanol", "Glucose"], "b", "Vinegar / acetic acid", "easy"),
        _q("Diamond and graphite are ___ of carbon:", ["Compounds", "Allotropes", "Elements only", "Mixtures"], "b", "Different forms (allotropes)", "medium"),
        _q("Functional group of alcohols:", ["−COOH", "−OH", "−CHO", "−NH₂"], "b", "Hydroxyl group", "medium"),
    ],
    ("Life Processes - Quiz", 10): [
        _q("Inhaled air is rich in:", ["CO₂", "Oxygen", "Hydrogen", "Helium"], "b", "We breathe in O₂", "easy"),
        _q("Heart of a human has how many chambers?", ["1", "2", "3", "4"], "d", "2 atria + 2 ventricles", "easy"),
        _q("Filtering unit in kidneys:", ["Neuron", "Nephron", "Alveolus", "Villi"], "b", "Nephron filters blood", "medium"),
    ],
    ("Jnanapeeta Puraskrutha Lekhakaru - Quiz", 10): [
        _q("Shivaram Karanth received Jnanapeetha for:", ["Mookajjiya Kanasugalu", "Naaku Tanti", "Yayati", "Karvalo"], "a", "1977 award for that novel", "hard"),
        _q("Masti Venkatesha Iyengar's Jnanapeetha was for:", ["Chikkaveera Rajendra", "Karvalo", "Naaku Tanti", "Avalokana"], "a", "1983 award", "hard"),
        _q("U R Ananthamurthy is famous for:", ["Samskara", "Yayati", "Mookajjiya Kanasugalu", "Karvalo"], "a", "Samskara — modern Kannada classic", "medium"),
    ],
    ("Karnataka Ekikarana - Quiz", 10): [
        _q("Aluru Venkata Rao is regarded as the:", ["First CM of Karnataka", "Father of Karnataka unification movement", "Founder of Karnataka", "First Governor"], "b", "Karnataka Kulapurohita", "medium"),
        _q("Before unification, Karnataka regions were under:", ["1 ruler", "Several British/princely jurisdictions", "Maratha empire only", "Mughals only"], "b", "Bombay, Madras, Hyderabad, Mysore etc", "medium"),
        _q("Mysore State was renamed Karnataka in:", ["1956", "1969", "1973", "1980"], "c", "1 Nov 1973 — Karnataka Naamakarana", "medium"),
    ],
    ("Dheera Naari Abbakka Rani - Quiz", 10): [
        _q("Abbakka Rani is sometimes called:", ["Rani Lakshmi of Karnataka", "Abhaya Rani", "Chowta Rani / Veera Rani", "Sea Queen"], "c", "Veera Rani Abbakka", "medium"),
        _q("Capital of her kingdom:", ["Mangaluru", "Ullala", "Mysuru", "Hampi"], "b", "Ullala on Karnataka coast", "medium"),
        _q("She is celebrated as a model of:", ["Greed", "Female courage and resistance", "Surrender", "Cooking"], "b", "Pioneer woman warrior", "easy"),
    ],
    ("Kavirajamarga - Quiz", 10): [
        _q("Genre of Kavirajamarga:", ["Novel", "Treatise on poetics (alankara shastra)", "Drama", "Folk song"], "b", "Earliest poetics in Kannada", "medium"),
        _q("Author traditionally credited:", ["Kalidasa", "Sri Vijaya / Amoghavarsha", "Pampa", "Janna"], "b", "Sri Vijaya (under King Amoghavarsha)", "hard"),
        _q("It mentions a region between which two rivers as 'Kannada-naadu'?", ["Krishna and Kaveri", "Ganga and Yamuna", "Tungabhadra and Godavari", "Indus and Saraswati"], "a", "Krishna to Kaveri", "hard"),
    ],
    ("Manushyatvada Gaana - Quiz", 10): [
        _q("Lesson reminds us:", ["To be ruled by selfishness", "All humans deserve dignity and love", "Greed is good", "Power is everything"], "b", "Universal humanity", "easy"),
        _q("'Daye' means:", ["Anger", "Compassion", "Sleep", "Hunger"], "b", "Daye = compassion", "medium"),
        _q("True greatness in the lesson is:", ["Money", "Service to fellow humans", "Power", "Fame"], "b", "Service to humanity", "easy"),
    ],
    ("A Letter to God - Quiz", 10): [
        _q("Where did Lencho live?", ["A village in Mexico (low ridge)", "USA", "India", "Spain"], "a", "Mexican village", "medium"),
        _q("Lencho asked God for:", ["A house", "100 pesos to replant his crop", "A car", "Land"], "b", "100 pesos to start over", "easy"),
        _q("The post-master organised the money to:", ["Cheat Lencho", "Strengthen his faith in God", "Punish him", "Tax him"], "b", "Wanted Lencho's faith preserved", "medium"),
    ],
    ("Nelson Mandela: Long Walk to Freedom - Quiz", 10): [
        _q("Apartheid means:", ["Equality", "Strict racial separation policy", "Friendship", "Democracy"], "b", "Afrikaans: 'apart-ness'", "easy"),
        _q("Mandela's political party:", ["BJP", "Congress", "ANC (African National Congress)", "Labour"], "c", "ANC", "easy"),
        _q("Mandela won the Nobel Peace Prize in:", ["1990", "1993", "2000", "2010"], "b", "1993, jointly with F W de Klerk", "medium"),
    ],
    ("Two Stories about Flying - Quiz", 10): [
        _q("'The Black Aeroplane' was written by:", ["Frederick Forsyth", "James Herriot", "Liam O'Flaherty", "George Orwell"], "a", "Frederick Forsyth", "medium"),
        _q("In the story, the Dakota plane was flying over:", ["English Channel", "Bay of Bengal", "Red Sea", "Pacific"], "a", "Crossing English Channel", "medium"),
        _q("'His First Flight' was written by:", ["Liam O'Flaherty", "Forsyth", "Tagore", "Frost"], "a", "Liam O'Flaherty", "medium"),
    ],
    ("Trigonometry (Introduction) - Quiz", 10): [
        _q("sin² θ + cos² θ = ?", ["0", "1", "tan θ", "Undefined"], "b", "Pythagorean identity", "easy"),
        _q("cos 60° = ?", ["0", "1/2", "√3/2", "1"], "b", "cos 60° = 1/2", "easy"),
        _q("sec θ = 1 / ?", ["sin θ", "cos θ", "tan θ", "cot θ"], "b", "sec = reciprocal of cos", "medium"),
    ],
    ("Light – Reflection and Refraction - Quiz", 10): [
        _q("Image formed by a plane mirror is:", ["Real and inverted", "Virtual, erect, same size", "Real, magnified", "Virtual, inverted"], "b", "Plane mirror image", "easy"),
        _q("Speed of light in vacuum (approx):", ["3 × 10⁸ m/s", "3 × 10⁵ m/s", "3 × 10⁶ m/s", "3 × 10² m/s"], "a", "About 300,000 km/s", "medium"),
        _q("A convex lens is also called:", ["Diverging", "Converging", "Plane", "Concave"], "b", "Convex converges light", "medium"),
    ],
    ("From the Diary of Anne Frank - Quiz", 10): [
        _q("Anne's diary was first published in:", ["1947", "1957", "1967", "1977"], "a", "1947 by her father Otto Frank", "medium"),
        _q("She received the diary as a:", ["Christmas gift", "13th birthday gift", "Wedding gift", "School prize"], "b", "13th birthday, June 12, 1942", "medium"),
        _q("Diary's secret confidante was named:", ["Sophie", "Margot", "Kitty", "Lily"], "c", "She wrote letters to 'Kitty'", "medium"),
    ],
}


EXTRA_BANK = {
    **EXTRA_GRADE_1,
    **EXTRA_GRADE_2,
    **EXTRA_GRADE_3,
    **EXTRA_GRADE_4,
    **EXTRA_GRADE_5,
    **EXTRA_GRADE_6,
    **EXTRA_GRADE_7,
    **EXTRA_GRADE_8,
    **EXTRA_GRADE_9,
    **EXTRA_GRADE_10,
}


class Command(BaseCommand):
    help = "Add MORE questions to every existing quiz across all 10 grades."

    def handle(self, *args, **options):
        added = 0
        unmatched = []
        skipped = 0

        for quiz in Quiz.objects.all().order_by('grade', 'subject', 'title'):
            key = (quiz.title, quiz.grade)
            if key not in EXTRA_BANK:
                unmatched.append(f"G{quiz.grade} {quiz.subject}: {quiz.title}")
                continue

            for qd in EXTRA_BANK[key]:
                obj, created = Question.objects.get_or_create(
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
                if created:
                    added += 1
                else:
                    skipped += 1

            # Update num_questions to match actual count
            quiz.num_questions = quiz.questions.count()
            quiz.save(update_fields=["num_questions"])

        self.stdout.write(self.style.SUCCESS(
            f"\nAdded {added} new questions, skipped {skipped} duplicates."
        ))
        if unmatched:
            self.stdout.write(self.style.WARNING(
                f"  No extra-question bank entry for {len(unmatched)} quizzes:"
            ))
            for t in unmatched[:30]:
                self.stdout.write(f"    - {t}")
            if len(unmatched) > 30:
                self.stdout.write(f"    ... and {len(unmatched) - 30} more")
