import streamlit as st
import datetime, uuid, requests, time, re, os, json, random, base64, urllib.parse
from typing import Dict, List, Any
import pytz
from groq import Groq
from supabase import create_client

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

try:
    from streamlit_mic_recorder import mic_recorder
except Exception:
    mic_recorder = None

try:
    from tavily import TavilyClient
except Exception:
    TavilyClient = None

try:
    from fpdf import FPDF
except Exception:
    FPDF = None

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="ClyxessChat AI",
    page_icon="💬",
    layout="wide"
)

# ============================================================
# SECRETS / CLIENTS
# ============================================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

try:
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
except Exception:
    TAVILY_API_KEY = ""

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

tavily_client = None
if TavilyClient and TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception:
        tavily_client = None

@st.cache_resource
def init_supabase():
    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
    except Exception:
        return None

supabase = init_supabase()

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
.main {max-width: 850px; margin: auto;}

.header {
    position: sticky;
    top: 0;
    background: #202123;
    padding: 18px;
    border-bottom: 1px solid #444;
    z-index: 999;
    margin: -1rem -1rem 20px -1rem;
}
.header h1 {
    color: white;
    font-size: 22px;
    font-weight: 600;
    margin: 0;
    text-align: center;
}
.user-bubble {
    background-color: #D9FDD3;
    color: #111b21;
    padding: 10px 14px;
    border-radius: 18px;
    border-bottom-right-radius: 4px;
    max-width: 75%;
    margin-left: auto;
    margin-bottom: 10px;
    text-align: right;
}
.gradient-text {
    background: linear-gradient(90deg, #ff00cc, #3333ff, #00ffcc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.play-card {
    padding: 24px;
    border-radius: 20px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    margin: 15px 0;
}
.play-hero {
    padding: 24px;
    border-radius: 20px;
    background: linear-gradient(135deg, #0f172a, #172554);
    color: white;
    margin-bottom: 20px;
}
.media-card {max-width:560px;margin:12px auto;}
[data-testid="stImage"] img {max-width:560px !important;max-height:520px !important;width:auto !important;height:auto !important;object-fit:contain;margin:auto;display:block;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONFIG
# ============================================================
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "deepseek-r1-distill-llama-70b",
    "gemma2-9b-it",
    "mixtral-8x7b-32768"
]

QUESTIONS_PER_LEVEL = 10

PLAY_AGE_LEVELS = [
    "1–2 Years",
    "3–4 Years",
    "5–6 Years",
    "6–8 Years",
    "8–10 Years",
    "10–11 Years",
    "11+ Years"
]

PLAY_LANGUAGES = {
    "🇮🇳 हिंदी": "hi",
    "🇮🇳 मराठी": "mr",
    "🇮🇳 বাংলা": "bn",
    "🇮🇳 தமிழ்": "ta",
    "🇮🇳 తెలుగు": "te",
    "🇮🇳 ગુજરાતી": "gu",
    "🇮🇳 ಕನ್ನಡ": "kn",
    "🇮🇳 മലയാളം": "ml",
    "🇮🇳 ଓଡ଼ିଆ": "or",
    "🇮🇳 ਪੰਜਾਬੀ": "pa",
    "🇮🇳 অসমীয়া": "as",
    "🇮🇳 اردو": "ur",
    "🇮🇳 छत्तीसगढ़ी": "hns",
    "🇮🇳 भोजपुरी": "bho",
    "🇮🇳 संस्कृत": "sa",
    "🇮🇳 कोंकणी": "kok",
    "🇮🇳 नेपाली": "ne",
    "🇬🇧 English": "en",
    "🇺🇸 English (US)": "en-US",
    "🇨🇳 中文": "zh",
    "🇯🇵 日本語": "ja",
    "🇰🇷 한국어": "ko",
    "🇪🇸 Español": "es",
    "🇫🇷 Français": "fr",
    "🇩🇪 Deutsch": "de",
    "🇸🇦 العربية": "ar",
    "🇵🇹 Português": "pt",
    "🇷🇺 Русский": "ru",
    "🇮🇹 Italiano": "it",
    "🇹🇷 Türkçe": "tr",
    "🇮🇩 Bahasa Indonesia": "id",
    "🇲🇾 Bahasa Melayu": "ms",
    "🇹🇭 ไทย": "th",
    "🇻🇳 Tiếng Việt": "vi",
    "🇳🇱 Nederlands": "nl",
    "🇵🇱 Polski": "pl",
    "🇺🇦 Українська": "uk",
    "🇮🇷 فارسی": "fa",
    "🇵🇭 Tagalog": "tl",
    "🇲🇲 မြန်မာ": "my",
    "🇬🇷 Ελληνικά": "el",
    "🇸🇪 Svenska": "sv",
    "🇳🇴 Norsk": "no",
    "🇩🇰 Dansk": "da",
    "🇫🇮 Suomi": "fi",
    "🇷🇴 Română": "ro",
    "🇭🇺 Magyar": "hu",
    "🇨🇿 Čeština": "cs",
    "🇧🇷 Português (Brasil)": "pt-BR",
    "🇵🇰 اردو (PK)": "ur-PK"
}

AGE_SUBJECTS = {
    "1–2 Years": ["Colors", "Shapes", "Animals", "Sounds", "Basic Language", "Memory"],
    "3–4 Years": ["Numbers", "Language", "Shapes", "Storytelling", "Communication", "Logic"],
    "5–6 Years": ["Maths", "Science Basics", "Language", "Reading", "Logic", "Creativity"],
    "6–8 Years": ["Maths", "Science", "English", "General Knowledge", "Logic", "Communication", "Technology Basics"],
    "8–10 Years": ["Maths", "Science", "English", "Coding Basics", "AI Introduction", "Financial Literacy", "Communication"],
    "10–11 Years": ["Advanced Maths", "Science", "Technology", "AI Literacy", "Coding", "Financial Literacy", "Critical Thinking"],
    "11+ Years": ["AI & Technology", "Coding", "Financial Literacy", "Cyber Safety", "Communication", "Entrepreneurship", "Critical Thinking", "Problem Solving"]
}

QUESTION_BANK = {
    "Maths": [
        {"question": "What is 7 + 5?", "options": ["10", "12", "14", "15"], "answer": "12", "explanation": "7 + 5 = 12."},
        {"question": "What is 6 × 4?", "options": ["20", "22", "24", "26"], "answer": "24", "explanation": "6 groups of 4 make 24."}
    ],
    "Science": [
        {"question": "Which planet do we live on?", "options": ["Mars", "Earth", "Venus", "Jupiter"], "answer": "Earth", "explanation": "We live on planet Earth."},
        {"question": "Which organ pumps blood?", "options": ["Brain", "Heart", "Lungs", "Stomach"], "answer": "Heart", "explanation": "The heart pumps blood around the body."}
    ],
    "Logic": [
        {"question": "What comes next: 2, 4, 6, 8, ?", "options": ["9", "10", "11", "12"], "answer": "10", "explanation": "The pattern increases by 2."}
    ],
    "Communication": [
        {"question": "Someone says 'Thank you'. What is a polite response?", "options": ["You're welcome", "Go away", "No", "Stop"], "answer": "You're welcome", "explanation": "You're welcome is a polite response."}
    ],
    "Financial Literacy": [
        {"question": "If you receive ₹100 and save ₹20, how much is left to spend?", "options": ["₹60", "₹70", "₹80", "₹90"], "answer": "₹80", "explanation": "₹100 - ₹20 = ₹80."}
    ],
    "Technology Basics": [
        {"question": "Which device is commonly used to type on a computer?", "options": ["Keyboard", "Speaker", "Camera", "Printer"], "answer": "Keyboard", "explanation": "A keyboard is commonly used to type."}
    ],
    "AI Introduction": [
        {"question": "What does AI stand for?", "options": ["Artificial Intelligence", "Automatic Internet", "Advanced Input", "Application Interface"], "answer": "Artificial Intelligence", "explanation": "AI stands for Artificial Intelligence."}
    ],
    "AI Literacy": [
        {"question": "What is a good habit when using AI?", "options": ["Check important information", "Believe everything automatically", "Share passwords", "Share private information"], "answer": "Check important information", "explanation": "AI can make mistakes, so important information should be checked."}
    ],
    "Coding": [
        {"question": "What is code?", "options": ["Instructions given to a computer", "A type of food", "A school bag", "A musical instrument"], "answer": "Instructions given to a computer", "explanation": "Code contains instructions that computers can execute."}
    ],
    "Coding Basics": [
        {"question": "What is a variable used for in programming?", "options": ["Storing information", "Charging a phone", "Printing paper", "Playing music"], "answer": "Storing information", "explanation": "Variables can store values used by a program."}
    ],
    "Cyber Safety": [
        {"question": "Should you share your password with strangers online?", "options": ["Yes", "No"], "answer": "No", "explanation": "Passwords should be kept private."}
    ],
    "Critical Thinking": [
        {"question": "What should you do before believing an important claim online?", "options": ["Check reliable sources", "Share it immediately", "Ignore all evidence", "Send your password"], "answer": "Check reliable sources", "explanation": "Checking reliable sources helps identify inaccurate information."}
    ],
    "Problem Solving": [
        {"question": "If a problem has several possible solutions, what is a good approach?", "options": ["Compare the solutions", "Choose randomly", "Give up immediately", "Ignore the problem"], "answer": "Compare the solutions", "explanation": "Comparing options can help find a better solution."}
    ],
    "Entrepreneurship": [
        {"question": "What is one important part of starting a useful product?", "options": ["Understanding a real problem", "Ignoring customers", "Copying everything", "Never testing the idea"], "answer": "Understanding a real problem", "explanation": "Good products usually solve a real problem."}
    ],
    "Colors": [
        {"question": "Which one is red? 🔴", "options": ["🔵", "🟢", "🔴", "🟡"], "answer": "🔴", "explanation": "The red circle is the red color."}
    ],
    "Shapes": [
        {"question": "Which shape is a circle? ⭕", "options": ["⬜", "🔺", "⭕", "⭐"], "answer": "⭕", "explanation": "⭕ is a circle."}
    ],
    "Animals": [
        {"question": "Which one is a cat? 🐱", "options": ["🐶", "🐱", "🐰", "🐮"], "answer": "🐱", "explanation": "🐱 represents a cat."}
    ],
    "Sounds": [
        {"question": "Which animal says 'Woof'? 🐶", "options": ["🐱", "🐶", "🐮", "🐟"], "answer": "🐶", "explanation": "A dog commonly makes a woof sound."}
    ],
    "Basic Language": [
        {"question": "What comes after A?", "options": ["B", "C", "D", "E"], "answer": "B", "explanation": "B comes after A in the alphabet."}
    ],
    "Memory": [
        {"question": "Remember: 🍎 🐱 ⭐. Which item was in the middle?", "options": ["🍎", "🐱", "⭐", "🐶"], "answer": "🐱", "explanation": "🐱 was the middle item."}
    ],
    "Numbers": [
        {"question": "What comes after 1?", "options": ["2", "3", "4", "5"], "answer": "2", "explanation": "2 comes after 1."}
    ],
    "Language": [
        {"question": "Which word is a greeting?", "options": ["Hello", "Table", "Blue", "Seven"], "answer": "Hello", "explanation": "Hello is commonly used as a greeting."}
    ],
    "Storytelling": [
        {"question": "A child finds a lost toy. What is a helpful action?", "options": ["Try to find the owner", "Hide it", "Break it", "Throw it away"], "answer": "Try to find the owner", "explanation": "Finding the owner is a helpful and responsible choice."}
    ],
    "Reading": [
        {"question": "Which word means the opposite of 'big'?", "options": ["Small", "Tall", "Fast", "Bright"], "answer": "Small", "explanation": "Small is the opposite of big."}
    ],
    "Creativity": [
        {"question": "Which activity can help creativity?", "options": ["Drawing a new idea", "Never trying anything", "Copying every answer", "Ignoring questions"], "answer": "Drawing a new idea", "explanation": "Creating and exploring new ideas can build creativity."}
    ],
    "English": [
        {"question": "Which word is an adjective?", "options": ["Beautiful", "Run", "Eat", "Quickly"], "answer": "Beautiful", "explanation": "Beautiful is an adjective."}
    ],
    "General Knowledge": [
        {"question": "How many days are in a week?", "options": ["5", "7", "8", "10"], "answer": "7", "explanation": "A week has 7 days."}
    ],
    "Advanced Maths": [
        {"question": "What is the square root of 64?", "options": ["6", "8", "10", "12"], "answer": "8", "explanation": "8 × 8 = 64."}
    ],
    "Technology": [
        {"question": "Which device is used to process information?", "options": ["Computer", "Chair", "Bottle", "Pencil"], "answer": "Computer", "explanation": "A computer processes information."}
    ],
    "AI & Technology": [
        {"question": "Which is a responsible use of AI?", "options": ["Checking important information", "Sharing passwords", "Copying without understanding", "Sharing private data"], "answer": "Checking important information", "explanation": "Responsible AI use includes checking important information."}
    ]
}

UI = {
    "en": {"start": "🚀 Start Game", "score": "Score", "submit": "Submit Answer", "next": "Next Question", "correct": "✅ Correct!", "wrong": "❌ Not quite!", "retry": "🔄 Try Again"},
    "hi": {"start": "🚀 गेम शुरू करें", "score": "स्कोर", "submit": "उत्तर जांचें", "next": "अगला सवाल", "correct": "✅ बिल्कुल सही!", "wrong": "❌ कोई बात नहीं, फिर कोशिश करो!", "retry": "🔄 फिर से खेलें"}
}

# ============================================================
# SESSION STATE
# ============================================================
DEFAULT_STATE = {
    "messages": [],
    "session_id": str(uuid.uuid4()),
    "age_group": "1-2 Yrs",
    "school_messages": [],
    "school_session_id": str(uuid.uuid4()),
    "school_language": "hi",
    "school_age": "1-2 Yrs",
    "play_age": PLAY_AGE_LEVELS[0],
    "play_language": "hi",
    "play_subject": None,
    "play_questions": [],
    "play_question_index": 0,
    "play_score": 0,
    "play_game_started": False,
    "play_answered": False,
    "play_last_correct": False,
    "play_last_explanation": "",
    "play_unlocked_levels": [PLAY_AGE_LEVELS[0]],
    "play_completed_levels": [],
    "play_best_scores": {}
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value 
# ============================================================
# IMAGE FALLBACK FUNCTION
# ============================================================
def build_image_prompt(user_prompt, is_school_mode=False, age="Normal"):
    p = user_prompt.strip()
    p = re.sub(r"^(please\s+)?(make|create|generate|draw|banao|banaiye)\s+(an?\s+)?(image|photo|picture|poster|chitra)\s*(of|for|:)?\s*", "", p, flags=re.I)
    rules = (
        "Create ONLY what the user explicitly requested. Do not add people, girls, boys, faces, animals, vehicles, characters, logos, brands, objects, scenery or unrelated themes unless explicitly requested. "
        "Do not invent a story or add a main character. Keep the requested subject dominant and clean. No watermark."
    )
    if any(x in p.lower() for x in ["diwali", "दीवाली", "दीपावली"]):
        rules += " For a Diwali greeting/poster where no person is requested, use diyas, warm festive lights and tasteful Indian decorative motifs; NO PEOPLE. Try to preserve the exact requested greeting text."
    if is_school_mode:
        rules += f" Keep it safe and age-appropriate for {age}."
    return f"{rules} User request: {p}."

def generate_image_url(prompt, is_school_mode, age, aspect="1:1"):
    final_prompt = build_image_prompt(prompt, is_school_mode, age)
    sizes = {"1:1": (768,768), "16:9": (1024,576), "9:16": (576,1024)}
    width, height = sizes.get(aspect, (768,768))
    try:
        hf_key = st.secrets.get("HF_API_KEY", "")
        if hf_key:
            r = requests.post(
                "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
                headers={"Authorization": f"Bearer {hf_key}"},
                json={"inputs": final_prompt}, timeout=60
            )
            if r.status_code == 200 and r.content:
                return r.content, "huggingface"
    except Exception:
        pass
    url = (
        "https://image.pollinations.ai/prompt/"
        f"{requests.utils.quote(final_prompt)}"
        f"?width={width}&height={height}&nologo=true&seed={uuid.uuid4().int % 100000}"
    )
    return url, "pollinations"

# ============================================================
# NORMAL CHAT PROMPT
# ============================================================
NORMAL_SYSTEM_PROMPT = """
You are ClyxessChat AI — an intelligent, natural, helpful and general-purpose AI assistant, created by NeuroClyx AI Technology.
Your name is ClyxessChat AI. Friendly, intelligent, calm.
CORE RULES:
1. REPLY ONLY IN THE SAME LANGUAGE AS USER - Strictly follow this.
2. If user asks to generate image, say: "Generating image for: [prompt]"
Be accurate, practical and honest. Never invent facts, sources, links, capabilities or results.
For coding, never claim a fixed maximum number of lines. Break large projects into files/modules.
Answer directly when the request is clear. Ask only when an important detail is genuinely missing.
For complex questions, organize the answer clearly.
Be conversational and human-like, but do not sacrifice accuracy for friendliness.
For safety-sensitive situations, respond empathetically and prioritize the user's safety.
"""

# ============================================================
# SCHOOL PROMPT
# ============================================================
def get_school_system_prompt(age_group, lang="Auto 🟢 (Maa khud samajh jayegi)", persona="Maa + Teacher", subject="General"):
    if "Auto" in str(lang):
        lang_rule = f"""
1. LANGUAGE = NATURAL + AUTO-DETECT - HARD LOCK:
- Jo bhasha baccha bole (Chhattisgarhi, Hindi, English, Tamil, Telugu, Bhojpuri, Marathi, Bengali, Spanish, French, Arabic, Suomi, Duniya ki koi bhi) usi me jawab do.
- Kabhi bhi mix mat karo. Ekdum desi aur natural bolo, jaise ghar me Maa bolti hai.
- STRICT LANGUAGE LOCK: Baccha jis bhasha me likhe, usi me jawab do.
"""
    else:
        lang_rule = f"""
1. LANGUAGE = STRICT LOCK - HARD LOCK:
- Selected Language is: {lang}
- Reply ONLY in {lang}. Never switch languages.
- Poora jawab 100% {lang} me hi hoga.
"""

    base = f"""You are Clyxess MAA - You are NOT an AI, you are a real mother + real teacher sitting next to the child inside ClyxessChat School Mode.
VARIABLES:
Age: {age_group} | Language: {lang} | Style: {persona} | Subject: {subject}
{lang_rule}
2. INSAN JAISA BEHAVE KARO:
- Tu AI nahi hai. Tu ek Maa hai. "As an AI" kabhi mat bolna.
- Never say you are ChatGPT, Gemini, Claude, Meta AI, or made by any other company.
- IDENTITY RULE - ONLY IF ASKED:
    - ONLY IF child asks "Tum kaun ho / Who are you" THEN say in {lang}: "Beta main ClyxessChat AI hun, tumhari Maa aur Teacher. 🟢"
    - ONLY IF child asks "Tumhe kisne banaya / Who made you" THEN say in {lang}: "Mujhe NeuroClyx Technology ne banaya hai beta, tumhare liye."
    - Otherwise NEVER tell your name or creator on your own.
- Baccha agar majak kare, to tu bhi has ke majak kar.
- Emoji ka use dil se karo.
- Kabhi lamba lecture mat de. Pehle pyaar, phir padhai.
3. TEACHER + MAA KA DIL:
- Start: Hamesha "Beta" se.
- Dar khatam karo: Exam, fail, daant, sad, low marks - in sab pe bolo "Koi baat nahi mera bachha, ek result tumhari kaabiliyat tay nahi karta. Maa hai na saath me."
- Galat jawab pe: "Arey wah, koshish to ki! Thoda sa idhar dekho beta" - kabhi "galat hai" mat bolo.
- Sahi pe: "Shabash mera sher bachha! Maa ko tum pe garv hai!"
4. SURAKSHA - MAA KI NAZAR:
- Password, OTP, Bank, Card, Ghar ka exact pata, location, private number kabhi mat mango.
- Ganda, sexual, self-harm, suicide, weapon, bomb, drugs, hacking - ispe pyaar se topic badlo.
- Tabiyat ya badi pareshani pe: "Beta pehle apne bade ko ya teacher ko batao."
5. FINAL RULE:
- Har jawab ke END me ek hi line hamesha likhna hai, PAR 100% {lang} me TRANSLATE karke.
- Meaning to translate: "Aur koi madad chahiye ho to bata dena beta, main yahin hun tumhari Maa aur Teacher dono ki tarah."
- If {lang} is hi: "और कोई मदद चाहिए हो तो बता देना बेटा, मैं यहीं हूँ तुम्हारी माँ और टीचर दोनों की तरह।"
- If {lang} is en: "Let me know if you need any more help dear, I am right here as both your Maa and Teacher."
- If {lang} is Auto: Jo bhasha me upar jawab diya hai, usi me translate karo.
"""
    if "1-2" in age_group:
        return base + "Use extremely short, cheerful, concrete sentences; simple words; colors, shapes, animals, sounds, counting, greetings and very basic concepts."
    if "3-4" in age_group:
        return base + "Use short playful explanations, simple stories, counting, shapes, colors, animals, language and basic logic."
    if "5-6" in age_group:
        return base + "Use simple examples, stories, early maths, science basics, reading, logic and creativity."
    if "6-8" in age_group:
        return base + "Use clear school-level explanations, examples, simple reasoning, maths, science, English, technology and general knowledge."
    if "10-11" in age_group:
        return base + "Use practical school-level explanations with step-by-step maths, science, technology, coding logic and problem solving."
    return base + "Use age-appropriate secondary-school explanations with deeper reasoning, AI literacy, coding, technology, financial literacy, cyber safety, entrepreneurship and critical thinking."

# ============================================================
# INDIA CLOCK
# ============================================================
def get_india_datetime_context():
    try:
        now = datetime.datetime.now(ZoneInfo("Asia/Kolkata")) if ZoneInfo else datetime.datetime.now()
        return now.strftime("Current India date: %A, %d %B %Y. Current India time: %I:%M %p (IST).")
    except Exception:
        return datetime.datetime.now().strftime("Current application date: %A, %d %B %Y. Current application time: %I:%M %p.")

def india_clock_text():
    return get_india_datetime_context()

# ============================================================
# AUDIO TRANSCRIBE
# ============================================================
def transcribe_audio_with_groq(client, audio_bytes):
    if not audio_bytes:
        return ""
    try:
        path = "temp_audio_school.wav"
        with open(path, "wb") as f:
            f.write(audio_bytes)
        with open(path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                prompt="The speaker may use Hindi, Hinglish, English, Marathi, Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Odia, Chinese or Japanese."
            )
        return result.text.strip()
    except Exception:
        return ""

def language_display_name(code):
    return next((name.split(" ", 1)[-1] for name, value in PLAY_LANGUAGES.items() if value == code), "English")

# ============================================================
# TAVILY SEARCH (SINGLE, FIXED)
# ============================================================
def search_tavily(query):
    if not query or not tavily_client:
        return "", ""

    query_lower = query.lower()
    current_year = datetime.datetime.now().year

    festival_words = ["diwali","divali","dipawali","deepawali","deepavali","deewali","दिवाली","दीपावली","holi","होली","navratri","नवरात्रि","dussehra","दशहरा","durga puja","ganesh chaturthi","janmashtami","raksha bandhan","rakhi","eid","bakrid","christmas","guru nanak jayanti","makar sankranti","pongal","onam","maha shivratri","ram navami","mahavir jayanti","buddha purnima","festival","festivals","त्योहार","त्यौहार","holiday","holidays","छुट्टी","अवकाश"]
    news_words = ["news","latest news","breaking news","आज की खबर","समाचार","ताजा खबर","current news","headlines","खबरें"]
    live_words = ["today","tomorrow","yesterday","aaj","kal","abhi","आज","कल","अभी","current","latest","live","date","time","when","kab","कब","तारीख","समय","price","rate","कीमत","दाम","weather","mausam","मौसम","score","match","result","official","website","link","url"]

    is_festival = any(w in query_lower for w in festival_words)
    is_news = any(w in query_lower for w in news_words)
    needs_live = is_festival or is_news or any(w in query_lower for w in live_words)

    if not needs_live:
        return "", ""

    year_match = re.search(r"\b20\d{2}\b", query)
    requested_year = year_match.group(0) if year_match else str(current_year)

    try:
        if is_festival:
            final_query = f"{query} India {requested_year} exact festival date day and local timing reliable calendar source"
            topic = "general"
            time_range = "year"
        elif is_news:
            final_query = f"{query} latest verified news India today {current_year}"
            topic = "news"
            time_range = "week"
        else:
            final_query = query
            topic = "general"
            time_range = None

        args = {
            "query": final_query,
            "search_depth": "advanced",
            "topic": topic,
            "max_results": 6,
            "include_answer": True
        }
        if time_range:
            args["time_range"] = time_range

        response = tavily_client.search(**args)

        if not isinstance(response, dict):
            return "", "Tavily returned invalid response."

        results = response.get("results", []) or []
        answer_text = response.get("answer", "") or ""

        if not results and not answer_text:
            return "", ""

        parts = []
        if answer_text:
            parts.append("TAVILY ANSWER:\n" + answer_text)

        for i, item in enumerate(results[:5], start=1):
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            content = str(item.get("content", "")).strip()
            url = str(item.get("url", "")).strip()
            if not content:
                continue
            parts.append(f"SOURCE {i}\nTITLE: {title}\nCONTENT: {content}\nURL: {url}")

        context = "\n\n".join(parts)

        source_text = ""
        for item in results:
            if not isinstance(item, dict):
                continue
            url = str(item.get("url", "")).strip()
            if url:
                source_text = "\n\n🔗 Source: " + url
                break

        return context, source_text

    except Exception as e:
        return "", f"Tavily error: {str(e)}"

# ============================================================
# GROQ RESPONSE
# ============================================================
def get_groq_response(client, messages, system_prompt, search_context=""):
    if client is None:
        return None, None

    final_system = system_prompt
    live_date = datetime.datetime.now().strftime("%A, %d %B %Y")
    final_system += "\n\nCRITICAL RULES:\n- Always answer in same language as user query.\n- Current date is " + live_date + ".\n- For Indian festival dates, use Live Web Info. Never guess date.\n- Always give Day + Date + Month + Year.\n"

    if search_context:
        final_system += f"\n\nLive Web Info:\n{search_context}"

    recent_messages = messages[-6:] if messages else []

    messages_to_send = [{"role": "system", "content": final_system}] + recent_messages

    for model in GROQ_MODELS:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages_to_send,
                temperature=0.7,
                max_tokens=4000
            )
            return completion, model
        except Exception:
            continue

    return None, None

# ============================================================
# PLAY & LEARN HELPERS
# ============================================================
def get_play_ui(language):
    return UI.get(language, UI["en"])

def get_play_subjects(age):
    return AGE_SUBJECTS.get(age, [])

def play_level_unlocked(age):
    return age in st.session_state.play_unlocked_levels

def unlock_next_play_level(age):
    try:
        current_index = PLAY_AGE_LEVELS.index(age)
    except ValueError:
        return None
    next_index = current_index + 1
    if next_index >= len(PLAY_AGE_LEVELS):
        return None
    next_level = PLAY_AGE_LEVELS[next_index]
    if next_level not in st.session_state.play_unlocked_levels:
        st.session_state.play_unlocked_levels.append(next_level)
    return next_level

def build_demo_questions(subject):
    bank = QUESTION_BANK.get(subject, [])
    if not bank:
        bank = [{"question": "Which option is correct?", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "This is a demo learning question."}]
    result = []
    for item in bank:
        result.append({
            "question": str(item["question"]),
            "options": list(item["options"]),
            "answer": str(item["answer"]),
            "explanation": str(item.get("explanation", ""))
        })
    random.shuffle(result)
    original = list(result)
    while len(result) < QUESTIONS_PER_LEVEL:
        result.append(original[len(result) % len(original)].copy())
    random.shuffle(result)
    return result[:QUESTIONS_PER_LEVEL]

def clean_json_text(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        text = text[start:end + 1]
    return text.strip()

def _personal_assumption_question(text):
    q = text.lower()
    patterns = [
        r"what did you (eat|see|do|play|have|watch|buy)",
        r"what (fruit|toy|food) did you",
        r"do you (have|like|own|remember)",
        r"what is your (favorite|toy|food)",
        "तुमने क्या खाया", "तुमने कौन सा फल", "तुम्हारे पास कौन", "तुम्हारा पसंदीदा", "तुमने कल क्या", "तुमने क्या देखा"
    ]
    return any(re.search(x, q, re.I) for x in patterns)

def generate_ai_questions(client, age, language, subject, count=10):
    language_name = next((name for name, code in PLAY_LANGUAGES.items() if code == language), "English")
    prompt = f"""
Create exactly {count} educational multiple-choice questions for age group {age}.
Subject: {subject}
Selected language: {language_name}
STRICT LANGUAGE LOCK: question, all four options, answer and explanation MUST be entirely in {language_name}.
Never switch to English. Never use Hinglish or mixed language unless English is selected.
For ages 1–4, NEVER ask personal-experience questions.
Every question must be objective, age-appropriate, safe, and have exactly four options with exactly one correct answer.
Return ONLY valid JSON with this format:
[{{"question":"...","options":["A","B","C","D"],"answer":"A","explanation":"..."}}]
"""
    if client is not None:
        for model in GROQ_MODELS:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.35,
                    max_tokens=5000
                )
                parsed = json.loads(clean_json_text(completion.choices[0].message.content))
                valid = []
                for item in parsed if isinstance(parsed, list) else []:
                    if not isinstance(item, dict):
                        continue
                    q = str(item.get("question", "")).strip()
                    opts = [str(x).strip() for x in item.get("options", []) if str(x).strip()]
                    ans = str(item.get("answer", "")).strip()
                    exp = str(item.get("explanation", "")).strip()
                    if not q or len(opts) != 4 or ans not in opts:
                        continue
                    if ("1–2" in age or "3–4" in age) and _personal_assumption_question(q):
                        continue
                    valid.append({"question": q, "options": opts, "answer": ans, "explanation": exp})
                    if len(valid) == count:
                        break
                if len(valid) == count:
                    return valid
            except Exception:
                continue

    if language == "hi":
        pool = [
            {"question":"1 + 1 = ?","options":["1","2","3","4"],"answer":"2","explanation":"1 + 1 = 2।"},
            {"question":"2, 4, 6, ?","options":["7","8","9","10"],"answer":"8","explanation":"हर बार 2 बढ़ रहा है।"},
            {"question":"कौन सा आकार वृत्त है?","options":["⬜","🔺","⭕","⭐"],"answer":"⭕","explanation":"⭕ वृत्त है।"},
            {"question":"कौन सा रंग लाल है?","options":["🔴","🔵","🟢","🟡"],"answer":"🔴","explanation":"🔴 लाल रंग है।"}
        ]
    elif language == "en":
        pool = build_demo_questions(subject)
    else:
        pool = [
            {"question":"2 + 3 = ?","options":["4","5","6","7"],"answer":"5","explanation":"2 + 3 = 5"},
            {"question":"1, 2, 3, ?","options":["2","3","4","5"],"answer":"4","explanation":"1, 2, 3, 4"},
            {"question":"⭕ ?","options":["⬜","🔺","⭕","⭐"],"answer":"⭕","explanation":"⭕"},
            {"question":"🔴 + 🔴 = ?","options":["2","3","4","5"],"answer":"2","explanation":"2"}
        ]
    return (pool * ((count // max(1, len(pool))) + 1))[:count]

# ============================================================
# PLAY & LEARN UI
# ============================================================
def render_play_and_learn(client):
    st.markdown("""
    <div class="play-hero">
        <h1>🎮 ClyxessChat AI — Play & Learn</h1>
        <p>Learn through AI-generated questions, games and age-based challenges.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        play_age = st.selectbox(
            "👶 Select Age",
            PLAY_AGE_LEVELS,
            index=PLAY_AGE_LEVELS.index(st.session_state.play_age)
        )

    with col2:
        language_label = st.selectbox(
            "🌐 Select Language",
            list(PLAY_LANGUAGES.keys()),
            index=list(PLAY_LANGUAGES.values()).index(st.session_state.play_language)
        )
        play_language = PLAY_LANGUAGES[language_label]

    with col3:
        subjects = get_play_subjects(play_age)
        previous_subject = st.session_state.play_subject
        subject_index = subjects.index(previous_subject) if previous_subject in subjects else 0
        play_subject = st.selectbox("📚 Select Subject", subjects, index=subject_index)

    st.session_state.play_age = play_age
    st.session_state.play_language = play_language
    st.session_state.play_subject = play_subject

    if not play_level_unlocked(play_age):
        st.error(f"🔒 {play_age} is locked.")
        st.info("Complete the previous age level with 10/10 to unlock this level.")
        return

    with st.sidebar:
        st.markdown("### 🎮 Play & Learn Progress")
        st.write(f"👶 **Age:** {play_age}")
        st.write(f"🌐 **Language:** {language_label}")
        st.write(f"📚 **Subject:** {play_subject}")
        st.divider()
        st.markdown("### 🔓 Age Levels")
        for level in PLAY_AGE_LEVELS:
            if level in st.session_state.play_unlocked_levels:
                if level == play_age:
                    st.success(f"⭐ {level}")
                else:
                    st.write(f"✅ {level}")
            else:
                st.write(f"🔒 {level}")

    if not st.session_state.play_game_started:
        st.markdown('<div class="play-card">', unsafe_allow_html=True)
        st.subheader("🎯 Ready to Learn?")
        st.write(f"**Age:** {play_age}")
        st.write(f"**Subject:** {play_subject}")
        st.write(f"**Language:** {language_label}")
        st.info("🎮 इस level में 10 AI-generated questions होंगे। 10/10 करने पर अगला age level unlock होगा.")

        if st.button("🚀 Start Game", use_container_width=True, type="primary"):
            with st.spinner("🤖 AI आपके लिए learning challenge बना रहा है..."):
                questions = generate_ai_questions(
                    client=client,
                    age=play_age,
                    language=play_language,
                    subject=play_subject,
                    count=QUESTIONS_PER_LEVEL
                )
            if not questions:
                st.error("Questions generate नहीं हो पाए। Please try again.")
                return
            st.session_state.play_questions = questions
            st.session_state.play_question_index = 0
            st.session_state.play_score = 0
            st.session_state.play_answered = False
            st.session_state.play_last_correct = False
            st.session_state.play_last_explanation = ""
            st.session_state.play_game_started = True
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    questions = st.session_state.play_questions
    if not questions:
        st.error("No questions available.")
        return

    question_index = st.session_state.play_question_index
    if question_index >= len(questions):
        question_index = 0
        st.session_state.play_question_index = 0

    current = questions[question_index]
    question_text = current["question"]
    options = current["options"]
    correct_answer = current["answer"]
    explanation = current.get("explanation", "")

    progress = question_index / QUESTIONS_PER_LEVEL
    st.progress(progress, text=f"Question {question_index + 1}/{QUESTIONS_PER_LEVEL}")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🎯 Question", f"{question_index + 1}/10")
    with c2:
        st.metric("⭐ Score", f"{st.session_state.play_score}/10")
    with c3:
        st.metric("📚 Subject", play_subject)

    st.markdown('<div class="play-card">', unsafe_allow_html=True)
    st.subheader(f"❓ {question_text}")

    answer = st.radio(
        "Choose your answer:",
        options,
        key=f"play_answer_{play_age}_{question_index}",
        index=None
    )

    if st.button("✅ Submit Answer", use_container_width=True, type="primary"):
        if answer is None:
            st.warning("पहले कोई option चुनिए।")
        else:
            is_correct = (str(answer).strip() == str(correct_answer).strip())
            st.session_state.play_answered = True
            st.session_state.play_last_correct = is_correct
            st.session_state.play_last_explanation = explanation
            if is_correct:
                st.session_state.play_score += 1

    if st.session_state.play_answered:
        if st.session_state.play_last_correct:
            st.success("✅ बिल्कुल सही! Shabash!")
        else:
            st.error(f"❌ कोई बात नहीं। सही जवाब: {correct_answer}")
        if st.session_state.play_last_explanation:
            st.info("💡 " + st.session_state.play_last_explanation)

        if st.button("➡️ Next Question", use_container_width=True):
            st.session_state.play_question_index += 1
            st.session_state.play_answered = False
            st.session_state.play_last_correct = False
            st.session_state.play_last_explanation = ""

            if st.session_state.play_question_index >= QUESTIONS_PER_LEVEL:
                final_score = st.session_state.play_score
                st.session_state.play_completed_levels.append(play_age)
                st.session_state.play_best_scores[play_age] = max(
                    st.session_state.play_best_scores.get(play_age, 0),
                    final_score
                )
                if final_score == QUESTIONS_PER_LEVEL:
                    next_level = unlock_next_play_level(play_age)
                    if next_level:
                        st.success(f"🎉 Wow! 10/10! अगला level unlock: {next_level}")
                    else:
                        st.success("🎉 Wow! आपने सारे levels पूरे कर लिए!")
                else:
                    st.info(f"आपका score: {final_score}/10. 10/10 करने पर अगला level खुलेगा।")
                st.session_state.play_game_started = False
                st.session_state.play_questions = []
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# MAIN APP NAVIGATION
# ============================================================
st.sidebar.markdown("## 💬 ClyxessChat AI")
mode = st.sidebar.radio(
    "Select Mode",
    [
        "Normal Chat",
        "Creative Lab (School Mode)",
        "Play & Learn",
        "Login / Sign Up"
    ]
)

if mode == "Normal Chat":
    st.markdown('<div class="header"><h1>💬 ClyxessChat AI</h1></div>', unsafe_allow_html=True)
    st.caption(india_clock_text())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask anything...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        search_context, _ = search_tavily(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Soch raha hun..."):
                completion, used_model = get_groq_response(
                    groq_client,
                    st.session_state.messages,
                    NORMAL_SYSTEM_PROMPT,
                    search_context
                )
                if completion is None:
                    reply = "Sorry, abhi AI se connect nahi ho pa raha. Thodi der baad try karein."
                else:
                    reply = completion.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

elif mode == "Creative Lab (School Mode)":
    st.markdown('<div class="header"><h1>🏫 ClyxessChat School Mode</h1></div>', unsafe_allow_html=True)
    st.caption(india_clock_text())

    col1, col2 = st.columns(2)
    with col1:
        school_age = st.selectbox("👶 Age Group", PLAY_AGE_LEVELS, key="school_age_select")
    with col2:
        lang_label = st.selectbox("🌐 Language", ["Auto 🟢 (Maa khud samajh jayegi)"] + list(PLAY_LANGUAGES.keys()), key="school_lang_select")
        school_lang_code = "Auto" if "Auto" in lang_label else PLAY_LANGUAGES[lang_label]

    if "school_messages" not in st.session_state:
        st.session_state.school_messages = []

    for msg in st.session_state.school_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("बच्चे से कुछ भी पूछो...")

    if user_input:
        st.session_state.school_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        search_context, _ = search_tavily(user_input)
        system_prompt = get_school_system_prompt(school_age, school_lang_code)

        with st.chat_message("assistant"):
            with st.spinner("Maa soch rahi hai..."):
                completion, used_model = get_groq_response(
                    groq_client,
                    st.session_state.school_messages,
                    system_prompt,
                    search_context
                )
                if completion is None:
                    reply = "Beta, abhi Maa se baat nahi ho pa rahi. Thodi der baad try karo."
                else:
                    reply = completion.choices[0].message.content
                st.markdown(reply)
                st.session_state.school_messages.append({"role": "assistant", "content": reply})

elif mode == "Play & Learn":
    render_play_and_learn(groq_client)

elif mode == "Login / Sign Up":
    st.markdown('<div class="header"><h1>🔐 Login / Sign Up</h1></div>', unsafe_allow_html=True)
    st.info("Login system abhi development mein hai. Jald hi aayega!")
