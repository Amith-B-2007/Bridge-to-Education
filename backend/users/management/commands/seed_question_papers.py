"""
python manage.py seed_question_papers

Creates real-format **100-mark question papers** (one per grade, Maths) with
mixed question types totalling 100 marks per paper:

  Section A — 5 × 1 mark   = 5   (MCQs)
  Section B — 5 × 2 marks  = 10  (very short answer)
  Section C — 5 × 3 marks  = 15  (short answer)
  Section D — 5 × 4 marks  = 20  (medium answer)
  Section E — 4 × 5 marks  = 20  (long answer)
  Section F — 3 × 10 marks = 30  (long-form)
                        TOTAL = 100  marks (27 questions)

Stored as Quiz rows with `chapter_number=92` so they show up in the
existing "Past Year Papers" tab. Non-MCQ questions store the model answer
in `explanation` and use empty options.

Idempotent — safe to re-run.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from users.models import Teacher
from resources.models import Subject, Chapter
from quizzes.models import Quiz, Question

User = get_user_model()


def MCQ(text, opts, correct, explanation=""):
    """1-mark MCQ. opts is a 4-tuple of strings."""
    return {
        "text": text,
        "marks": 1,
        "question_type": "mcq",
        "options_json": [{"key": k, "text": v} for k, v in zip(["a", "b", "c", "d"], opts)],
        "correct_answer": correct,
        "explanation": explanation,
        "difficulty": "easy",
    }


def Q(text, marks, model_answer="", qtype=None, difficulty="medium"):
    """Non-MCQ question (short / long / essay)."""
    if qtype is None:
        qtype = (
            "short_answer" if marks <= 3 else
            "long_answer"  if marks <= 5 else
            "essay"
        )
    return {
        "text": text,
        "marks": marks,
        "question_type": qtype,
        "options_json": [],
        "correct_answer": "",
        "explanation": model_answer,
        "difficulty": difficulty,
    }


# (grade, subject, year, paper_title, [questions])
PAPERS = [

    # ─── GRADE 1 — MATHS ─────────────────────────────────────────────────
    (1, "maths", 2024, "Annual Question Paper", [
        # Section A: 5 × 1-mark MCQs
        MCQ("How many fingers are there on one hand?", ["3", "4", "5", "6"], "c"),
        MCQ("Number that comes just after 7 is:", ["6", "8", "9", "5"], "b"),
        MCQ("Smallest number among 4, 2, 7, 3:", ["4", "2", "7", "3"], "b"),
        MCQ("A shape with 3 sides is a:", ["Square", "Triangle", "Circle", "Rectangle"], "b"),
        MCQ("5 + 4 = ?", ["7", "8", "9", "10"], "c"),
        # Section B: 5 × 2-mark short answer
        Q("Write the numbers from 6 to 10 in order.", 2, "6, 7, 8, 9, 10."),
        Q("Find the sum: 8 + 5 = ?", 2, "8 + 5 = 13."),
        Q("Subtract: 14 − 6 = ?", 2, "14 − 6 = 8."),
        Q("Fill in the blanks: 2, 4, 6, 8, ___, ___.", 2, "10, 12 (skip count by 2)."),
        Q("Name any two shapes you see in a clock.", 2, "Circle (clock face) and lines / triangle (hands)."),
        # Section C: 5 × 3-mark
        Q("Add: (i) 9 + 3, (ii) 7 + 5, (iii) 6 + 6.", 3, "(i) 12, (ii) 12, (iii) 12."),
        Q("Subtract: (i) 10 − 3, (ii) 15 − 7, (iii) 18 − 9.", 3, "(i) 7, (ii) 8, (iii) 9."),
        Q("Compare using <, >, or =: (i) 8 ___ 12, (ii) 5 ___ 5, (iii) 9 ___ 7.", 3, "(i) <, (ii) =, (iii) >."),
        Q("Count and write: how many tens and ones in 24?", 3, "24 = 2 tens + 4 ones."),
        Q("Skip count by 2 starting at 2 up to 10. Write the numbers.", 3, "2, 4, 6, 8, 10."),
        # Section D: 5 × 4-mark
        Q("Riya has 8 apples. She gives 3 apples to her friend. How many apples are left with Riya? Show working.", 4, "Apples left = 8 − 3 = 5 apples."),
        Q("There are 4 boys and 5 girls in a group. Find the total number of children.", 4, "Total = 4 + 5 = 9 children."),
        Q("A teacher distributes 2 pencils to each of the 5 students. How many pencils in all?", 4, "Total pencils = 2 × 5 = 10 pencils."),
        Q("Add three numbers: 3 + 4 + 5. Show your steps.", 4, "Step 1: 3 + 4 = 7. Step 2: 7 + 5 = 12."),
        Q("From 20, subtract 8 then subtract 4. What is the result?", 4, "20 − 8 = 12; 12 − 4 = 8."),
        # Section E: 4 × 5-mark
        Q("A shop has 10 candies. The shopkeeper sells 3 candies and then receives 5 more. How many candies are in the shop now? Show all steps.", 5, "Start = 10. After selling = 10 − 3 = 7. After receiving = 7 + 5 = 12 candies."),
        Q("Arrange these numbers from smallest to largest: 5, 9, 2, 7, 1.", 5, "Order: 1, 2, 5, 7, 9."),
        Q("Mother bought 6 oranges and 4 mangoes. (i) Total fruits? (ii) Which fruit has more?", 5, "(i) 6 + 4 = 10 fruits. (ii) Oranges (6 > 4)."),
        Q("Look around and write the names of any 5 round things you see.", 5, "Examples: Coin, ball, plate, wheel, clock face."),
        # Section F: 3 × 10-mark
        Q("In a classroom there are 12 boys and 8 girls. (a) Find the total number of children (3 marks). (b) How many more boys than girls? (3 marks). (c) If 4 children go home, how many remain? (4 marks).", 10, "(a) 12 + 8 = 20 children. (b) 12 − 8 = 4 more boys. (c) 20 − 4 = 16 children remain."),
        Q("Pranav had 25 chocolates. He gave 10 to his sister and 7 to his brother. (a) How many chocolates did he give in total? (4 marks). (b) How many were left with him? (4 marks). (c) If he ate 3 more, how many remain? (2 marks).", 10, "(a) 10 + 7 = 17 given. (b) 25 − 17 = 8 left. (c) 8 − 3 = 5 remain."),
        Q("Make a list of any 10 things you can count at home and write the count next to each. (Example: 4 chairs, 2 fans …).", 10, "Sample answer: 4 chairs, 2 fans, 6 plates, 3 spoons, 1 TV, 5 windows, 2 doors, 3 books, 2 beds, 1 clock."),
    ]),

    # ─── GRADE 2 — MATHS ─────────────────────────────────────────────────
    (2, "maths", 2024, "Annual Question Paper", [
        MCQ("Number that comes just after 99 is:", ["98", "100", "101", "999"], "b"),
        MCQ("How many sides does a square have?", ["3", "4", "5", "6"], "b"),
        MCQ("How many days in 1 week?", ["5", "6", "7", "8"], "c"),
        MCQ("8 × 2 = ?", ["10", "12", "14", "16"], "d"),
        MCQ("Which is bigger: 64 or 46?", ["64", "46", "Equal", "Cannot tell"], "a"),
        Q("Write the place value of 7 in 472.", 2, "7 is in the tens place; place value = 70."),
        Q("Skip count by 5 starting at 5 up to 30.", 2, "5, 10, 15, 20, 25, 30."),
        Q("Find the sum: 23 + 17.", 2, "23 + 17 = 40."),
        Q("Find the difference: 50 − 24.", 2, "50 − 24 = 26."),
        Q("Write the number 'fifty-six' in figures.", 2, "56."),
        Q("Add: (i) 25 + 14, (ii) 36 + 23, (iii) 41 + 19.", 3, "(i) 39, (ii) 59, (iii) 60."),
        Q("Subtract: (i) 67 − 24, (ii) 80 − 35, (iii) 90 − 47.", 3, "(i) 43, (ii) 45, (iii) 43."),
        Q("Multiply: (i) 3 × 4, (ii) 5 × 6, (iii) 7 × 8.", 3, "(i) 12, (ii) 30, (iii) 56."),
        Q("Continue the pattern: 10, 20, 30, ___, ___, ___.", 3, "40, 50, 60 (add 10 each time)."),
        Q("A clock shows 4 o'clock. After 3 hours, what time is it?", 3, "4 + 3 = 7 o'clock."),
        Q("Vinay has 35 marbles. He buys 18 more. How many marbles does he have now?", 4, "35 + 18 = 53 marbles."),
        Q("There are 60 children in a school. 25 are girls. How many boys are there?", 4, "60 − 25 = 35 boys."),
        Q("Find the total cost: 5 pencils at ₹4 each and 3 erasers at ₹2 each.", 4, "Pencils: 5 × 4 = ₹20. Erasers: 3 × 2 = ₹6. Total = ₹26."),
        Q("Multiply: 14 × 3. Show working.", 4, "14 × 3 = (10 × 3) + (4 × 3) = 30 + 12 = 42."),
        Q("Mother gives ₹50 to Reena. She spends ₹28. How much is left?", 4, "50 − 28 = ₹22 left."),
        Q("A box has 6 rows of chocolates with 8 in each row. (i) Total chocolates? (ii) If 12 are eaten, how many remain?", 5, "(i) 6 × 8 = 48. (ii) 48 − 12 = 36 remain."),
        Q("Write the numbers between 56 and 67. How many numbers are there?", 5, "57, 58, 59, 60, 61, 62, 63, 64, 65, 66 — that is 10 numbers."),
        Q("Compare and arrange in descending order: 78, 56, 92, 34, 65.", 5, "92, 78, 65, 56, 34."),
        Q("A dozen pencils cost ₹60. (i) Cost of one pencil? (ii) Cost of 5 pencils?", 5, "(i) ₹60 ÷ 12 = ₹5 each. (ii) 5 × 5 = ₹25."),
        Q("A shopkeeper had 250 apples in his shop. He sold 90 in the morning, 65 in the afternoon, and 40 in the evening. (a) Total sold? (3 marks). (b) Apples left? (3 marks). (c) If next day he doubles his stock, how many apples will he have? (4 marks).", 10, "(a) 90 + 65 + 40 = 195 sold. (b) 250 − 195 = 55 left. (c) Doubling next day: he buys 250 more, so total = 55 + 250 = 305 (or 2 × 250 = 500 if 'doubles' means new stock)."),
        Q("Make a multiplication table of 6 from 6×1 to 6×10.", 10, "6, 12, 18, 24, 30, 36, 42, 48, 54, 60."),
        Q("Look around the classroom. Count and write the number of: (a) windows (b) doors (c) benches (d) tables (e) bulbs/fans. Then add them all to find the grand total.", 10, "Sample answer: (a) 4 windows (b) 2 doors (c) 12 benches (d) 1 table (e) 4 fans. Total = 4 + 2 + 12 + 1 + 4 = 23."),
    ]),

    # ─── GRADE 3 — MATHS ─────────────────────────────────────────────────
    (3, "maths", 2024, "Annual Question Paper", [
        MCQ("Place value of 5 in 256:", ["5", "50", "500", "5000"], "b"),
        MCQ("Successor of 999:", ["998", "1000", "9999", "10000"], "b"),
        MCQ("8 × 7 = ?", ["54", "56", "58", "63"], "b"),
        MCQ("How many minutes in half an hour?", ["15", "20", "30", "45"], "c"),
        MCQ("Which is greater: 234 or 243?", ["234", "243", "Equal", "Cannot tell"], "b"),
        Q("Write the number 'three hundred forty-five' in figures.", 2, "345."),
        Q("Round 4,789 to the nearest hundred.", 2, "4,789 ≈ 4,800."),
        Q("Find the sum of 125 and 178.", 2, "125 + 178 = 303."),
        Q("Find: 250 ÷ 5.", 2, "250 ÷ 5 = 50."),
        Q("How many ₹5 coins make ₹50?", 2, "10 coins (10 × 5 = 50)."),
        Q("Add: (i) 235 + 478, (ii) 569 + 234, (iii) 800 + 99.", 3, "(i) 713, (ii) 803, (iii) 899."),
        Q("Subtract: (i) 800 − 345, (ii) 1000 − 567, (iii) 654 − 289.", 3, "(i) 455, (ii) 433, (iii) 365."),
        Q("Find: (i) 12 × 7, (ii) 25 × 4, (iii) 8 × 9.", 3, "(i) 84, (ii) 100, (iii) 72."),
        Q("From 8:30 AM to 11:00 AM is how many hours and minutes?", 3, "2 hours 30 minutes."),
        Q("Write the multiplication table of 9 from 9×1 to 9×5.", 3, "9, 18, 27, 36, 45."),
        Q("If 1 box has 12 pencils, how many pencils are there in 5 boxes?", 4, "5 × 12 = 60 pencils."),
        Q("A bottle holds 2 litres. How many such bottles fill a 16-litre tank?", 4, "16 ÷ 2 = 8 bottles."),
        Q("Sumi had ₹500. She bought a book for ₹125 and a pen for ₹35. How much is left?", 4, "Spent = 125 + 35 = 160. Left = 500 − 160 = ₹340."),
        Q("Divide 144 by 12 and write the quotient and remainder.", 4, "144 ÷ 12 = 12, remainder 0."),
        Q("If 1 kg of rice costs ₹45, find the cost of 6 kg.", 4, "6 × 45 = ₹270."),
        Q("A school has 350 students. If 165 are boys, find the number of girls. Then find the difference between boys and girls.", 5, "Girls = 350 − 165 = 185. Difference = 185 − 165 = 20 more girls than boys."),
        Q("Arjun saves ₹15 every day. How much will he save in (i) 1 week, (ii) 30 days?", 5, "(i) 7 × 15 = ₹105. (ii) 30 × 15 = ₹450."),
        Q("Find the perimeter of a rectangle with length 12 cm and width 7 cm.", 5, "Perimeter = 2(l + w) = 2(12 + 7) = 2 × 19 = 38 cm."),
        Q("Convert: (i) 3 hours into minutes, (ii) 4 weeks into days, (iii) 250 paise into rupees.", 5, "(i) 3 × 60 = 180 min. (ii) 4 × 7 = 28 days. (iii) 250 ÷ 100 = ₹2.50."),
        Q("A farmer has 240 mangoes. He puts them into baskets of 8 mangoes each. (a) How many baskets? (3 m). (b) If each basket sells for ₹120, total earning? (4 m). (c) If 5 baskets are damaged, how many baskets remain saleable? (3 m).", 10, "(a) 240 ÷ 8 = 30 baskets. (b) 30 × 120 = ₹3,600. (c) 30 − 5 = 25 baskets."),
        Q("A train leaves station A at 7:15 AM and reaches station B at 11:30 AM. (a) Total travel time? (3 m). (b) If the distance is 255 km, find the speed in km/hour (round to nearest whole) (4 m). (c) If a return ticket costs ₹180 and 25 passengers travel, total fare collected? (3 m).", 10, "(a) 7:15 AM to 11:30 AM = 4 hours 15 minutes. (b) 255 ÷ 4.25 ≈ 60 km/h. (c) 25 × 180 = ₹4,500."),
        Q("Make a bar chart (or describe one) showing the number of students who like 4 fruits: Mango (12), Banana (8), Apple (6), Orange (4). Then answer: which fruit is most liked, which is least liked, and the total number of students.", 10, "Most liked = Mango (12). Least liked = Orange (4). Total = 12 + 8 + 6 + 4 = 30 students. (Bar chart should show 4 vertical bars of decreasing heights for Mango, Banana, Apple, Orange.)"),
    ]),

    # ─── GRADE 4 — MATHS ─────────────────────────────────────────────────
    (4, "maths", 2024, "Annual Question Paper", [
        MCQ("How many edges does a cube have?", ["6", "8", "10", "12"], "d"),
        MCQ("1 km = ___ metres", ["100", "500", "1000", "10000"], "c"),
        MCQ("12 × 5 = ?", ["50", "55", "60", "65"], "c"),
        MCQ("1 litre = ___ mL", ["10", "100", "1000", "10000"], "c"),
        MCQ("Sum of angles in a triangle:", ["90°", "180°", "270°", "360°"], "b"),
        Q("Write 4,503 in expanded form.", 2, "4,503 = 4000 + 500 + 0 + 3."),
        Q("How many faces does a cuboid have?", 2, "A cuboid has 6 faces."),
        Q("Convert: 250 cm into metres.", 2, "250 cm ÷ 100 = 2.5 m."),
        Q("Find: 96 ÷ 8.", 2, "96 ÷ 8 = 12."),
        Q("State whether 247 is a prime number. Why?", 2, "247 = 13 × 19, so it is composite, not prime."),
        Q("Find the sum: 1,236 + 4,789.", 3, "1,236 + 4,789 = 6,025."),
        Q("Subtract: 5,008 − 1,679.", 3, "5,008 − 1,679 = 3,329."),
        Q("Multiply: 234 × 6.", 3, "234 × 6 = 1,404."),
        Q("Divide: 168 ÷ 12. Give quotient and remainder.", 3, "168 ÷ 12 = 14, remainder 0."),
        Q("Find HCF of 12 and 18 by listing factors.", 3, "Factors of 12: 1,2,3,4,6,12. Factors of 18: 1,2,3,6,9,18. HCF = 6."),
        Q("Find the perimeter of a rectangle with length 15 cm and width 9 cm.", 4, "P = 2(15 + 9) = 2 × 24 = 48 cm."),
        Q("A car travels 60 km in 1 hour. How far will it travel in 4½ hours?", 4, "60 × 4.5 = 270 km."),
        Q("Convert: 3 hours 25 minutes into minutes.", 4, "3 × 60 + 25 = 180 + 25 = 205 minutes."),
        Q("A jug holds 1.5 L. How many such jugs can be filled from a 9 L tank?", 4, "9 ÷ 1.5 = 6 jugs."),
        Q("A shop has 1,250 packets of biscuits. It sells 786 packets in a week. How many are left?", 4, "1,250 − 786 = 464 packets left."),
        Q("Find the area of a rectangle of length 14 cm and width 6 cm. Also find the perimeter.", 5, "Area = 14 × 6 = 84 cm². Perimeter = 2(14 + 6) = 40 cm."),
        Q("If 1 kg sugar costs ₹42, find the cost of (i) 5 kg, (ii) ½ kg.", 5, "(i) 5 × 42 = ₹210. (ii) 42 ÷ 2 = ₹21."),
        Q("Solve: 7 × 25 + 3 × 15 − 4 × 8.", 5, "7×25 = 175; 3×15 = 45; 4×8 = 32. So 175 + 45 − 32 = 188."),
        Q("Convert: (i) 4 km into m, (ii) 7000 m into km, (iii) 5 m into cm, (iv) 350 cm into m.", 5, "(i) 4000 m. (ii) 7 km. (iii) 500 cm. (iv) 3.5 m."),
        Q("A school has 4 sections of class 4 with 35 students each. (a) Total students in class 4? (3). (b) If each student pays ₹250 fees, total fees collected? (4). (c) If 12 students are absent on a particular day, how many present? (3).", 10, "(a) 4 × 35 = 140 students. (b) 140 × 250 = ₹35,000. (c) 140 − 12 = 128 present."),
        Q("A field is 80 m long and 45 m wide. (a) Find the perimeter (3). (b) Find the area (3). (c) If grass is to be planted in this field at ₹15 per square metre, find the total cost (4).", 10, "(a) P = 2(80 + 45) = 250 m. (b) Area = 80 × 45 = 3,600 m². (c) Cost = 3,600 × 15 = ₹54,000."),
        Q("Look at the multiplication of 786 × 24 step by step. (a) Write the standard algorithm. (b) Verify your answer using estimation (round 786 to 800 and 24 to 25). (c) State whether estimation is close to actual.", 10, "(a) 786 × 24 = 786 × 20 + 786 × 4 = 15,720 + 3,144 = 18,864. (b) Estimate: 800 × 25 = 20,000. (c) 18,864 is close to 20,000 (~6% off), so estimation is reasonable."),
    ]),

    # ─── GRADE 5 — MATHS ─────────────────────────────────────────────────
    (5, "maths", 2024, "Annual Question Paper", [
        MCQ("Place value of 5 in 25,634:", ["5", "50", "500", "5000"], "d"),
        MCQ("Decimal form of 3/4:", ["0.25", "0.5", "0.75", "1.0"], "c"),
        MCQ("LCM of 4 and 6:", ["10", "12", "18", "24"], "b"),
        MCQ("Area of a square of side 7 cm:", ["28", "49", "56", "70"], "b"),
        MCQ("(-3) × (-4) = ?", ["-12", "-7", "7", "12"], "d"),
        Q("Write 2,34,567 in words (Indian system).", 2, "Two lakh thirty-four thousand five hundred sixty-seven."),
        Q("Find the HCF of 8 and 12.", 2, "Factors: 8 → 1,2,4,8 ; 12 → 1,2,3,4,6,12. HCF = 4."),
        Q("Convert 3/5 into a decimal.", 2, "3 ÷ 5 = 0.6."),
        Q("Find: 4.5 + 2.75.", 2, "4.5 + 2.75 = 7.25."),
        Q("Round 6,847 to the nearest thousand.", 2, "6,847 ≈ 7,000."),
        Q("Solve: (i) 3/4 of 20, (ii) 2/3 of 15, (iii) 1/2 + 1/4.", 3, "(i) 15. (ii) 10. (iii) 3/4."),
        Q("Find LCM of 12 and 18 using prime factorisation.", 3, "12 = 2²×3 ; 18 = 2×3². LCM = 2²×3² = 36."),
        Q("Multiply: 2.4 × 3.5.", 3, "2.4 × 3.5 = 8.4."),
        Q("Convert: (i) 2 hours 30 min into minutes, (ii) 5 km into m, (iii) 1.5 L into mL.", 3, "(i) 150 min. (ii) 5,000 m. (iii) 1,500 mL."),
        Q("Compare and arrange in ascending order: 0.7, 0.07, 0.77, 7.0.", 3, "0.07 < 0.7 < 0.77 < 7.0."),
        Q("Find the perimeter of a rectangle with length 18 cm and width 12 cm.", 4, "P = 2(18+12) = 60 cm."),
        Q("Find the area of a square field of side 25 m.", 4, "A = 25² = 625 m²."),
        Q("If a fisherman catches 36 fish per day, how many will he catch in 2 weeks?", 4, "14 × 36 = 504 fish."),
        Q("A rectangle has area 84 cm² and length 12 cm. Find its width.", 4, "Width = 84 ÷ 12 = 7 cm."),
        Q("Solve: 3/4 + 1/2 − 1/4. Show steps.", 4, "Common denominator 4: 3/4 + 2/4 − 1/4 = 4/4 = 1."),
        Q("Find the smallest 3-digit number divisible by both 6 and 8.", 5, "LCM(6,8) = 24. Smallest 3-digit multiple of 24 = 120."),
        Q("A car covers 45 km in 1 hour. (i) Distance in 4 hours? (ii) Time to cover 270 km?", 5, "(i) 4 × 45 = 180 km. (ii) 270 ÷ 45 = 6 hours."),
        Q("Convert: (i) 0.25 to a fraction, (ii) 7/8 to decimal, (iii) 15% to a fraction.", 5, "(i) 1/4. (ii) 0.875. (iii) 15/100 = 3/20."),
        Q("Solve the word problem: From a length of cloth 25 m, 4.5 m is used for one shirt and 3.25 m for another. How much cloth is left?", 5, "Used = 4.5 + 3.25 = 7.75. Left = 25 − 7.75 = 17.25 m."),
        Q("A rectangular garden is 40 m long and 25 m wide. (a) Perimeter (2). (b) Area (3). (c) Cost of fencing at ₹50/m (3). (d) Cost of laying grass at ₹35/m² (2).", 10, "(a) 2(40+25) = 130 m. (b) 40×25 = 1000 m². (c) 130 × 50 = ₹6,500. (d) 1000 × 35 = ₹35,000."),
        Q("In a school of 1,250 students, 60% are girls. (a) Number of girls (3). (b) Number of boys (3). (c) If 5% of all students are absent, how many are present? (4).", 10, "(a) 60% of 1250 = 750 girls. (b) 1250 − 750 = 500 boys. (c) 5% of 1250 = 62.5 ≈ 63. Present = 1250 − 63 = 1187."),
        Q("A water tank holds 5,000 L. (a) Convert this into mL (2). (b) If a family uses 250 L per day, for how many days will the tank last? (4). (c) If they manage to reduce usage by 20%, find the new daily usage and how many days the tank lasts now (4).", 10, "(a) 5,000 × 1000 = 50,00,000 mL. (b) 5000 ÷ 250 = 20 days. (c) Reduced usage = 250 − 50 = 200 L/day. New duration = 5000 ÷ 200 = 25 days."),
    ]),

    # ─── GRADE 6 — MATHS ─────────────────────────────────────────────────
    (6, "maths", 2024, "Annual Question Paper", [
        MCQ("Roman numeral for 50:", ["L", "C", "D", "M"], "a"),
        MCQ("Smallest prime number:", ["1", "2", "3", "5"], "b"),
        MCQ("Sum of angles in a triangle:", ["90°", "180°", "270°", "360°"], "b"),
        MCQ("(-5) + 3 = ?", ["-8", "-2", "2", "8"], "b"),
        MCQ("A polygon with 6 sides:", ["Pentagon", "Hexagon", "Octagon", "Decagon"], "b"),
        Q("Define a prime number with two examples.", 2, "A prime number has exactly two factors: 1 and itself. Examples: 2, 3, 5, 7."),
        Q("Convert 1,23,45,678 into the International System.", 2, "12,345,678 (twelve million three hundred forty-five thousand six hundred seventy-eight)."),
        Q("Find HCF of 18 and 24 using prime factorisation.", 2, "18 = 2×3²; 24 = 2³×3. HCF = 2×3 = 6."),
        Q("Write the additive inverse of -7 and 5.", 2, "Additive inverse of -7 is 7; of 5 is -5."),
        Q("How many lines of symmetry does a rectangle have?", 2, "A rectangle has 2 lines of symmetry."),
        Q("Find LCM of 12, 16 and 24 using prime factorisation.", 3, "12 = 2²×3; 16 = 2⁴; 24 = 2³×3. LCM = 2⁴×3 = 48."),
        Q("Solve: 2/3 + 5/6 − 1/2. Show steps.", 3, "LCD = 6. = 4/6 + 5/6 − 3/6 = 6/6 = 1."),
        Q("Calculate: (-15) + 12 − (-3) + (-7).", 3, "= -15 + 12 + 3 − 7 = -7."),
        Q("Find perimeter of a triangle with sides 7 cm, 9 cm, 11 cm.", 3, "P = 7 + 9 + 11 = 27 cm."),
        Q("Define and give an example of a 'composite number'.", 3, "Composite number = a positive integer > 1 with more than two factors. Example: 4 (factors 1,2,4)."),
        Q("Solve: 7x − 4 = 24. Find x.", 4, "7x = 28 → x = 4."),
        Q("Find the area of a rectangle with length 25 m and breadth 18 m.", 4, "A = 25 × 18 = 450 m²."),
        Q("If the cost of 12 books is ₹540, find cost of 1 book and 8 books.", 4, "1 book = 540 ÷ 12 = ₹45. 8 books = 8 × 45 = ₹360."),
        Q("Round 4,76,852 to nearest thousand and to nearest lakh.", 4, "Nearest thousand = 4,77,000. Nearest lakh = 5,00,000."),
        Q("Find the value of: (-3) × 4 + 6 × (-2) − (-10).", 4, "= -12 − 12 + 10 = -14."),
        Q("Construct an angle of 60° using a protractor and write the steps.", 5, "Steps: (1) Draw a base ray. (2) Place protractor centre on starting point. (3) Mark 60° on the scale. (4) Join with a straight line. The required angle = 60°."),
        Q("In a class of 40 students, 60% like cricket. (i) Number of cricket lovers? (ii) Number of others?", 5, "(i) 60% of 40 = 24. (ii) 40 − 24 = 16."),
        Q("A rectangular field is 50 m × 30 m. (i) Perimeter? (ii) Area? (iii) Fencing cost at ₹25/m?", 5, "(i) 2(50+30) = 160 m. (ii) 50×30 = 1500 m². (iii) 160 × 25 = ₹4,000."),
        Q("Find LCM and HCF of 24 and 36. Verify: HCF × LCM = product of the two numbers.", 5, "HCF = 12, LCM = 72. Verify: 12 × 72 = 864 = 24 × 36 ✓"),
        Q("Solve the word problem: A father is 3 times as old as his son. After 12 years he will be 2 times as old. (a) Form an equation (4 m). (b) Solve for present ages (4 m). (c) State father's age 5 years from now (2 m).", 10, "Let son = x. Father = 3x. After 12: father = 3x+12, son = x+12. 3x+12 = 2(x+12) → 3x+12 = 2x+24 → x = 12. (b) Son 12, Father 36. (c) Father in 5 yrs = 41."),
        Q("A water tank in the shape of a cuboid has length 5 m, width 3 m, height 2 m. (a) Find the volume in m³ (3). (b) Convert to litres (1 m³ = 1000 L) (3). (c) If a family uses 200 L per day, how many days will it last? (4).", 10, "(a) 5 × 3 × 2 = 30 m³. (b) 30 × 1000 = 30,000 L. (c) 30,000 ÷ 200 = 150 days."),
        Q("Draw and explain the number line representation of the addition (-3) + 5. Then add: (-7) + 2 + (-4) using a number line, showing each step.", 10, "(-3) + 5: start at -3, move 5 right → land at 2. So (-3) + 5 = 2. (-7) + 2 + (-4): start at -7, move 2 right to -5, then 4 left to -9. Final answer: -9."),
    ]),

    # ─── GRADE 7 — MATHS ─────────────────────────────────────────────────
    (7, "maths", 2024, "Annual Question Paper", [
        MCQ("(-3) × (-4) = ?", ["-12", "-7", "7", "12"], "d"),
        MCQ("0.25 in fraction form:", ["1/4", "1/2", "2/5", "1/3"], "a"),
        MCQ("Mean of 4, 6, 8, 10:", ["6", "7", "8", "9"], "b"),
        MCQ("Two angles whose sum = 90° are:", ["Supplementary", "Complementary", "Vertical", "Right"], "b"),
        MCQ("Equilateral triangle each angle:", ["45°", "60°", "75°", "90°"], "b"),
        Q("State the rule for multiplying two negative integers, with one example.", 2, "Negative × negative = positive. Example: (-3)×(-4) = 12."),
        Q("Convert 5/8 into a decimal.", 2, "5 ÷ 8 = 0.625."),
        Q("Find the value of x: 3x = 24.", 2, "x = 8."),
        Q("Define complementary and supplementary angles.", 2, "Complementary: sum = 90°. Supplementary: sum = 180°."),
        Q("Write the prime factorisation of 84.", 2, "84 = 2² × 3 × 7."),
        Q("Solve: 2x + 7 = 19. Show steps.", 3, "2x = 19 − 7 = 12 → x = 6."),
        Q("Add: 2/3 + 3/4 − 1/6. Show steps.", 3, "LCD = 12. = 8/12 + 9/12 − 2/12 = 15/12 = 5/4."),
        Q("Find: (i) (-7) × 5, (ii) 24 ÷ (-6), (iii) (-15) ÷ (-3).", 3, "(i) -35. (ii) -4. (iii) 5."),
        Q("Find median of: 3, 7, 9, 12, 14.", 3, "Already in order, n = 5; median = middle value = 9."),
        Q("Find perimeter of a triangle with sides 8 cm, 10 cm, 12 cm.", 3, "P = 8 + 10 + 12 = 30 cm."),
        Q("Solve: 3(x − 2) = 2x + 5. Find x.", 4, "3x − 6 = 2x + 5 → x = 11."),
        Q("Convert 2/5 into percentage.", 4, "(2/5) × 100 = 40%."),
        Q("In right-angled triangle with legs 6 and 8 cm, find hypotenuse using Pythagoras.", 4, "h² = 6² + 8² = 36 + 64 = 100 → h = 10 cm."),
        Q("Find simple interest on ₹2,000 at 8% per annum for 3 years.", 4, "SI = (P×R×T)/100 = (2000×8×3)/100 = ₹480."),
        Q("Find the mode of: 4, 6, 4, 7, 8, 4, 9, 6, 4.", 4, "4 occurs 4 times → mode = 4."),
        Q("Find x in the equation: (x/3) + 5 = 11.", 5, "x/3 = 6 → x = 18."),
        Q("Construct a triangle PQR where PQ = 5 cm, QR = 6 cm, PR = 7 cm. Write the steps of construction.", 5, "Steps: 1) Draw PQ = 5 cm. 2) With centre P, draw arc of radius 7 cm. 3) With centre Q, draw arc of radius 6 cm. 4) Mark intersection as R. 5) Join PR and QR."),
        Q("Convert: (i) 1.25 to fraction, (ii) 7/4 to mixed number, (iii) 3 1/2 to improper fraction.", 5, "(i) 5/4. (ii) 1 3/4. (iii) 7/2."),
        Q("A rectangle has length 14 cm and breadth 8 cm. Find its area, perimeter and diagonal (use Pythagoras).", 5, "Area = 14×8 = 112 cm². Perimeter = 2(14+8) = 44 cm. Diagonal = √(14² + 8²) = √(196+64) = √260 ≈ 16.12 cm."),
        Q("A cyclist covers 60 km in 4 hours. (a) Speed (2). (b) Distance in 5½ hours at same speed (3). (c) If speed increases by 5 km/h, distance in 4 hrs (3). (d) Time to cover 200 km at original speed (2).", 10, "(a) 60/4 = 15 km/h. (b) 5.5 × 15 = 82.5 km. (c) New speed = 20 km/h; distance = 4 × 20 = 80 km. (d) 200/15 ≈ 13.33 hrs."),
        Q("In a survey of 200 students, the data of favourite subjects is: Maths 60, Science 50, English 40, Social 30, Others 20. (a) Draw a bar graph (or describe one) (4). (b) Find percentage choosing Maths (3). (c) What fraction chose subjects other than Maths and Science? (3).", 10, "(a) Bar graph with 5 bars: Maths 60, Science 50, English 40, Social 30, Others 20. (b) (60/200)×100 = 30%. (c) Other than M+S = 200 − 110 = 90 students = 90/200 = 9/20."),
        Q("Construct an angle of 75° using only a compass and ruler. Write the steps. Then bisect it.", 10, "Method: 75° = 60° + 15°, where 15° = half of 30° (half of bisected 60°). Steps: 1) Draw ray. 2) Construct 60° using arcs. 3) Construct 90° similarly. 4) Bisect the 30° gap between 60° and 90° to get 75°. 5) To bisect 75°: draw arcs from both arms of the 75° angle that intersect, join intersection to the vertex; this gives 37.5° on each side."),
    ]),

    # ─── GRADE 8 — MATHS ─────────────────────────────────────────────────
    (8, "maths", 2024, "Annual Question Paper", [
        MCQ("Multiplicative inverse of 4/5:", ["-4/5", "5/4", "-5/4", "1"], "b"),
        MCQ("Sum of interior angles of any quadrilateral:", ["180°", "270°", "360°", "540°"], "c"),
        MCQ("Square of 12:", ["122", "124", "144", "164"], "c"),
        MCQ("(a + b)² equals:", ["a² + b²", "a² + 2ab + b²", "a² − 2ab + b²", "ab"], "b"),
        MCQ("Probability of head when fair coin tossed:", ["0", "1/2", "1", "1/4"], "b"),
        Q("Define rational number with two examples.", 2, "A number that can be written as p/q where p, q are integers and q ≠ 0. Examples: 1/2, -3/4."),
        Q("Find: √196.", 2, "√196 = 14."),
        Q("Solve: 5x − 12 = 23.", 2, "5x = 35 → x = 7."),
        Q("Write the formula for area of a trapezium.", 2, "Area = ½ × (sum of parallel sides) × height = ½(a + b)h."),
        Q("State whether the equation x² + 1 = 0 has real solutions.", 2, "No, since x² ≥ 0 for any real x, so x² + 1 ≥ 1 ≠ 0."),
        Q("Solve: 3(x − 2) = 2x + 1.", 3, "3x − 6 = 2x + 1 → x = 7."),
        Q("Expand using identity: (3x + 4)².", 3, "(3x)² + 2(3x)(4) + 4² = 9x² + 24x + 16."),
        Q("Find HCF and LCM of 36 and 48 using prime factorisation.", 3, "36 = 2²×3²; 48 = 2⁴×3. HCF = 2²×3 = 12; LCM = 2⁴×3² = 144."),
        Q("Find the cube root of 729.", 3, "729 = 9³ → cube root = 9."),
        Q("Find the area of a parallelogram with base 12 cm and height 8 cm.", 3, "Area = base × height = 12 × 8 = 96 cm²."),
        Q("Solve the linear equation: (2x − 1)/3 + 4 = 7.", 4, "(2x − 1)/3 = 3 → 2x − 1 = 9 → x = 5."),
        Q("Factorise: x² + 7x + 12.", 4, "x² + 7x + 12 = (x + 3)(x + 4)."),
        Q("Find the surface area of a cube of side 6 cm.", 4, "SA = 6 × side² = 6 × 36 = 216 cm²."),
        Q("If the simple interest on ₹5,000 for 3 years is ₹600, find the rate.", 4, "SI = (P×R×T)/100 → 600 = (5000×R×3)/100 → R = 4%."),
        Q("Verify: (a − b)² = a² − 2ab + b² for a = 5, b = 2.", 4, "LHS = (5−2)² = 9. RHS = 25 − 20 + 4 = 9. LHS = RHS ✓."),
        Q("In a bag there are 10 balls: 4 red, 3 blue, 3 green. Find probability of (i) red, (ii) blue or green.", 5, "(i) 4/10 = 2/5. (ii) (3+3)/10 = 6/10 = 3/5."),
        Q("Find the area of a trapezium with parallel sides 12 cm and 18 cm and height 8 cm.", 5, "Area = ½(12+18)×8 = ½ × 30 × 8 = 120 cm²."),
        Q("Find the volume of a cuboid 10 cm × 6 cm × 4 cm. Then find its total surface area.", 5, "V = 10×6×4 = 240 cm³. SA = 2(lw + wh + hl) = 2(60+24+40) = 248 cm²."),
        Q("A man bought an article for ₹800 and sold it for ₹920. Find profit and profit %.", 5, "Profit = 920 − 800 = ₹120. Profit % = (120/800) × 100 = 15%."),
        Q("In a class of 50 students, 30 like maths, 25 like science, 10 like both. (a) Draw a Venn diagram (or describe). (b) How many like only maths? (c) How many like only science? (d) How many like neither? Show all parts.", 10, "Only maths = 30 − 10 = 20. Only science = 25 − 10 = 15. Both = 10. Total liking either = 20 + 15 + 10 = 45. Neither = 50 − 45 = 5."),
        Q("A solid cylinder has radius 7 cm and height 20 cm. (a) Find its volume (use π = 22/7) (4). (b) Find total surface area (4). (c) Convert volume to litres (1 cm³ = 1 mL) (2).", 10, "(a) V = πr²h = (22/7)×49×20 = 3,080 cm³. (b) TSA = 2πr(r+h) = 2×(22/7)×7×27 = 1,188 cm². (c) 3,080 cm³ = 3,080 mL = 3.08 L."),
        Q("Solve graphically (or describe the graph) of the equations: x + y = 6 and x − y = 2. (a) Find solution algebraically (4). (b) Verify (3). (c) Plot any 2 points on each line (3).", 10, "Adding: 2x = 8 → x = 4; subtracting: 2y = 4 → y = 2. Solution (4, 2). Verify: 4+2 = 6 ✓; 4−2 = 2 ✓. Sample points on x+y=6: (0,6), (6,0). On x−y=2: (2,0), (5,3)."),
    ]),

    # ─── GRADE 9 — MATHS ─────────────────────────────────────────────────
    (9, "maths", 2024, "Annual Question Paper", [
        MCQ("Decimal expansion of 1/3:", ["Terminating", "Non-terminating, repeating", "Non-terminating, non-repeating", "Whole number"], "b"),
        MCQ("Degree of polynomial 3x² + 5x + 7:", ["1", "2", "3", "0"], "b"),
        MCQ("(3, -2) lies in quadrant:", ["I", "II", "III", "IV"], "d"),
        MCQ("Standard form of linear equation in 2 variables:", ["ax + b = 0", "ax² + bx + c = 0", "ax + by + c = 0", "ax + by = c²"], "c"),
        MCQ("Distance of (3, 4) from origin:", ["3", "4", "5", "7"], "c"),
        Q("Define rational and irrational numbers with one example each.", 2, "Rational: p/q form, q ≠ 0 (e.g. 3/4). Irrational: cannot be expressed as p/q (e.g. √2)."),
        Q("Evaluate: (√5 + √2)(√5 − √2).", 2, "Difference of squares = 5 − 2 = 3."),
        Q("If p(x) = x² − 3x + 2, find p(1).", 2, "p(1) = 1 − 3 + 2 = 0."),
        Q("Find the coordinates of the point that lies on the y-axis at distance 5 below origin.", 2, "(0, -5)."),
        Q("State Heron's formula for area of a triangle.", 2, "Area = √(s(s−a)(s−b)(s−c)) where s = (a+b+c)/2."),
        Q("Find the value of 'a' if (x + 2) is a factor of x³ + ax + 2.", 3, "By factor theorem: substitute x = -2. (-2)³ + a(-2) + 2 = 0 → -8 − 2a + 2 = 0 → -2a = 6 → a = -3."),
        Q("Factorise: 8x³ + 27.", 3, "Sum of cubes: (2x)³ + 3³ = (2x + 3)(4x² − 6x + 9)."),
        Q("Find the area of a triangle with sides 13 cm, 14 cm, 15 cm using Heron's formula.", 3, "s = (13+14+15)/2 = 21. Area = √(21×8×7×6) = √7056 = 84 cm²."),
        Q("Verify Euclid's division lemma for a = 17, b = 6.", 3, "17 = 6 × 2 + 5 (q = 2, r = 5; 0 ≤ r < b ✓)."),
        Q("Find the equation of x-axis and y-axis.", 3, "x-axis: y = 0. y-axis: x = 0."),
        Q("Solve the linear equation: 3(x − 2) = 5x + 4. Show steps.", 4, "3x − 6 = 5x + 4 → -2x = 10 → x = -5."),
        Q("If a polynomial p(x) = 2x³ − kx² + 3x − 5 leaves remainder 7 when divided by (x + 1), find k.", 4, "p(-1) = 7 → -2 − k − 3 − 5 = 7 → -10 − k = 7 → k = -17."),
        Q("Find the area of a rhombus whose diagonals are 16 cm and 12 cm.", 4, "Area = ½ × d₁ × d₂ = ½ × 16 × 12 = 96 cm²."),
        Q("Plot points A(2,3), B(2,-3), C(-2,-3) on a graph and identify the figure formed by joining them and origin.", 4, "Quadrilateral with vertices (0,0), (2,3), (2,-3), (-2,-3). Shape: a trapezium / general quadrilateral. (Sketch on graph.)"),
        Q("Surface area of sphere of radius 7 cm. Use π = 22/7.", 4, "SA = 4πr² = 4 × 22/7 × 49 = 616 cm²."),
        Q("Solve graphically (or describe the graph) of x + y = 5 and 2x − y = 4. Find (i) point of intersection, (ii) verify. ", 5, "Add: 3x = 9 → x = 3. y = 5 − 3 = 2. Solution (3, 2). Verify: 3+2 = 5 ✓, 6−2 = 4 ✓."),
        Q("If two angles of a triangle are 35° and 75°, find the third angle and classify the triangle.", 5, "Third angle = 180 − 35 − 75 = 70°. All angles acute → acute-angled triangle. All sides different → scalene."),
        Q("In a parallelogram ABCD, ∠A = 75°. Find ∠B, ∠C and ∠D. State the property used.", 5, "Property: opposite angles equal; adjacent angles supplementary. ∠C = 75° (opp). ∠B = 180 − 75 = 105° (adj supp). ∠D = 105°."),
        Q("Find the volume of a hemisphere of radius 21 cm. Use π = 22/7.", 5, "V = (2/3)πr³ = (2/3)(22/7)(21³) = (2/3)(22/7)(9261) = 19,404 cm³."),
        Q("In a right circular cylinder of radius 7 cm and height 20 cm: (a) Find curved surface area (3). (b) Total surface area (3). (c) Volume (4). Use π = 22/7.", 10, "(a) CSA = 2πrh = 2×22/7×7×20 = 880 cm². (b) TSA = 2πr(r+h) = 2×22/7×7×27 = 1,188 cm². (c) V = πr²h = 22/7×49×20 = 3,080 cm³."),
        Q("A cumulative frequency table is given below. Marks of 30 students: <10: 5; 10-20: 10; 20-30: 8; 30-40: 4; 40-50: 3. (a) Draw a histogram (4). (b) Find the modal class (3). (c) Find total number of students who scored at least 20 marks (3).", 10, "(a) Histogram: bars of widths 10 and heights 5, 10, 8, 4, 3 for the five intervals. (b) Modal class = 10–20 (highest frequency 10). (c) ≥ 20: 8 + 4 + 3 = 15 students."),
        Q("Prove that the sum of any two sides of a triangle is greater than the third side. Then verify for a triangle with sides 5, 7, 9.", 10, "Proof (Triangle Inequality): For triangle ABC with sides a, b, c, the line segment between two vertices is the shortest path; any path through the third vertex is longer. Hence a + b > c, b + c > a, c + a > b. Verify: 5+7 = 12 > 9 ✓; 7+9 = 16 > 5 ✓; 5+9 = 14 > 7 ✓."),
    ]),

    # ─── GRADE 10 — MATHS ────────────────────────────────────────────────
    (10, "maths", 2024, "Annual Question Paper", [
        MCQ("HCF × LCM of two numbers =", ["Sum", "Product", "Difference", "1"], "b"),
        MCQ("Sum of zeroes of x² − 5x + 6:", ["-5", "5", "6", "-6"], "b"),
        MCQ("Discriminant of ax² + bx + c is:", ["b² + 4ac", "b² − 4ac", "4ac − b²", "2b − ac"], "b"),
        MCQ("nth term of AP:", ["a + nd", "a + (n-1)d", "a + (n+1)d", "an + d"], "b"),
        MCQ("sin² θ + cos² θ =", ["0", "1", "tan θ", "Undefined"], "b"),
        Q("State the Fundamental Theorem of Arithmetic.", 2, "Every composite number can be expressed as a product of primes uniquely (up to order)."),
        Q("Find HCF of 96 and 404 using Euclid's algorithm.", 2, "404 = 96×4 + 20; 96 = 20×4 + 16; 20 = 16×1 + 4; 16 = 4×4 + 0. HCF = 4."),
        Q("Find the discriminant of 2x² − 4x + 3.", 2, "D = b² − 4ac = 16 − 24 = -8."),
        Q("State the relationship between zeroes and coefficients of a quadratic polynomial.", 2, "If α, β are zeroes of ax² + bx + c, then α+β = -b/a and αβ = c/a."),
        Q("If sin θ = 3/5, find cos θ.", 2, "cos²θ = 1 − sin²θ = 1 − 9/25 = 16/25 → cos θ = 4/5."),
        Q("Find roots of x² − 5x + 6 = 0 by factorisation.", 3, "(x − 2)(x − 3) = 0 → x = 2 or x = 3."),
        Q("Find the 10th term of the AP 2, 5, 8, 11, …", 3, "a = 2, d = 3. a₁₀ = 2 + 9×3 = 29."),
        Q("Solve: 2x + 3y = 11 and x − y = 3. Find x, y.", 3, "From 2nd: x = y + 3. Substitute: 2(y+3) + 3y = 11 → 5y = 5 → y = 1. x = 4."),
        Q("Find the area of a sector of a circle of radius 14 cm with central angle 90°. Use π = 22/7.", 3, "Area = (90/360)×πr² = ¼ × (22/7)×196 = 154 cm²."),
        Q("Prove that √2 is irrational. Outline of proof.", 3, "Assume √2 = p/q (lowest terms). Then 2q² = p², so p² is even, hence p is even. Let p = 2m → 4m² = 2q² → q² = 2m², so q is even. Then both p, q even, contradicting 'lowest terms'. Hence √2 is irrational."),
        Q("Solve the quadratic 2x² − 7x + 3 = 0 using quadratic formula.", 4, "x = (7 ± √(49 − 24))/4 = (7 ± 5)/4 → x = 3 or x = 1/2."),
        Q("Find the sum of first 25 terms of the AP 5, 8, 11, …", 4, "a = 5, d = 3, n = 25. S₂₅ = (n/2)[2a + (n-1)d] = (25/2)[10 + 72] = (25/2)(82) = 1,025."),
        Q("Find the distance between points P(2, 3) and Q(-1, 7).", 4, "d = √((2-(-1))² + (3-7)²) = √(9 + 16) = √25 = 5."),
        Q("Prove: 1/(1 + sin θ) + 1/(1 − sin θ) = 2 sec²θ.", 4, "LHS = [(1−sin θ) + (1+sin θ)] / [(1+sin θ)(1−sin θ)] = 2 / (1−sin²θ) = 2 / cos²θ = 2 sec²θ. ✓"),
        Q("In ΔABC right-angled at B, AB = 6 cm and BC = 8 cm. Find AC and sin A, cos A, tan A.", 4, "AC = √(36+64) = 10. sin A = BC/AC = 8/10 = 4/5; cos A = 6/10 = 3/5; tan A = 8/6 = 4/3."),
        Q("Find the value of k for which the system has a unique solution: 2x + 3y = 7 and 4x + ky = 14.", 5, "For unique solution: 2/4 ≠ 3/k → 1/2 ≠ 3/k → k ≠ 6. So unique solution for all k ≠ 6."),
        Q("Find the volume of a cone with radius 5 cm and height 12 cm. Use π = 22/7.", 5, "V = (1/3)πr²h = (1/3)(22/7)(25)(12) = 314.28… ≈ 314.29 cm³."),
        Q("Solve graphically (or describe) x + y = 5 and 2x − y = 4. Mention solution and verify.", 5, "Adding: 3x = 9 → x = 3, y = 2. Verify: 3+2 = 5 ✓, 6−2 = 4 ✓."),
        Q("A bag contains 5 red, 4 blue and 3 green balls. One ball is drawn at random. Find P(red), P(not red), P(blue or green).", 5, "Total = 12. P(red) = 5/12. P(not red) = 7/12. P(blue or green) = 7/12."),
        Q("(a) State the quadratic formula (2). (b) Find the values of x for which 3x² − 5x + 1 = 0 (4). (c) Verify your roots by substituting (4).", 10, "(a) x = (-b ± √(b²−4ac)) / 2a. (b) D = 25 − 12 = 13. x = (5 ± √13)/6. Two roots: (5+√13)/6 and (5−√13)/6. (c) Substitute back: 3x² − 5x + 1 should give 0 for both. (Numerical check: √13 ≈ 3.606, x ≈ 1.434 or 0.232; verify each gives ~0.)"),
        Q("(a) Define an arithmetic progression with example (2). (b) Find the 20th term and sum to 20 terms of: 7, 10, 13, … (4). (c) Show that the AP 3, 7, 11, 15, … never contains a multiple of 5 unless… [show one example] (4).", 10, "(a) An AP is a sequence where each term differs from the previous by a constant 'd'. Example: 2, 5, 8, 11, … (d=3). (b) a=7, d=3. a₂₀ = 7+19(3) = 64. S₂₀ = (20/2)(7+64) = 10×71 = 710. (c) The AP 3, 7, 11, 15, 19, 23, 27, 31, 35, … contains 35 = 7×5. So multiples of 5 do appear (when 4n+3 ≡ 0 mod 5 i.e. 4n ≡ 2 i.e. n ≡ 3 mod 5)."),
        Q("(a) Prove that the lengths of tangents drawn from an external point to a circle are equal. (5). (b) Two tangents PA and PB are drawn to a circle with centre O from external point P. If ∠APB = 70°, find ∠AOB. (5).", 10, "(a) Proof: Let P be external; PA, PB tangent at A, B. OA ⊥ PA and OB ⊥ PB (radius ⊥ tangent). In ΔOAP and ΔOBP: OA = OB (radii), OP common, ∠OAP = ∠OBP = 90°. So ΔOAP ≅ ΔOBP (RHS). Hence PA = PB. (b) AOBP is a quadrilateral with ∠OAP = ∠OBP = 90°. Sum = 360°, so ∠AOB + ∠APB = 180°. ∠AOB = 180 − 70 = 110°."),
    ]),
]


class Command(BaseCommand):
    help = "Create 100-mark previous-year-style question papers for every grade."

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

        for grade, subject_code, year, paper_title, questions in PAPERS:
            total_marks = sum(q["marks"] for q in questions)

            subj, _ = Subject.objects.get_or_create(name=subject_code)
            chapter, _ = Chapter.objects.get_or_create(
                subject=subj, grade=grade, chapter_number=92,
                defaults={
                    "title": f"Question Papers ({subject_code})",
                    "description": f"Grade {grade} 100-mark mock papers — {subject_code}",
                },
            )

            quiz_title = f"Question Paper {year} — {subject_code.title()} ({total_marks} marks)"
            quiz, created = Quiz.objects.get_or_create(
                chapter=chapter,
                title=quiz_title,
                defaults={
                    "subject": subject_code,
                    "grade": grade,
                    "description": f"Mock {total_marks}-mark previous-year-style paper. Mixed question types — MCQ, short answer, long answer, essay.",
                    "num_questions": len(questions),
                    "duration_minutes": 180,           # 3 hours like a real board paper
                    "passing_percentage": 33.0,        # standard board pass mark
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
                        "options_json": qd["options_json"],
                        "correct_answer": qd["correct_answer"],
                        "explanation": qd["explanation"],
                        "difficulty": qd.get("difficulty", "medium"),
                        "marks": qd["marks"],
                        "question_type": qd["question_type"],
                    },
                )
                if q_created:
                    added_questions += 1
                else:
                    skipped += 1

            quiz.num_questions = quiz.questions.count()
            quiz.save(update_fields=["num_questions"])

        self.stdout.write(self.style.SUCCESS(
            f"\nQuestion Papers: +{added_papers} new papers, "
            f"+{added_questions} questions ({skipped} duplicates skipped)."
        ))
        self.stdout.write("Each paper = 100 marks, mixed types (1, 2, 3, 4, 5, 10 mark questions).")
