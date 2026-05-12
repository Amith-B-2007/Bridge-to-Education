from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from urllib.parse import quote
from .models import Subject, Chapter, Resource, StudentResourceDownload
from .serializers import (
    SubjectSerializer, ChapterSerializer, ResourceSerializer,
    ResourceUploadSerializer, StudentResourceDownloadSerializer
)

# ------------------------------------------------------------------
# NCERT chapter PDF URL builder
# Confirmed URL pattern: https://ncert.nic.in/ncerts/l/{grade_letter}{subject_code}1{chapter:02d}.pdf
# Grade letters: 1=a, 2=b, ..., 6=f, 7=g, 8=h, 9=i, 10=j
# ------------------------------------------------------------------
_GRADE_LETTER = {i: chr(ord('a') + i - 1) for i in range(1, 11)}

# Only include (subject, grade) combos whose NCERT codes I'm confident are correct.
# Everything else falls back to the NCERT textbook selector page.
_NCERT_SUBJECT_CODE = {
    # Maths grades 6-10  (code 'emh' = English Medium Mathematics Higher)
    ('maths', 6): 'emh', ('maths', 7): 'emh', ('maths', 8): 'emh',
    ('maths', 9): 'emh', ('maths', 10): 'emh',
    # Science grades 6-10  (code 'esc' = Environmental Science / Science)
    ('science', 6): 'esc', ('science', 7): 'esc', ('science', 8): 'esc',
    ('science', 9): 'esc', ('science', 10): 'esc',
}


def _ncert_chapter_url(grade: int, subject: str, chapter_number: int) -> str:
    """Return direct NCERT chapter PDF URL, or NCERT textbook selector as fallback."""
    grade_letter = _GRADE_LETTER.get(grade, 'f')
    code = _NCERT_SUBJECT_CODE.get((subject, grade))
    if code:
        # Pattern confirmed: https://ncert.nic.in/ncerts/l/femh101.pdf
        return f"https://ncert.nic.in/ncerts/l/{grade_letter}{code}1{chapter_number:02d}.pdf"
    # fallback — user selects class / subject manually
    return "https://ncert.nic.in/textbook.php"


SUBJECT_DISPLAY = {
    'maths': 'Mathematics',
    'science': 'Science',
    'english': 'English',
    'social_science': 'Social Science',
    'kannada': 'Kannada',
}

