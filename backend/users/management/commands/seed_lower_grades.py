"""
python manage.py seed_lower_grades

Adds chapters, quizzes and real curriculum questions for Grades 1, 2, 3 and 4
across Maths, English, EVS (as 'science') and Kannada.

Safe to re-run — only fills empty/placeholder quizzes; existing real
questions are left alone.
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

    # ─── GRADE 1 ─────────────────────────────────────────────────────────
    # Maths
    (1, "maths", 1, "Numbers 1 to 9", [
        _q("How many fingers are there on one hand?", ["3", "4", "5", "6"], "c", "We have 5 fingers on each hand", "easy"),
        _q("The number that comes just after 5 is:", ["3", "4", "6", "7"], "c", "Counting: 5, 6 next", "easy"),
        _q("How many wheels does a bicycle have?", ["1", "2", "3", "4"], "b", "Bi = 2 wheels", "easy"),
    ]),
    (1, "maths", 2, "Numbers 10 to 20", [
        _q("Number that comes after 9 is:", ["8", "10", "11", "12"], "b", "9 + 1 = 10", "easy"),
        _q("How many fingers in total on both hands?", ["8", "9", "10", "12"], "c", "5 + 5 = 10", "easy"),
        _q("Which number is between 12 and 14?", ["11", "13", "15", "16"], "b", "12, 13, 14", "easy"),
    ]),
    (1, "maths", 3, "Addition", [
        _q("2 + 3 = ?", ["4", "5", "6", "7"], "b", "2 + 3 = 5", "easy"),
        _q("4 + 4 = ?", ["6", "7", "8", "9"], "c", "4 + 4 = 8", "easy"),
        _q("If you have 1 apple and get 2 more, how many in total?", ["2", "3", "4", "5"], "b", "1 + 2 = 3", "easy"),
    ]),
    # English
    (1, "english", 1, "A Happy Child", [
        _q("In the poem, the child is very:", ["Sad", "Happy", "Angry", "Tired"], "b", "Title says 'A Happy Child'", "easy"),
        _q("The child's house has many:", ["Cars", "Windows and doors", "Phones", "Books"], "b", "House described with windows and doors", "easy"),
        _q("Where does the happy child play?", ["In school", "Around the house", "On a boat", "In a hospital"], "b", "Around the house", "easy"),
    ]),
    (1, "english", 2, "Three Little Pigs", [
        _q("The first pig built his house from:", ["Bricks", "Straw", "Wood", "Stone"], "b", "Straw was easy and quick", "easy"),
        _q("Who blew the houses down?", ["A wolf", "A lion", "A bear", "A fox"], "a", "The big bad wolf", "easy"),
        _q("Which house was the strongest?", ["Straw house", "Wood house", "Brick house", "Glass house"], "c", "The brick house could not be blown down", "easy"),
    ]),
    (1, "english", 3, "After a Bath", [
        _q("After a bath we feel:", ["Dirty", "Fresh and clean", "Tired", "Hungry"], "b", "Bath makes us fresh", "easy"),
        _q("We dry ourselves with a:", ["Mat", "Towel", "Pillow", "Soap"], "b", "Towel dries the body", "easy"),
        _q("Daily bath keeps us:", ["Sick", "Healthy and clean", "Lazy", "Sleepy"], "b", "Cleanliness keeps germs away", "easy"),
    ]),
    # EVS (taught as 'science' in DB)
    (1, "science", 1, "My Body", [
        _q("How many eyes do we have?", ["1", "2", "3", "4"], "b", "Two eyes", "easy"),
        _q("We hear with our:", ["Eyes", "Ears", "Nose", "Mouth"], "b", "Ears help us hear", "easy"),
        _q("We smell with our:", ["Mouth", "Nose", "Hands", "Feet"], "b", "Nose is for smelling", "easy"),
    ]),
    (1, "science", 2, "My Family", [
        _q("Father's father is your:", ["Uncle", "Grandfather", "Brother", "Cousin"], "b", "Grandfather", "easy"),
        _q("Mother's daughter (other than you) is your:", ["Aunt", "Sister", "Friend", "Cousin"], "b", "Sister", "easy"),
        _q("A family with parents, children, grandparents is called a:", ["Small family", "Joint family", "Empty family", "Single family"], "b", "Joint family", "easy"),
    ]),
    (1, "science", 3, "Animals Around Us", [
        _q("A cow gives us:", ["Wool", "Milk", "Honey", "Eggs"], "b", "We drink cow's milk", "easy"),
        _q("Which animal lays eggs?", ["Cow", "Dog", "Hen", "Goat"], "c", "Hens lay eggs", "easy"),
        _q("A baby dog is called a:", ["Calf", "Kitten", "Puppy", "Foal"], "c", "Baby dog = puppy", "easy"),
    ]),
    # Kannada
    (1, "kannada", 1, "Aksharagalu", [
        _q("'Aksharagalu' means:", ["Numbers", "Letters / alphabets", "Songs", "Games"], "b", "Aksharagalu = alphabet letters", "easy"),
        _q("How many vowels (swaragalu) are in Kannada?", ["10", "13", "16", "20"], "b", "13 swaragalu", "medium"),
        _q("First letter of Kannada alphabet is:", ["ಅ (a)", "ಕ (ka)", "ಗ (ga)", "ನ (na)"], "a", "ಅ is the first vowel", "easy"),
    ]),
    (1, "kannada", 2, "Bannagalu (Colours)", [
        _q("'Kempu' is which colour?", ["Blue", "Red", "Green", "Yellow"], "b", "Kempu = red", "easy"),
        _q("'Hasiru' is which colour?", ["Red", "Green", "Yellow", "White"], "b", "Hasiru = green", "easy"),
        _q("Sky is what colour?", ["Neeli (blue)", "Kempu (red)", "Hasiru (green)", "Hasiru-yellow"], "a", "Neeli = blue", "easy"),
    ]),
    (1, "kannada", 3, "Praaningalu (Animals)", [
        _q("'Naayi' means:", ["Cat", "Dog", "Cow", "Goat"], "b", "Naayi = dog", "easy"),
        _q("'Hasu' means:", ["Cow", "Cat", "Horse", "Bird"], "a", "Hasu = cow", "easy"),
        _q("'Bekku' means:", ["Cat", "Dog", "Mouse", "Rabbit"], "a", "Bekku = cat", "easy"),
    ]),

    # ─── GRADE 2 ─────────────────────────────────────────────────────────
    # Maths
    (2, "maths", 1, "What is Long, What is Round?", [
        _q("Which of these is round?", ["A pencil", "A ball", "A book", "A ruler"], "b", "Ball is round", "easy"),
        _q("A long straight thing is a:", ["Ball", "Stick / pencil", "Plate", "Coin"], "b", "Stick is long", "easy"),
        _q("Wheels of a car are:", ["Square", "Round", "Triangle", "Long"], "b", "Wheels are round so they roll", "easy"),
    ]),
    (2, "maths", 2, "Counting in Groups", [
        _q("Skip count by 2: 2, 4, 6, ?", ["7", "8", "9", "10"], "b", "Add 2: 6 + 2 = 8", "easy"),
        _q("How many tens make 30?", ["1", "2", "3", "4"], "c", "10 × 3 = 30", "easy"),
        _q("5 + 5 + 5 = ?", ["10", "15", "20", "25"], "b", "Three 5s = 15", "easy"),
    ]),
    (2, "maths", 3, "Addition and Subtraction", [
        _q("12 + 7 = ?", ["18", "19", "20", "21"], "b", "12 + 7 = 19", "easy"),
        _q("20 − 8 = ?", ["10", "11", "12", "13"], "c", "20 − 8 = 12", "easy"),
        _q("Sita has 15 sweets and gives 5. How many left?", ["5", "8", "10", "20"], "c", "15 − 5 = 10", "medium"),
    ]),
    # English
    (2, "english", 1, "First Day at School", [
        _q("On the first day, the child feels:", ["Bored", "A little nervous and excited", "Sad always", "Angry"], "b", "New experience = mixed feelings", "easy"),
        _q("At school children meet new:", ["Trees", "Friends and teachers", "Cars", "Animals"], "b", "Friends and teachers", "easy"),
        _q("School helps us to:", ["Sleep", "Learn and grow", "Cook", "Fight"], "b", "Learning is the goal", "easy"),
    ]),
    (2, "english", 2, "I am Lucky", [
        _q("In the poem, the child feels lucky to be:", ["Rich", "Themselves (any creature they imagine)", "Tall", "Famous"], "b", "Each verse celebrates a different creature", "medium"),
        _q("The poem tells us we should:", ["Hate ourselves", "Be happy with who we are", "Copy others", "Be sad"], "b", "Be content with who we are", "easy"),
        _q("Being 'lucky' here mostly means:", ["Having gold", "Being happy / content", "Winning a race", "Eating sweets"], "b", "Happy / content", "medium"),
    ]),
    (2, "english", 3, "Mr. Nobody", [
        _q("Who breaks things in the house according to the poem?", ["Mother", "Mr. Nobody", "The cat", "The wind"], "b", "Mr. Nobody — a fun way to blame nobody", "easy"),
        _q("Mr. Nobody is actually:", ["A real person", "Imaginary — children blame him", "A pet", "A neighbour"], "b", "Imaginary scapegoat", "easy"),
        _q("The poem teaches us to:", ["Always blame others", "Take responsibility", "Run away", "Cry"], "b", "Take responsibility for our actions", "medium"),
    ]),
    # EVS
    (2, "science", 1, "Plants Around Us", [
        _q("Plants need ___ to grow.", ["Only soil", "Water, sunlight and air", "Only milk", "Only colours"], "b", "Plants need water, sunlight, air", "easy"),
        _q("Mango grows on a:", ["Bush", "Creeper", "Tree", "Grass"], "c", "Mango is a tree", "easy"),
        _q("Roses grow on a:", ["Tree", "Shrub / bush with thorns", "Creeper", "Grass"], "b", "Rose is a shrub", "easy"),
    ]),
    (2, "science", 2, "Animals", [
        _q("Animals that eat only plants are:", ["Carnivores", "Herbivores", "Omnivores", "Insects"], "b", "Cow, goat = herbivores", "easy"),
        _q("Lion is a:", ["Herbivore", "Carnivore (meat-eater)", "Omnivore", "Insect"], "b", "Lion eats other animals", "easy"),
        _q("Animals that live in water are called:", ["Aerial", "Terrestrial", "Aquatic", "Wild"], "c", "Aquatic = water-living", "medium"),
    ]),
    (2, "science", 3, "Water", [
        _q("Water becomes ice when it is:", ["Heated", "Cooled below 0°C", "Boiled", "Mixed with sugar"], "b", "Freezing point of water = 0°C", "easy"),
        _q("Water becomes vapour when:", ["Cooled", "Heated", "Frozen", "Stirred"], "b", "Heating water → steam/vapour", "easy"),
        _q("Drinking unclean water causes:", ["Strength", "Diseases", "Happiness", "Energy"], "b", "Dirty water → illness", "easy"),
    ]),
    # Kannada
    (2, "kannada", 1, "Hannugalu (Fruits)", [
        _q("'Mavinahannu' is which fruit?", ["Apple", "Mango", "Banana", "Orange"], "b", "Mavinahannu = mango", "easy"),
        _q("'Bale hannu' is:", ["Mango", "Banana", "Pomegranate", "Apple"], "b", "Bale = banana", "easy"),
        _q("'Sebina hannu' is:", ["Apple", "Banana", "Mango", "Guava"], "a", "Sebu = apple", "easy"),
    ]),
    (2, "kannada", 2, "Tarakaarigalu (Vegetables)", [
        _q("'Aalugadde' is:", ["Onion", "Potato", "Tomato", "Carrot"], "b", "Aalugadde = potato", "easy"),
        _q("'Eeruli' is:", ["Onion", "Garlic", "Potato", "Beetroot"], "a", "Eeruli = onion", "easy"),
        _q("'Tomatohannu' / 'Tomato' is what colour?", ["Green", "Red", "Yellow", "Black"], "b", "Ripe tomato is red", "easy"),
    ]),
    (2, "kannada", 3, "Naadina Geethe", [
        _q("'Naadu' means:", ["A river", "A nation / homeland", "A song", "A market"], "b", "Naadu = country/homeland", "easy"),
        _q("National anthem of India is:", ["Vande Mataram", "Jana Gana Mana", "Saare Jahan Se Achha", "Jai Hind"], "b", "Jana Gana Mana", "easy"),
        _q("Karnataka's state anthem is:", ["Jaya Bharata Jananiya", "Vande Mataram", "Naadu Naadu", "Jai Karnataka"], "a", "'Jaya Bharata Jananiya Tanujate' by Kuvempu", "medium"),
    ]),

    # ─── GRADE 3 ─────────────────────────────────────────────────────────
    # Maths
    (3, "maths", 1, "Numbers 100 to 1000", [
        _q("Which is greater: 234 or 243?", ["234", "243", "Equal", "Cannot tell"], "b", "Tens place: 4 > 3", "easy"),
        _q("Place value of 5 in 256:", ["5", "50", "500", "5000"], "b", "5 is in tens place", "medium"),
        _q("Number that comes after 999 is:", ["100", "1000", "9999", "9990"], "b", "999 + 1 = 1000", "easy"),
    ]),
    (3, "maths", 2, "Give and Take (Subtraction)", [
        _q("85 − 27 = ?", ["48", "58", "62", "68"], "b", "85 − 27 = 58", "easy"),
        _q("100 − 47 = ?", ["43", "53", "63", "73"], "b", "100 − 47 = 53", "easy"),
        _q("If Ravi had 50 marbles and gave away 18, how many left?", ["28", "32", "38", "42"], "b", "50 − 18 = 32", "medium"),
    ]),
    (3, "maths", 3, "Multiplication", [
        _q("4 × 6 = ?", ["18", "20", "24", "28"], "c", "4 × 6 = 24", "easy"),
        _q("7 × 5 = ?", ["30", "35", "40", "42"], "b", "7 × 5 = 35", "easy"),
        _q("3 boxes of 8 chocolates each = ___ chocolates", ["16", "20", "24", "28"], "c", "3 × 8 = 24", "medium"),
    ]),
    # English
    (3, "english", 1, "Good Morning", [
        _q("The poem 'Good Morning' wishes:", ["Sad night", "A pleasant morning to nature & people", "A storm", "Rain only"], "b", "Cheerful greeting", "easy"),
        _q("Birds in the poem are:", ["Sleeping", "Singing / chirping", "Dead", "Flying away forever"], "b", "Singing in the morning", "easy"),
        _q("The poem makes us feel:", ["Tired", "Fresh and happy", "Sad", "Hungry"], "b", "Cheerful", "easy"),
    ]),
    (3, "english", 2, "The Magic Garden", [
        _q("In the story, what was special about the garden?", ["Magical / talking flowers", "It had only weeds", "It was made of stone", "It had no plants"], "a", "Magical garden", "easy"),
        _q("Children took care of the garden by:", ["Trampling it", "Watering and weeding it", "Burning it", "Ignoring it"], "b", "Watering and weeding", "easy"),
        _q("The story teaches us to:", ["Waste plants", "Take care of nature", "Cut all flowers", "Stay indoors"], "b", "Care for nature", "easy"),
    ]),
    (3, "english", 3, "Bird Talk", [
        _q("In the poem, what do the birds talk about?", ["Cars", "Children / people", "Movies", "Food only"], "b", "They gossip about people", "easy"),
        _q("The poem is told from the point of view of:", ["A child", "Birds", "A teacher", "A dog"], "b", "Birds chatting on a branch", "medium"),
        _q("The poem is mainly:", ["Sad", "Funny / playful", "Scary", "Boring"], "b", "Light, humorous tone", "easy"),
    ]),
    # EVS
    (3, "science", 1, "Living and Non-living", [
        _q("Which is a living thing?", ["A book", "A tree", "A pencil", "A cup"], "b", "Trees grow and reproduce", "easy"),
        _q("Living things can:", ["Only sit still", "Grow, eat, breathe", "Be made of stone", "Last forever"], "b", "All living traits", "easy"),
        _q("Which of these is non-living?", ["Cat", "Plant", "Stone", "Fish"], "c", "Stone has no life", "easy"),
    ]),
    (3, "science", 2, "Foods We Eat", [
        _q("Foods that give us energy:", ["Carbohydrates (rice, roti)", "Plastic", "Stones", "Paper"], "a", "Carbs give energy", "easy"),
        _q("Milk is rich in:", ["Iron only", "Protein and calcium", "Salt", "Sugar only"], "b", "Milk = protein + calcium", "medium"),
        _q("Fruits and vegetables provide:", ["Only fat", "Vitamins and minerals", "Plastic", "Sugar only"], "b", "Vitamins and minerals", "easy"),
    ]),
    (3, "science", 3, "Plants Around Us", [
        _q("Big plants with thick stems are called:", ["Herbs", "Shrubs", "Trees", "Grass"], "c", "Trees are tall with woody trunks", "easy"),
        _q("Small soft-stemmed plants are:", ["Trees", "Herbs", "Shrubs", "Vines"], "b", "Herbs (e.g. mint, coriander)", "medium"),
        _q("Plants that climb on a support are:", ["Trees", "Creepers / climbers", "Shrubs", "Herbs"], "b", "Creepers like money plant", "medium"),
    ]),
    # Kannada
    (3, "kannada", 1, "Belakhinaha (Dawn)", [
        _q("'Belakhu' means:", ["Light", "Dark", "Cold", "Hot"], "a", "Belakhu = light", "easy"),
        _q("Dawn / sunrise in Kannada is:", ["Sandhya", "Belakhinaha / Munjane", "Madhyahna", "Raatri"], "b", "Munjane = morning", "medium"),
        _q("At dawn the sky becomes:", ["Dark", "Bright with sunlight", "Black", "Stormy always"], "b", "Sun rises and sky brightens", "easy"),
    ]),
    (3, "kannada", 2, "Karnataka Hesarugalu (Famous places)", [
        _q("Capital of Karnataka:", ["Mysuru", "Bengaluru", "Hubballi", "Mangaluru"], "b", "Bengaluru is the capital", "easy"),
        _q("Famous palace city of Karnataka:", ["Bengaluru", "Mysuru", "Bidar", "Belgaum"], "b", "Mysuru Palace", "easy"),
        _q("Coastal city in Karnataka:", ["Hubballi", "Mangaluru", "Mysuru", "Tumakuru"], "b", "Mangaluru is on the coast", "medium"),
    ]),
    (3, "kannada", 3, "Naadu Naadina Heggalike (Country pride)", [
        _q("Our country is:", ["Karnataka", "Bharata / India", "Bengaluru", "Mysuru"], "b", "Bharata = India", "easy"),
        _q("Karnataka's state language is:", ["Tamil", "Kannada", "Hindi", "Marathi"], "b", "Kannada", "easy"),
        _q("Karnataka was unified on:", ["15 August", "1 November", "26 January", "2 October"], "b", "1 Nov — Karnataka Rajyotsava", "medium"),
    ]),

    # ─── GRADE 4 ─────────────────────────────────────────────────────────
    # Maths
    (4, "maths", 1, "Building with Bricks (Shapes)", [
        _q("A brick has how many faces?", ["4", "6", "8", "12"], "b", "Cuboid has 6 faces", "medium"),
        _q("How many edges does a cube have?", ["8", "10", "12", "16"], "c", "12 edges in a cube", "medium"),
        _q("A circle has how many corners?", ["1", "0", "4", "Many"], "b", "A circle has no corners", "easy"),
    ]),
    (4, "maths", 2, "Long and Short (Measurement)", [
        _q("1 metre = ___ centimetres", ["10", "100", "1000", "10000"], "b", "1 m = 100 cm", "easy"),
        _q("1 km = ___ metres", ["100", "500", "1000", "10000"], "c", "1 km = 1000 m", "easy"),
        _q("Best unit to measure length of a pencil:", ["Kilometre", "Metre", "Centimetre", "Millimetre"], "c", "Pencils are best in cm", "medium"),
    ]),
    (4, "maths", 3, "Multiplication and Division", [
        _q("12 × 5 = ?", ["50", "55", "60", "65"], "c", "12 × 5 = 60", "easy"),
        _q("48 ÷ 6 = ?", ["6", "7", "8", "9"], "c", "48 ÷ 6 = 8", "easy"),
        _q("If 24 sweets are shared equally among 4 children, each gets:", ["4", "5", "6", "8"], "c", "24 ÷ 4 = 6", "medium"),
    ]),
    # English
    (4, "english", 1, "Wake Up", [
        _q("The poem 'Wake Up' is told to a:", ["Sleeping bird", "Sleeping child", "Sleeping fish", "Sleeping cat"], "b", "Mother wakes up child", "easy"),
        _q("In the morning, what calls us to wake up?", ["The night", "Birds singing / sun rising", "Stars", "Moon"], "b", "Morning sounds", "easy"),
        _q("The poem encourages us to:", ["Sleep more", "Get up early and enjoy the day", "Stay indoors", "Cry"], "b", "Get up early", "easy"),
    ]),
    (4, "english", 2, "Neha's Alarm Clock", [
        _q("Neha used many things as alarm clocks. Which one?", ["Her dog", "Her grandmother and pet rooster", "A robot", "A computer"], "b", "She tried different living alarm clocks", "easy"),
        _q("The funniest alarm clock was the:", ["Telephone", "Rooster crowing", "Bell", "Drum"], "b", "Rooster's crow", "easy"),
        _q("In the end Neha learns:", ["To be late", "To wake up on her own", "To skip school", "To sleep all day"], "b", "Self-discipline", "medium"),
    ]),
    (4, "english", 3, "Helen Keller", [
        _q("Helen Keller was unable to:", ["Walk", "See and hear", "Speak only", "Eat"], "b", "She was deaf and blind from childhood", "easy"),
        _q("Her famous teacher was:", ["Anne Sullivan", "Mother Teresa", "Florence Nightingale", "Marie Curie"], "a", "Anne Sullivan taught her language", "medium"),
        _q("Helen Keller's story teaches us:", ["To give up", "Determination overcomes disabilities", "To be lazy", "To stay sad"], "b", "Will power overcomes hardship", "easy"),
    ]),
    # EVS
    (4, "science", 1, "Going to School", [
        _q("Which is a faster mode of transport?", ["Walking", "Bicycle", "Car", "Bullock cart"], "c", "Cars are faster", "easy"),
        _q("In hilly / mountain areas children may go to school by:", ["Boat", "Walking on narrow paths", "Train", "Plane"], "b", "Often a long walk", "medium"),
        _q("In flooded / river areas children may use a:", ["Bicycle", "Boat / canoe", "Train", "Bus"], "b", "Boats cross rivers", "medium"),
    ]),
    (4, "science", 2, "The Story of Amrita (Trees)", [
        _q("Amrita Devi is famous for:", ["Building a palace", "Saving trees by hugging them", "Cooking food", "Painting"], "b", "She gave her life to save khejri trees", "medium"),
        _q("This event happened in which state?", ["Kerala", "Rajasthan (Khejarli)", "Punjab", "Goa"], "b", "Khejarli, Rajasthan, 1730", "hard"),
        _q("Her community is called:", ["Bhils", "Bishnois", "Kols", "Santhals"], "b", "Bishnois protect nature", "medium"),
    ]),
    (4, "science", 3, "Anita and the Honeybees", [
        _q("Honey is collected from:", ["Trees", "Beehives by bees", "Cow", "Goat"], "b", "Bees make honey from nectar", "easy"),
        _q("The leader of a beehive is the:", ["Worker bee", "Queen bee", "Drone", "Soldier"], "b", "Queen bee lays eggs", "medium"),
        _q("Bees help plants by:", ["Eating their leaves", "Pollinating flowers", "Cutting them", "Drying them"], "b", "Pollination helps plants make seeds", "medium"),
    ]),
    # Kannada
    (4, "kannada", 1, "Karnataka Sampada (Heritage)", [
        _q("UNESCO World Heritage site in Karnataka:", ["Hampi", "Taj Mahal", "Red Fort", "Charminar"], "a", "Hampi — Vijayanagara ruins", "medium"),
        _q("Famous classical dance of Karnataka:", ["Bharatanatyam", "Yakshagana", "Kathak", "Mohiniyattam"], "b", "Yakshagana", "medium"),
        _q("Famous waterfall on Sharavati river:", ["Niagara", "Jog Falls", "Athirapally", "Hogenakkal"], "b", "Jog Falls", "easy"),
    ]),
    (4, "kannada", 2, "Janapada Geethegalu (Folk Songs)", [
        _q("'Janapada' means:", ["Royal", "Folk / common people", "Foreign", "Modern"], "b", "Songs of common people", "easy"),
        _q("Folk songs are usually sung:", ["Only in films", "By common people for celebrations and work", "Only in temples", "Only on TV"], "b", "Sung in villages, festivals, fields", "easy"),
        _q("Folk songs preserve a community's:", ["Money", "Culture and traditions", "Buildings", "Crops"], "b", "Cultural heritage", "medium"),
    ]),
    (4, "kannada", 3, "Nadigalu (Rivers of Karnataka)", [
        _q("Which river flows through Mysuru / Bengaluru region?", ["Cauvery", "Ganga", "Yamuna", "Godavari"], "a", "Cauvery is South Karnataka's main river", "medium"),
        _q("'Nadi' means:", ["Mountain", "River", "Forest", "Lake"], "b", "Nadi = river", "easy"),
        _q("Tungabhadra is formed by joining of:", ["Ganga and Yamuna", "Tunga and Bhadra rivers", "Krishna and Cauvery", "Godavari and Krishna"], "b", "Tunga + Bhadra → Tungabhadra", "medium"),
    ]),
]


class Command(BaseCommand):
    help = "Add chapters, quizzes and questions for Grades 1-4 (Maths, English, EVS, Kannada)."

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

        added_quiz = 0
        updated_quiz = 0
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
                # Already filled by a previous run — leave alone
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

            if created:
                added_quiz += 1
            else:
                updated_quiz += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. New quizzes: {added_quiz}, updated: {updated_quiz}, "
            f"skipped (already filled): {skipped}"
        ))
        self.stdout.write(f"Coverage: Grades 1-4, subjects: maths, english, science (EVS), kannada")