# ── Grade-specific NCERT chapter titles ──────────────────────────────────────
# Keyed by (subject, grade).  Falls back to generic names if not found.
_CHAPTERS = {
    # ── MATHS ──────────────────────────────────────────────────────────────
    ('maths', 1): ["Shapes and Space", "Numbers from One to Nine", "Addition",
                   "Subtraction", "Numbers from Ten to Twenty", "Time",
                   "Measurement", "Numbers from Twenty-one to Fifty",
                   "Data Handling", "Patterns", "Numbers", "Money"],
    ('maths', 2): ["What is Long? What is Round?", "Counting in Groups",
                   "How Much Can You Carry?", "Counting in Tens", "Patterns",
                   "Footprints", "Jugs and Mugs", "Tens and Ones",
                   "My Funday", "Add our Points", "Lines and Lines",
                   "Give and Take", "The Longest Step", "Birds Come, Birds Go",
                   "How Many Ponytails?"],
    ('maths', 3): ["Where to Look From?", "Fun with Numbers", "Give and Take",
                   "Long and Short", "Shapes and Designs",
                   "Fun with Give and Take", "Time Goes On", "Who is Heavier?",
                   "How Many Times?", "Play with Patterns", "Jugs and Mugs",
                   "Can We Share?", "Smart Charts!", "Rupees and Paise"],
    ('maths', 4): ["Building with Bricks", "Long and Short", "A Trip to Bhopal",
                   "Tick-Tick-Tick", "The Way the World Looks", "The Junk Seller",
                   "Jugs and Mugs", "Carts and Wheels", "Halves and Quarters",
                   "Play with Patterns", "Tables and Shares",
                   "How Heavy? How Light?", "Fields and Fences", "Smart Charts"],
    ('maths', 5): ["The Fish Tale", "Shapes and Angles", "How Many Squares?",
                   "Parts and Wholes", "Does it Look the Same?",
                   "Be My Multiple, I'll be Your Factor",
                   "Can You See the Pattern?", "Mapping Your Way",
                   "Boxes and Sketches", "Tenths and Hundredths",
                   "Area and its Boundary", "Smart Charts",
                   "Ways to Multiply and Divide", "How Big? How Heavy?"],
    ('maths', 6): ["Knowing Our Numbers", "Whole Numbers",
                   "Playing with Numbers", "Basic Geometrical Ideas",
                   "Understanding Elementary Shapes", "Integers", "Fractions",
                   "Decimals", "Data Handling", "Mensuration", "Algebra",
                   "Ratio and Proportion"],
    ('maths', 7): ["Integers", "Fractions and Decimals", "Data Handling",
                   "Simple Equations", "Lines and Angles",
                   "The Triangle and its Properties", "Comparing Quantities",
                   "Rational Numbers", "Perimeter and Area",
                   "Algebraic Expressions", "Exponents and Powers",
                   "Symmetry", "Visualising Solid Shapes"],
    ('maths', 8): ["Rational Numbers", "Linear Equations in One Variable",
                   "Understanding Quadrilaterals", "Data Handling",
                   "Squares and Square Roots", "Cubes and Cube Roots",
                   "Comparing Quantities", "Algebraic Expressions and Identities",
                   "Mensuration", "Exponents and Powers",
                   "Direct and Inverse Proportions", "Factorisation",
                   "Introduction to Graphs"],
    ('maths', 9): ["Number Systems", "Polynomials", "Coordinate Geometry",
                   "Linear Equations in Two Variables",
                   "Introduction to Euclid's Geometry", "Lines and Angles",
                   "Triangles", "Quadrilaterals", "Circles",
                   "Heron's Formula", "Surface Areas and Volumes", "Statistics"],
    ('maths', 10): ["Real Numbers", "Polynomials",
                    "Pair of Linear Equations in Two Variables",
                    "Quadratic Equations", "Arithmetic Progressions",
                    "Triangles", "Coordinate Geometry",
                    "Introduction to Trigonometry",
                    "Some Applications of Trigonometry", "Circles",
                    "Areas Related to Circles", "Surface Areas and Volumes",
                    "Statistics", "Probability"],
    # ── SCIENCE ────────────────────────────────────────────────────────────
    ('science', 1): ["Plants Around Us", "Animals Around Us", "My Body",
                     "Food We Eat", "Clean Surroundings"],
    ('science', 2): ["Plants", "Animals", "Housing and Clothing",
                     "Food and Water", "Air, Water and Weather"],
    ('science', 3): ["Plants and Animals", "Food We Eat",
                     "Water", "Air Around Us", "Our Body"],
    ('science', 4): ["Plants: Parts and Functions", "Animals: Habitats",
                     "Food and Nutrition", "Rocks and Soil", "Forces and Energy"],
    ('science', 5): ["Super Senses", "A Snake Charmer's Story",
                     "From Tasting to Digesting", "Mangoes Round the Year",
                     "Seeds and Seeds", "Every Drop Counts",
                     "Experiments with Water", "A Treat for Mosquitoes",
                     "Up You Go!", "Walls Tell Stories",
                     "Sunita in Space", "What if it Finishes?",
                     "A Shelter so High!", "When the Earth Shook!",
                     "Blow Hot, Blow Cold", "Who Will Do This Work?",
                     "Across the Wall", "No Place for Us?",
                     "A Seed Tells a Farmer's Story", "Whose Forests?",
                     "Like Father, Like Daughter", "On the Move Again"],
    ('science', 6): ["Food: Where Does It Come From?", "Components of Food",
                     "Fibre to Fabric", "Sorting Materials and Groups",
                     "Separation of Substances", "Changes Around Us",
                     "Getting to Know Plants", "Body Movements",
                     "The Living Organisms and Their Surroundings",
                     "Motion and Measurement of Distances",
                     "Light, Shadows and Reflections",
                     "Electricity and Circuits", "Fun with Magnets",
                     "Water", "Air Around Us", "Garbage In, Garbage Out"],
    ('science', 7): ["Nutrition in Plants", "Nutrition in Animals",
                     "Fibre to Fabric", "Heat", "Acids, Bases and Salts",
                     "Physical and Chemical Changes",
                     "Weather, Climate and Adaptations of Animals to Climate",
                     "Winds, Storms and Cyclones", "Soil",
                     "Respiration in Organisms",
                     "Transportation in Animals and Plants",
                     "Reproduction in Plants", "Motion and Time",
                     "Electric Current and its Effects", "Light",
                     "Water: A Precious Resource", "Forests: Our Lifeline",
                     "Wastewater Story"],
    ('science', 8): ["Crop Production and Management",
                     "Microorganisms: Friend and Foe",
                     "Coal and Petroleum", "Combustion and Flame",
                     "Conservation of Plants and Animals",
                     "Reproduction in Animals",
                     "Reaching the Age of Adolescence",
                     "Force and Pressure", "Friction", "Sound",
                     "Chemical Effects of Electric Current",
                     "Some Natural Phenomena", "Light",
                     "Stars and the Solar System",
                     "Pollution of Air and Water"],
    ('science', 9): ["Matter in Our Surroundings",
                     "Is Matter Around Us Pure?",
                     "Atoms and Molecules", "Structure of the Atom",
                     "The Fundamental Unit of Life", "Tissues",
                     "Motion", "Force and Laws of Motion",
                     "Gravitation", "Work and Energy", "Sound",
                     "Improvement in Food Resources"],
    ('science', 10): ["Chemical Reactions and Equations",
                      "Acids, Bases and Salts", "Metals and Non-metals",
                      "Carbon and its Compounds", "Life Processes",
                      "Control and Coordination",
                      "How do Organisms Reproduce?", "Heredity",
                      "Light – Reflection and Refraction",
                      "Human Eye and the Colourful World",
                      "Electricity", "Magnetic Effects of Electric Current",
                      "Our Environment"],
    # ── ENGLISH ────────────────────────────────────────────────────────────
    ('english', 1): ["A Happy Child", "After a Bath", "One Little Kitten",
                     "Once I Saw a Little Bird", "Baba Blacksheep",
                     "Lalu and Peelu", "Cats", "Three Little Pigs"],
    ('english', 2): ["First Day at School", "Haldi's Adventure",
                     "I am Lucky!", "I Want", "A Smile", "The Wind and the Sun",
                     "Rain", "Storm in the Garden", "Zoo Manners",
                     "Funny Bunny", "Mr Nobody", "Curlylocks and the Three Bears",
                     "On My Blackboard I Can Draw", "Make it Shorter"],
    ('english', 3): ["Good Morning", "The Magic Garden", "Bird Talk",
                     "Nina and the Baby Sparrows", "Little By Little",
                     "The Enormous Turnip", "Sea Song", "A Little Fish Story",
                     "Don't Tell", "He is My Brother", "Furniture Rap",
                     "Puppy and I", "What's in the Mailbox?",
                     "Don't be Afraid of the Dark"],
    ('english', 4): ["Wake Up!", "Neha's Alarm Clock", "Noses",
                     "The Little Fir Tree", "Run!", "Nasruddin's Aim",
                     "Alice in Wonderland", "Don't be Afraid of the Dark",
                     "Pinocchio", "Helen Keller", "The Donkey"],
    ('english', 5): ["Ice-Cream Man", "Wonderful Waste!", "Teamwork",
                     "Flying Together", "My Shadow", "Robinson Crusoe",
                     "Crying", "My Elder Brother", "The Lazy Frog",
                     "Rip Van Winkle", "Class Discussion", "The Talkative Barber"],
    ('english', 6): ["Who Did Patrick's Homework?", "How the Dog Found Himself a Master",
                     "Taro's Reward", "An Indian-American Woman in Space",
                     "A Different Kind of School", "Who I Am",
                     "Fair Play", "A Game of Chance", "Desert Animals",
                     "The Banyan Tree", "A House, A Home", "The Kite",
                     "The Quarrel", "Beauty", "Where Do All the Teachers Go?",
                     "The Wonderful Words", "Vocation", "What if"],
    ('english', 7): ["Three Questions", "A Gift of Chappals",
                     "Gopal and the Hilsa Fish", "The Ashes That Made Trees Bloom",
                     "Quality", "Expert Detectives", "The Invention of Vita-Wonk",
                     "Fire: Friend and Foe", "A Bicycle in Good Repair",
                     "The Story of Cricket"],
    ('english', 8): ["The Best Christmas Present in the World", "The Tsunami",
                     "Glimpses of the Past", "Bepin Choudhury's Lapse of Memory",
                     "The Summit Within", "This is Jody's Fawn",
                     "A Visit to Cambridge", "A Short Monsoon Diary",
                     "The Great Stone Face–I", "The Great Stone Face–II"],
    ('english', 9): ["The Fun They Had", "The Sound of Music",
                     "The Little Girl", "A Truly Beautiful Mind",
                     "The Snake and the Mirror", "My Childhood",
                     "Packing", "Reach for the Top", "The Bond of Love",
                     "Kathmandu", "If I Were You"],
    ('english', 10): ["A Letter to God", "Nelson Mandela: Long Walk to Freedom",
                      "Two Stories about Flying", "From the Diary of Anne Frank",
                      "Glimpses of India", "Mijbil the Otter",
                      "Madam Rides the Bus", "The Sermon at Benares",
                      "The Proposal", "A Triumph of Surgery",
                      "The Thief's Story", "The Midnight Visitor",
                      "A Question of Trust", "Footprints without Feet",
                      "The Making of a Scientist", "The Necklace",
                      "The Hack Driver", "Bholi", "The Book That Saved the Earth"],
    # ── SOCIAL SCIENCE ─────────────────────────────────────────────────────
    ('social_science', 6): ["What, Where, How and When?",
                            "From Hunting-Gathering to Growing Food",
                            "In the Earliest Cities", "What Books and Burials Tell Us",
                            "Kingdoms, Kings and an Early Republic",
                            "New Questions and Ideas", "Ashoka, The Emperor Who Gave Up War",
                            "Vital Villages, Thriving Towns", "Traders, Kings and Pilgrims",
                            "New Empires and Kingdoms", "Buildings, Paintings and Books",
                            "The Earth in the Solar System", "Globe: Latitudes and Longitudes",
                            "Motions of the Earth", "Maps",
                            "Major Domains of the Earth",
                            "Major Landforms of the Earth",
                            "Our Country – India", "India: Climate, Vegetation and Wildlife",
                            "Understanding Diversity", "Diversity and Discrimination",
                            "What is Government?", "Key Elements of a Democratic Government",
                            "Panchayati Raj", "Rural Administration",
                            "Urban Administration", "Rural Livelihoods",
                            "Urban Livelihoods"],
    ('social_science', 9): ["The French Revolution", "Socialism in Europe and the Russian Revolution",
                            "Nazism and the Rise of Hitler",
                            "Forest Society and Colonialism",
                            "Pastoralists in the Modern World",
                            "India – Size and Location",
                            "Physical Features of India", "Drainage",
                            "Climate", "Natural Vegetation and Wild Life",
                            "Population", "What is Democracy? Why Democracy?",
                            "Constitutional Design", "Electoral Politics",
                            "Working of Institutions",
                            "Democratic Rights", "The Story of Village Palampur",
                            "People as Resource", "Poverty as a Challenge",
                            "Food Security in India"],
    ('social_science', 10): ["The Rise of Nationalism in Europe",
                             "Nationalism in India", "The Making of a Global World",
                             "The Age of Industrialisation", "Print Culture and the Modern World",
                             "Resources and Development", "Forest and Wildlife Resources",
                             "Water Resources", "Agriculture",
                             "Minerals and Energy Resources",
                             "Manufacturing Industries",
                             "Lifelines of National Economy",
                             "Power Sharing", "Federalism",
                             "Democracy and Diversity", "Gender, Religion and Caste",
                             "Popular Struggles and Movements",
                             "Political Parties", "Outcomes of Democracy",
                             "Challenges to Democracy",
                             "Development", "Sectors of the Indian Economy",
                             "Money and Credit", "Globalisation and the Indian Economy",
                             "Consumer Rights"],
    # ── KANNADA ────────────────────────────────────────────────────────────
    ('kannada', 1): ["Varnamale", "Akshara Abhyas", "Padagalu", "Vaakya Rachane",
                     "Chitra Varnane"],
    ('kannada', 2): ["Varnamale Abhyas", "Shabdagalu", "Vaakya Nirmana",
                     "Lekhana Abhyas", "Kavitha Parichaya"],
    ('kannada', 3): ["Akshara Parichaya", "Shabda Bhandara", "Vaakya Rachane",
                     "Gadya Paatha", "Padya Paatha", "Vyakarana Parichaya"],
    ('kannada', 4): ["Aksharamale", "Kannada Shabdagalu", "Vaakya Rachane",
                     "Gadya Bhaga", "Padya Bhaga", "Patra Lekhana"],
    ('kannada', 5): ["Kannada Varnamale", "Shabda Bhandara", "Vaakya Nirmana",
                     "Gadya Paatha", "Padya Paatha", "Vyakarana", "Prabandha"],
    ('kannada', 6): ["Nanna Kannadanadu", "Saahasada Kathe", "Prakriti Soundarya",
                     "Mahana Vyaktigalu", "Namma Aachara", "Kavitha Lahari",
                     "Vyakarana - Sandhi", "Lekhana Koushalya"],
    ('kannada', 7): ["Kannada Naadu Nudi", "Veeragathe", "Vigyana Priya",
                     "Naamma Dharma", "Jeevanadalli Saahasaya", "Kavitha",
                     "Vyakarana - Samaasa", "Prabandha Lekhana"],
    ('kannada', 8): ["Saadhana", "Samskruti", "Giri Saale", "Naadi Teera",
                     "Mahaakaavya Parichaya", "Aadhyatmika Chintha",
                     "Vyakarana - Krutha Prathyaya", "Nibandha"],
    ('kannada', 9): ["Rashtrakavi Kuvempu", "Naada Geethe",
                     "Pracheena Sahitya", "Vachana Sahitya",
                     "Adhunika Kavitha", "Gadya Saahitya",
                     "Vyakarana - Vibhakthi", "Prabandha"],
    ('kannada', 10): ["Jnaanapeetha Puraskrutha Lekhakaru",
                      "Karnataka Ekikarana", "Kannada Saahitya Charitre",
                      "Praacheena Kannada", "Madhyakaaleena Kavitha",
                      "Adhunika Gadya", "Vyakarana", "Prabandha Lekhana",
                      "Pariksha Tayyaari"],
}

_SUBJECT_DEFAULT_CHAPTERS = {
    'maths':         ["Introduction", "Basic Concepts", "Operations",
                      "Fractions and Decimals", "Geometry", "Measurement",
                      "Data Handling", "Algebra", "Problem Solving", "Revision"],
    'science':       ["Living World", "Materials", "Forces & Motion",
                      "Energy", "Environment", "Human Body",
                      "Plants", "Animals", "Earth & Space", "Technology"],
    'english':       ["Reading Skills", "Writing Skills", "Grammar",
                      "Vocabulary", "Literature", "Comprehension",
                      "Poetry", "Short Stories", "Communication", "Revision"],
    'social_science':["History", "Geography", "Civics",
                      "Economics", "Environment", "Maps & Globes",
                      "Government", "Culture", "Society", "Revision"],
    'kannada':       ["Varnamale", "Shabda Bhandara", "Vaakya Rachane",
                      "Gadya Paatha", "Padya Paatha", "Vyakarana",
                      "Lekhana", "Sahitya", "Kavitha", "Prabandha"],
}


def _chapter_titles(subject: str, grade: int):
    """Return grade-specific chapter titles, falling back to subject defaults."""
    specific = _CHAPTERS.get((subject, grade))
    if specific:
        return specific
    return _SUBJECT_DEFAULT_CHAPTERS.get(subject, [f"Chapter {i+1}" for i in range(10)])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_resource_links(request):
    """
    POST /api/resources/links/
    Body: { grade, subject, chapter_number, chapter_title? }
    Returns: { ncert_url, youtube_url, google_url, chapter_title }
    """
    grade = int(request.data.get('grade', 5))
    subject = request.data.get('subject', 'maths').lower()
    chapter_number = int(request.data.get('chapter_number', 1))
    chapter_title = request.data.get('chapter_title', f'Chapter {chapter_number}')

    subject_display = SUBJECT_DISPLAY.get(subject, subject.title())

    ncert_url = _ncert_chapter_url(grade, subject, chapter_number)

    yt_query = f"NCERT Class {grade} {subject_display} Chapter {chapter_number} {chapter_title} explanation"
    youtube_url = f"https://www.youtube.com/results?search_query={quote(yt_query)}"

    google_query = f"NCERT Class {grade} {subject_display} Chapter {chapter_number} {chapter_title} notes"
    google_url = f"https://www.google.com/search?q={quote(google_query)}"

    khan_query = f"{subject_display} Class {grade} {chapter_title}"
    khan_url = f"https://www.khanacademy.org/search?page_search_query={quote(khan_query)}"

    return Response({
        'ncert_url': ncert_url,
        'youtube_url': youtube_url,
        'google_url': google_url,
        'khan_url': khan_url,
        'chapter_title': chapter_title,
        'grade': grade,
        'subject': subject_display,
        'chapter_number': chapter_number,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chapters_for_subject(request):
    """
    GET /api/resources/chapters-list/?grade=5&subject=maths
    Returns a simple list of chapters with titles so the frontend
    can render them without needing DB-seeded Chapter rows.
    """
    grade = int(request.GET.get('grade', 5))
    subject = request.GET.get('subject', 'maths').lower()
    subject_display = SUBJECT_DISPLAY.get(subject, subject.title())

    # Try DB first
    db_chapters = Chapter.objects.filter(
        subject__name=subject, grade=grade
    ).order_by('chapter_number')

    if db_chapters.exists():
        chapters = [
            {'number': ch.chapter_number, 'title': ch.title}
            for ch in db_chapters
        ]
    else:
        # Fall back to hardcoded titles
        titles = _chapter_titles(subject, grade)
        chapters = [
            {'number': i + 1, 'title': title}
            for i, title in enumerate(titles)
        ]

    return Response({
        'grade': grade,
        'subject': subject,
        'subject_display': subject_display,
        'chapters': chapters,
    })

class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['subject', 'grade']
    ordering = ['grade', 'chapter_number']

class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.filter(is_approved=True)
    serializer_class = ResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['grade', 'subject', 'resource_type', 'chapter']
    search_fields = ['title', 'description']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return ResourceUploadSerializer
        return ResourceSerializer

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'teacher_profile'):
            return Response(
                {'error': 'Only teachers can upload resources'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resource = serializer.save(
            uploaded_by=request.user.teacher_profile,
            is_approved=True  # Auto-approve for now
        )
        
        return Response(
            ResourceSerializer(resource).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def download(self, request, pk=None):
        resource = self.get_object()
        student = request.user.student_profile
        
        download, created = StudentResourceDownload.objects.get_or_create(
            student=student,
            resource=resource
        )
        
        # Increment download count
        resource.download_count += 1
        resource.save()
        
        return Response({
            'message': 'Resource downloaded',
            'file_path': resource.file_path,
            'file_size': resource.file_size
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_downloads(self, request):
        student = request.user.student_profile
        downloads = StudentResourceDownload.objects.filter(student=student).order_by('-downloaded_at')
        serializer = StudentResourceDownloadSerializer(downloads, many=True)
        return Response(serializer.data)
