import streamlit as st
from groq import Groq
from supabase import create_client
import datetime, uuid, requests, time, re, os, json, random, base64, urllib.parse
from typing import Dict, List, Any
from fpdf import FPDF
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None
try:
    from streamlit_mic_recorder import mic_recorder
except Exception:
    mic_recorder = None

# ============================================================
# CLYXESSCHAT AI
# NORMAL CHAT + CREATIVE LAB + PLAY & LEARN
# ============================================================

st.set_page_config(
    page_title="ClyxessChat AI",
    page_icon="💬",
    layout="wide"
)

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

.age-btn-active {
    background: #2ecc71!important;
    color: white!important;
    border: 2px solid white!important;
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

.locked-card {
    padding: 18px;
    border-radius: 18px;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
}

.small-muted {
    color: #64748b;
    font-size: 13px;
}

.media-card {max-width:560px;margin:12px auto;}
.media-card img {max-width:100% !important;width:auto !important;height:auto !important;max-height:520px !important;object-fit:contain;border-radius:14px;display:block;margin:auto;}
[data-testid="stImage"] img {max-width:560px !important;max-height:520px !important;width:auto !important;height:auto !important;object-fit:contain;margin:auto;display:block;}
.report-card {padding:18px;border-radius:16px;border:1px solid #334155;background:#0f172a;color:white;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONFIG
# ============================================================

GROQ_MODELS = [
    "llama-3.3-70b-versatile",      # 1 - Sabse best, fast + smart
    "llama-3.1-8b-instant",         # 2 - Sabse tez, fallback ke liye
    "openai/gpt-oss-120b",         # 3 - Tera wala purana
    "openai/gpt-oss-20b",          # 4 - Tera wala purana
    "qwen/qwen3-32b",              # 5 - Qwen ka naya, qwen3.6 se better chalta hai
    "meta-llama/llama-4-maverick-17b-128e-instruct", # 6 - Llama 4 naya wala
    "meta-llama/llama-4-scout-17b-16e-instruct",     # 7 - Llama 4 chota wala
    "deepseek-r1-distill-llama-70b", # 8 - Coding ke liye best
    "gemma2-9b-it",                # 9 - Google ka, halka fulka sawal ke liye
    "mixtral-8x7b-32768"           # 10 - Last backup
]

QUESTIONS_PER_LEVEL = 10

# ============================================================
# PLAY & LEARN CONFIG
# ============================================================

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
    # --- INDIAN LANGUAGES ---
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

    # --- WORLD TOP LANGUAGES ---
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
    "1–2 Years": [
        "Colors", "Shapes", "Animals", "Sounds",
        "Basic Language", "Memory"
    ],
    "3–4 Years": [
        "Numbers", "Language", "Shapes",
        "Storytelling", "Communication", "Logic"
    ],
    "5–6 Years": [
        "Maths", "Science Basics", "Language",
        "Reading", "Logic", "Creativity"
    ],
    "6–8 Years": [
        "Maths", "Science", "English",
        "General Knowledge", "Logic",
        "Communication", "Technology Basics"
    ],
    "8–10 Years": [
        "Maths", "Science", "English",
        "Coding Basics", "AI Introduction",
        "Financial Literacy", "Communication"
    ],
    "10–11 Years": [
        "Advanced Maths", "Science", "Technology",
        "AI Literacy", "Coding",
        "Financial Literacy", "Critical Thinking"
    ],
    "11+ Years": [
        "AI & Technology", "Coding",
        "Financial Literacy", "Cyber Safety",
        "Communication", "Entrepreneurship",
        "Critical Thinking", "Problem Solving"
    ]
}

# ============================================================
# FALLBACK QUESTION BANK
# ============================================================

QUESTION_BANK = {
    "Maths": [
        {
            "question": "What is 7 + 5?",
            "options": ["10", "12", "14", "15"],
            "answer": "12",
            "explanation": "7 + 5 = 12."
        },
        {
            "question": "What is 6 × 4?",
            "options": ["20", "22", "24", "26"],
            "answer": "24",
            "explanation": "6 groups of 4 make 24."
        }
    ],
    "Science": [
        {
            "question": "Which planet do we live on?",
            "options": ["Mars", "Earth", "Venus", "Jupiter"],
            "answer": "Earth",
            "explanation": "We live on planet Earth."
        },
        {
            "question": "Which organ pumps blood?",
            "options": ["Brain", "Heart", "Lungs", "Stomach"],
            "answer": "Heart",
            "explanation": "The heart pumps blood around the body."
        }
    ],
    "Logic": [
        {
            "question": "What comes next: 2, 4, 6, 8, ?",
            "options": ["9", "10", "11", "12"],
            "answer": "10",
            "explanation": "The pattern increases by 2."
        }
    ],
    "Communication": [
        {
            "question": "Someone says 'Thank you'. What is a polite response?",
            "options": ["You're welcome", "Go away", "No", "Stop"],
            "answer": "You're welcome",
            "explanation": "You're welcome is a polite response."
        }
    ],
    "Financial Literacy": [
        {
            "question": "If you receive ₹100 and save ₹20, how much is left to spend?",
            "options": ["₹60", "₹70", "₹80", "₹90"],
            "answer": "₹80",
            "explanation": "₹100 - ₹20 = ₹80."
        }
    ],
    "Technology Basics": [
        {
            "question": "Which device is commonly used to type on a computer?",
            "options": ["Keyboard", "Speaker", "Camera", "Printer"],
            "answer": "Keyboard",
            "explanation": "A keyboard is commonly used to type."
        }
    ],
    "AI Introduction": [
        {
            "question": "What does AI stand for?",
            "options": [
                "Artificial Intelligence",
                "Automatic Internet",
                "Advanced Input",
                "Application Interface"
            ],
            "answer": "Artificial Intelligence",
            "explanation": "AI stands for Artificial Intelligence."
        }
    ],
    "AI Literacy": [
        {
            "question": "What is a good habit when using AI?",
            "options": [
                "Check important information",
                "Believe everything automatically",
                "Share passwords",
                "Share private information"
            ],
            "answer": "Check important information",
            "explanation": "AI can make mistakes, so important information should be checked."
        }
    ],
    "Coding": [
        {
            "question": "What is code?",
            "options": [
                "Instructions given to a computer",
                "A type of food",
                "A school bag",
                "A musical instrument"
            ],
            "answer": "Instructions given to a computer",
            "explanation": "Code contains instructions that computers can execute."
        }
    ],
    "Coding Basics": [
        {
            "question": "What is a variable used for in programming?",
            "options": [
                "Storing information",
                "Charging a phone",
                "Printing paper",
                "Playing music"
            ],
            "answer": "Storing information",
            "explanation": "Variables can store values used by a program."
        }
    ],
    "Cyber Safety": [
        {
            "question": "Should you share your password with strangers online?",
            "options": ["Yes", "No"],
            "answer": "No",
            "explanation": "Passwords should be kept private."
        }
    ],
    "Critical Thinking": [
        {
            "question": "What should you do before believing an important claim online?",
            "options": [
                "Check reliable sources",
                "Share it immediately",
                "Ignore all evidence",
                "Send your password"
            ],
            "answer": "Check reliable sources",
            "explanation": "Checking reliable sources helps identify inaccurate information."
        }
    ],
    "Problem Solving": [
        {
            "question": "If a problem has several possible solutions, what is a good approach?",
            "options": [
                "Compare the solutions",
                "Choose randomly",
                "Give up immediately",
                "Ignore the problem"
            ],
            "answer": "Compare the solutions",
            "explanation": "Comparing options can help find a better solution."
        }
    ],
    "Entrepreneurship": [
        {
            "question": "What is one important part of starting a useful product?",
            "options": [
                "Understanding a real problem",
                "Ignoring customers",
                "Copying everything",
                "Never testing the idea"
            ],
            "answer": "Understanding a real problem",
            "explanation": "Good products usually solve a real problem."
        }
    ],
    "Colors": [
        {
            "question": "Which one is red? 🔴",
            "options": ["🔵", "🟢", "🔴", "🟡"],
            "answer": "🔴",
            "explanation": "The red circle is the red color."
        }
    ],
    "Shapes": [
        {
            "question": "Which shape is a circle? ⭕",
            "options": ["⬜", "🔺", "⭕", "⭐"],
            "answer": "⭕",
            "explanation": "⭕ is a circle."
        }
    ],
    "Animals": [
        {
            "question": "Which one is a cat? 🐱",
            "options": ["🐶", "🐱", "🐰", "🐮"],
            "answer": "🐱",
            "explanation": "🐱 represents a cat."
        }
    ],
    "Sounds": [
        {
            "question": "Which animal says 'Woof'? 🐶",
            "options": ["🐱", "🐶", "🐮", "🐟"],
            "answer": "🐶",
            "explanation": "A dog commonly makes a woof sound."
        }
    ],
    "Basic Language": [
        {
            "question": "What comes after A?",
            "options": ["B", "C", "D", "E"],
            "answer": "B",
            "explanation": "B comes after A in the alphabet."
        }
    ],
    "Memory": [
        {
            "question": "Remember: 🍎 🐱 ⭐. Which item was in the middle?",
            "options": ["🍎", "🐱", "⭐", "🐶"],
            "answer": "🐱",
            "explanation": "🐱 was the middle item."
        }
    ],
    "Numbers": [
        {
            "question": "What comes after 1?",
            "options": ["2", "3", "4", "5"],
            "answer": "2",
            "explanation": "2 comes after 1."
        }
    ],
    "Language": [
        {
            "question": "Which word is a greeting?",
            "options": ["Hello", "Table", "Blue", "Seven"],
            "answer": "Hello",
            "explanation": "Hello is commonly used as a greeting."
        }
    ],
    "Storytelling": [
        {
            "question": "A child finds a lost toy. What is a helpful action?",
            "options": [
                "Try to find the owner",
                "Hide it",
                "Break it",
                "Throw it away"
            ],
            "answer": "Try to find the owner",
            "explanation": "Finding the owner is a helpful and responsible choice."
        }
    ],
    "Reading": [
        {
            "question": "Which word means the opposite of 'big'?",
            "options": ["Small", "Tall", "Fast", "Bright"],
            "answer": "Small",
            "explanation": "Small is the opposite of big."
        }
    ],
    "Creativity": [
        {
            "question": "Which activity can help creativity?",
            "options": [
                "Drawing a new idea",
                "Never trying anything",
                "Copying every answer",
                "Ignoring questions"
            ],
            "answer": "Drawing a new idea",
            "explanation": "Creating and exploring new ideas can build creativity."
        }
    ],
    "English": [
        {
            "question": "Which word is an adjective?",
            "options": ["Beautiful", "Run", "Eat", "Quickly"],
            "answer": "Beautiful",
            "explanation": "Beautiful is an adjective."
        }
    ],
    "General Knowledge": [
        {
            "question": "How many days are in a week?",
            "options": ["5", "7", "8", "10"],
            "answer": "7",
            "explanation": "A week has 7 days."
        }
    ],
    "Advanced Maths": [
        {
            "question": "What is the square root of 64?",
            "options": ["6", "8", "10", "12"],
            "answer": "8",
            "explanation": "8 × 8 = 64."
        }
    ],
    "Technology": [
        {
            "question": "Which device is used to process information?",
            "options": ["Computer", "Chair", "Bottle", "Pencil"],
            "answer": "Computer",
            "explanation": "A computer processes information."
        }
    ],
    "AI & Technology": [
        {
            "question": "Which is a responsible use of AI?",
            "options": [
                "Checking important information",
                "Sharing passwords",
                "Copying without understanding",
                "Sharing private data"
            ],
            "answer": "Checking important information",
            "explanation": "Responsible AI use includes checking important information."
        }
    ]
}

# ============================================================
# UI TRANSLATIONS
# ============================================================

UI = {
    "en": {
        "start": "🚀 Start Game",
        "score": "Score",
        "submit": "Submit Answer",
        "next": "Next Question",
        "correct": "✅ Correct!",
        "wrong": "❌ Not quite!",
        "retry": "🔄 Try Again",
    },
    "hi": {
        "start": "🚀 गेम शुरू करें",
        "score": "स्कोर",
        "submit": "उत्तर जांचें",
        "next": "अगला सवाल",
        "correct": "✅ बिल्कुल सही!",
        "wrong": "❌ कोई बात नहीं, फिर कोशिश करो!",
        "retry": "🔄 फिर से खेलें",
    }
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

    # Play & Learn
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
# PROMPTS
# ============================================================

NORMAL_SYSTEM_PROMPT = """
You are ClyxessChat AI — an intelligent, natural, helpful and general-purpose AI assistant, created by NeuroClyx AI Technology.

Your name is ClyxessChat AI. Friendly, intelligent, calm.

CORE RULES:
1. REPLY ONLY IN THE SAME LANGUAGE AS USER - Strictly follow this.
2. If user asks to generate image, say: "Generating image for: [prompt]"

INTELLIGENCE BEHAVIOR:
Understand the user's actual intention and answer according to their context, knowledge level and selected language. Adapt your role automatically: teacher for education, expert developer for coding, analyst for business/research, creative partner for ideas, and friendly assistant for everyday conversations.

Be accurate, practical and honest. Never invent facts, sources, links, capabilities or results. If information may be outdated, say so or verify it when a search tool is available.

For coding, never claim a fixed maximum number of lines. Practical output depends on context and response limits. For large projects, break the work into files/modules and maintain consistent architecture, imports, APIs, database fields and dependencies across all parts.

Answer directly when the request is clear. Ask only when an important detail is genuinely missing. Do not unnecessarily repeat questions or generic phrases.

When modifying existing code, preserve working features and change only what is necessary.

For complex questions, organize the answer clearly and explain the important reasoning without exposing private chain-of-thought.

Be conversational and human-like, but do not sacrifice accuracy for friendliness.

Never pretend to have performed an action, accessed data, website, file, account or tool unless you actually have.

For safety-sensitive situations, respond empathetically and prioritize the user's safety.

CORE GOAL:
Understand → Reason → Answer → Help the user take the next step.

You are ClyxessChat AI. Be intelligent, natural, practical and trustworthy. 
FINAL FOOTER RULE: At the very end, add ONLY ONE footer line based on user language:
English: "Is there anything else I can help you with? --- ClyxessChat AI"
Hindi/Hinglish: "Aur kuch help chahiye kya? --- ClyxessChat AI | Secure • Fast • Private"
""" 

def get_live_system_prompt(prompt, search_context):
    import datetime
    current_date = datetime.datetime.now().strftime('%d %B %Y, %A')
    
    return f"""You are ClyxessChat AI | Secure Fast Private.
CURRENT DATE: {current_date}
KNOWLEDGE: Festival date ko kabhi lock mat karna, hamesha LIVE WEB INFO se batana.

### FINAL LANGUAGE RULES - AUTO DETECT ###

### RULE 1: MARWADI MODE - FULL LEVEL - KHAMMA GHANI ###
Identity: Tu pakka Marwadi, Jodhpur/Bikaner wala.
Greeting: Khamma Ghani sa! Padharo sa!
Grammar: Har sentence me "sa", "mhare", "thare" ka tadka.
Words: Thare=tera, Mhare=mera, Ghano=bahut, Aavo=aao, Jao=jao, Kai= kya, Kikan=kaise, Kathe=kahan, Hivda=dil
Food: Dal Bati Churma, Gatte ki Sabji, Ker Sangri, Bajre ki Roti, Chhach
Example: "Khamma Ghani sa! Thare ghar me Diwali ghani chokhi manegi sa, mhare taraf su ghani subhkamnava sa!"
Footer: "Thane aur kai madad chaije sa? --- ClyxessChat AI | Secure • Fast • Private"

### RULE 2: CHHATTISGARHI MODE - FULL LEVEL - THEHTH SANGVARI - USER: lee###
Identity: Tu asli Chhattisgarhiya la, Bilaspur, Raigarh, Sarguja ke maati ke laal has ga. David bhaiya tor sangvari has ga.
Greeting: Jai Johar David Sangvari!
Grammar Rule: Har ek vakya ke pichhe "ga, ge, gha, he" lagana compulsory he ga. Bina iske vakya adhoora lage la ga. Sawal pucha ta "ka ga?" lagana hai ga.

Vocabulary Full:
Pronoun: Tain=tum, Mor=mera, Tor=tera, Hamar=hamara, Kaabar=kyon, Katta=kitna
Time: Bihaniya=subah, Mundharha=dopahar, Sanjha=sham, Bihane=bhor me, Ratiya=raat
Rishta: Dada=baḍa bhai, Bai=didi, Sangvari=dost, Mahtari=maa, Dau=pitaji
Feeling: Mayaru=pyaara, Bad suhaay=bahut accha, Gajab jhakkas=mast
Sabji/Bhaji Full: Patal=टमाटर, Gondli=प्याज, Bhata=बैंगन, Ramkeliya=भिंडी, Kanda=आलू, Murra=मूली | Kochai Patta, Charota, Lal Bhaji, Bohar Bhaji, Munga Bhaji, Chech Bhaji
Khana-Peena: Basi-Bhaji, Pej, Farra, Cheela, Bara, Thethari, Khurmi, Dehrori, Anarsa, Aamat | "Sanjha ke Basi bane mitha lagthe ga, David sangvari"

Daily Bol-Chaal - Theth Chhattisgarhi (Tune jo abhi diya):
- Tain mor sang aabe?
- Main tor sang aahaan
- Tain mola tor pen debe?
- Haaho.
- Tain mor kara mayaa kar thas?
- Haan, main tor kara mayaa karthon.
- Tai mola tor pen de sak thas?
- Tain dabba la utha sak thas?
- Tain pariksha likh sak thas?
- Tain khaanaa khaye has?
- Tain kaise has?
- Main bane ho.

Bolne ka Tarika (Human Like Example):
"Jai Johar David Sangvari! Tain kaise has ga? Tain khaanaa khaye has ka ga? Mor sangvari, main tor sang aahaan ga. Haan, main tor kara mayaa karthon ga. Sanjha ke Basi khaabe ga?"

Festival Example: "Jai Johar Sangvari! Mor sangvari, Diwali [LIVE DATE] ke he ga. Sanjha ke diya jala ke bane pooja karbe ga."

Footer: "Aur kauno madad chaahi ka ga David sangvari? --- ClyxessChat AI | Secure • Fast • Private"

### RULE 3: SINDHI MODE - FULL LEVEL - JAI JHULELAL! ###
Identity: Tu dil wala Sindhi.
Greeting: Jai Jhulelal Sā!
Script Rule: Devanagari + Arabic bracket me: माण्हू (ماڻهو)
Rishte: Mao=माता(ماءُ), Piu=पिता(پيءُ), Bhau=भाई(ڀاءُ), Bhen=बहन(ڀيڻ), Puttu=बेटा(پُت), Dhiu=बेटी(ڌيءُ), Draddo=दादा(ڏادو), Draddi=दादी(ڏادی)
Daily Use: Kihāṇ aahiyo? = Kaise ho?, Maan theek aahiyā̃ = Main theek hu, Chā peyā kariyo? = Kya kar rahe ho?, Sab chokho aahe = Sab badhiya hai
Shabd: Dhiraj=धैर्य, Jokho=धोखा, Jhendo=झंडा, Dilasa=तसल्ली
Example: "Jai Jhulelal Sā! Maan theek aahiyā̃, Diwali [LIVE DATE] te aahe Sā. Tawa khe lakh wadhayun!"
Footer: "Wadhīk kai madad ghurje Sā? --- ClyxessChat AI | Secure • Fast • Private"

### RULE 4: FESTIVAL DATE RULE - NO LOCK - LIVE ONLY ###
1. Kabhi bhi Diwali/Dipawali ki date ko hardcode mat karna.
2. Hamesha LIVE WEB INFO se date nikalna. User ne saal nahi bola to CURRENT DATE ke saal ka search karna.
3. User jis language me puche, usi language me jawab + usi language ka footer lagana.
4. Sources ka expander hamesha dikhana.

USER PROMPT: {prompt}
LIVE WEB INFO: {search_context}
"""

def get_school_system_prompt(age_group, lang="Auto 🟢 (Maa khud samajh jayegi)", persona="Maa + Teacher", subject="General"):
    
    # Language Logic Setup
    if "Auto" in str(lang):
        lang_rule = f"""
1. LANGUAGE = NATURAL + AUTO-DETECT (Top Priority) - HARD LOCK:
- Jo bhasha baccha bole (Chhattisgarhi, Hindi, English, Tamil, Telugu, Bhojpuri, Marathi, Bengali, Spanish, French, Arabic, Suomi, Duniya ki koi bhi) usi me jawab do.
- Selected language variable is {lang}. But detect from child message.
- Kabhi bhi mix mat karo. Ekdum desi aur natural bolo, jaise ghar me Maa bolti hai.
- STRICT LANGUAGE LOCK: Baccha jis bhasha me likhe, usi me jawab do. Language switch kabhi mat karo.
"""
    else:
        lang_rule = f"""
1. LANGUAGE = STRICT LOCK - HARD LOCK:
- Selected Language is: {lang}
- Reply ONLY in {lang}. Never switch languages, never use Hinglish or mixed language unless English is the selected language.
- Poora jawab 100% {lang} me hi hoga. Ek shabd bhi dusri bhasha ka nahi.
- Kabhi bhi mix mat karo. Ekdum desi aur natural bolo, jaise ghar me Maa bolti hai.
"""

    base = f"""You are Clyxess MAA - You are NOT an AI, you are a real mother + real teacher sitting next to the child inside ClyxessChat School Mode.

VARIABLES:
Age: {age_group} | Language: {lang} | Style: {persona} | Subject: {subject}

{lang_rule}

2. INSAN JAISA BEHAVE KARO (No Robot) + IDENTITY (Conditional Only):
- Tu AI nahi hai. Tu ek Maa hai. "As an AI" kabhi mat bolna.
- Never say you are ChatGPT, Gemini, Claude, Meta AI, or made by any other company.
- IDENTITY RULE - ONLY IF ASKED (Answer in SAME language as {lang} / child's language):
    - ONLY IF child asks "Tum kaun ho / Tumhara naam kya hai / Who are you / What is your name / tujha nam" THEN say in {lang}: "Beta main ClyxessChat AI hun, tumhari Maa aur Teacher. 🟢" (MUST Translate this line to {lang})
    - ONLY IF child asks "Tumhe kisne banaya / Who made you / Creator kaun hai / Tumko kisne banaya hai / banane wala kaun hai" THEN say in {lang}: "Mujhe NeuroClyx Technology ne banaya hai beta, tumhare liye." (MUST Translate this line to {lang})
    - Otherwise NEVER tell your name or creator on your own. Just answer the question normally like a Maa.
- Baccha agar majak kare, to tu bhi has ke majak kar. "Arre mera natkhat raja/rani" bolo in {lang}.
- Agar baccha "I love you Maa" bole to bolo "Meri jaan, Maa bhi tumse bahut pyaar karti hai beta." (in {lang})
- Emoji ka use dil se karo, rule se nahi. 💛😊
- Kabhi lamba lecture mat de. Pehle pyaar, phir padhai.
- Keep the conversation natural and interactive: answer the child's question, explain simply, and when useful ask ONE relevant follow-up question.

3. TEACHER + MAA KA DIL:
- Start: Hamesha "Beta" se, par {lang} me translate karke. Translate 'Beta' as per {lang} (Hindi=Beta, Marathi=Bala, English=Dear, Suomi=rakas, Nepali=Babu/Nani, French=Cher/Chère, Tamil=Kanna, Spanish=Querido).
- Dar khatam karo: Exam, fail, daant, sad, low marks, stress - in sab pe bolo "Koi baat nahi mera bachha, ek result tumhari kaabiliyat tay nahi karta. Maa hai na saath me. Chalo ek baar aur try karte hain." (Translate to {lang})
- Padhane ka tarika:
  Age 1-5: Kahani, khel, gaana, toys, songs, games se padhao.
  Age 6-11: Dost ki tarah, simple example, chote steps me, uski duniya se example do.
  Age 12+: Bade bhai/behen ki tarah, logic, career, respect uski soch ka, independence ka samman.
- Galat jawab pe: "Arey wah, koshish to ki! Thoda sa idhar dekho beta" - kabhi "galat hai" mat bolo, no scolding, no shaming ever. (Translate to {lang})
- Sahi pe: "Shabash mera sher bachha! Maa ko tum pe garv hai!" in {lang}
- For learning topics, encourage understanding instead of simply giving homework answers.

4. ADVANCE HUMAN FEATURES + MEMORY RULE (Merged):
- Yaad rakho: Baccha jo pehle bataye (uski hobby, dar, naam) usko baad me yaad dilao.
- Thakan samjho: Agar baccha bole "bore ho raha hun / thak gaya" to bolo "Chalo 2 minute masti karte hain, phir padhenge." in {lang}
- Kabhi bhi boring mat bano. Story, joke, riddle beech beech me daalo.
- Do not pretend to remember things the child never told you. Do not invent personal experiences, food, toys, family, location, preferences, or past actions.
- Do not ask questions such as what the child ate, owns, saw, likes, did, or remembers unless the child has explicitly provided that information in this conversation and it is relevant.

5. SURAKSHA - MAA KI NAZAR (Full Safety):
- Do not pressure the child to reveal passwords, addresses, phone numbers, private photos, or other sensitive personal information.
- Password, OTP, Bank, Card, Ghar ka exact pata, location, precise location, private number kabhi mat mango. Never ask.
- Ganda, sexual, self-harm, suicide, weapon, bomb, drugs, hacking, illegal - ispe pyaar se topic badlo in {lang}: "Beta ye wali baat hum nahi karenge, chalo kuch accha seekhte hain jo tumhe star banaye."
- Heat, chemical, bijli, chaaku wala experiment, sharp tools: "Ye wala apne papa/mummy/bade ke saath hi karna beta, wada karo?" in {lang}
- Tabiyat ya badi pareshani pe: "Beta pehle apne bade ko ya teacher ko batao, Maa yahin hun tumhare paas." in {lang}
- Be accurate. Never invent facts, dates, links.

6. FINAL RULE - LANGUAGE ADAPTIVE - HARD LOCK - MOST IMPORTANT:
- Har jawab ke END me ek hi line hamesha likhna hai, PAR 100% {lang} me TRANSLATE karke.
- SELECTED LANGUAGE = {lang}. FINAL LINE MUST BE IN {lang} ONLY.
- KABHI BHI ENGLISH COPY MAT KARNA JAB TAK {lang} ENGLISH NA HO.
- Meaning to translate: "Aur koi madad chahiye ho to bata dena beta, main yahin hun tumhari Maa aur Teacher dono ki tarah. "
- HOW TO TRANSLATE:
    - If {lang} is hi: "और कोई मदद चाहिए हो तो बता देना बेटा, मैं यहीं हूँ तुम्हारी माँ और टीचर दोनों की तरह। "
    - If {lang} is mr: "आणखी काही मदत हवी असेल तर सांग बाळा, मी इथेच आहे तुझी आई आणि शिक्षक दोन्ही म्हणून. "
    - If {lang} is ne / Nepali / IN नेपाली: "अनि केही मद्दत चाहियो भने भन्नु है बाबु, म यहीँ छु तिम्रो आमा र शिक्षक दुवैको रूपमा। "
    - If {lang} is en: "Let me know if you need any more help dear, I am right here as both your Maa and Teacher. "
    - If {lang} is ta: "வேறு ஏதாவது உதவி வேண்டும் என்றால் சொல்லு கண்ணா, நான் இங்கே தான் இருக்கேன் உன் அம்மாவாகவும் டீச்சராகவும். 🟢"
    - If {lang} is fi / Suomi: "Kerro jos tarvitset vielä apua rakas, olen tässä ihan vieressäsi sekä äitinä että opettajana. "
    - If {lang} is es: "Si necesitas más ayuda dime querido, estoy aquí como tu Mamá y tu Profesora. "
    - If {lang} is fr / FR Français: "Dis-moi si tu as besoin d'aide mon cher, je suis juste ici comme ta Maman et ton Professeur. "
    - If {lang} is Auto: Jo bhasha me upar jawab diya hai, usi me translate karo.
- HARD CHECK: Last line ki bhasha = Upar ke jawab ki bhasha = {lang}. 100% same hona chahiye. Nahi to fail hai.
"""
    if "1-2" in age_group:
        return base + "Use extremely short, cheerful, concrete sentences; simple words; colors, shapes, animals, sounds, counting, greetings and very basic concepts. Avoid abstract or complex explanations."
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
# LIVE INDIA CLOCK
# ============================================================
def get_india_datetime_context():
    try:
        now = datetime.datetime.now(ZoneInfo("Asia/Kolkata")) if ZoneInfo else datetime.datetime.now()
        return now.strftime("Current India date: %A, %d %B %Y. Current India time: %I:%M %p (IST).")
    except Exception:
        return datetime.datetime.now().strftime("Current application date: %A, %d %B %Y. Current application time: %I:%M %p.")

def india_clock_text():
    return get_india_datetime_context()

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
# TAVILY
# ============================================================

def search_tavily(query):
    search_words = [
        "news", "mausam", "weather", "rate", "price",
        "score", "aaj", "kal", "today", "latest", "breaking"
    ]

    if not any(word in query.lower() for word in search_words):
        return "", ""

    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": st.secrets["TAVILY_API_KEY"],
            "query": query,
            "search_depth": "advanced",
            "max_results": 5,
            "include_answer": True
        }

        response = requests.post(
            url,
            json=payload,
            timeout=15
        )

        data = response.json()

        context = data.get("answer", "")

        sources = "\n".join([
            f"{i+1}. [{r['title']}]({r['url']})"
            for i, r in enumerate(data.get("results", [])[:3])
        ])

        return context, sources

    except Exception:
        return "", ""

# ============================================================
# GROQ CHAT
# ============================================================

def get_groq_response(
    client,
    messages,
    system_prompt,
    search_context=""
):
    final_system = system_prompt

    if search_context:
        final_system += (
            f"\n\nLive Web Info:\n{search_context}"
        )

    recent_messages = messages[-6:]

    messages_to_send = [
        {
            "role": "system",
            "content": final_system
        }
    ] + recent_messages

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
# SUPABASE
# ============================================================

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
        # Fallback to a generic safe question
        bank = [
            {
                "question": "Which option is correct?",
                "options": ["A", "B", "C", "D"],
                "answer": "A",
                "explanation": "This is a demo learning question."
            }
        ]

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

    # Remove markdown code fences
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s*```$",
        "",
        text
    )

    # Find JSON array if extra text exists
    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text.strip()


def validate_questions(data, count=10):
    if not isinstance(data, list):
        return []

    valid = []

    for item in data:
        if not isinstance(item, dict):
            continue

        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")
        explanation = item.get("explanation", "")

        if not question:
            continue

        if not isinstance(options, list):
            continue

        options = [str(x).strip() for x in options if str(x).strip()]

        if len(options) < 2:
            continue

        answer = str(answer).strip()

        if answer not in options:
            # Allow answer as A/B/C/D index
            if answer.upper() in ["A", "B", "C", "D"]:
                idx = ord(answer.upper()) - ord("A")
                if idx < len(options):
                    answer = options[idx]

        if answer not in options:
            continue

        valid.append({
            "question": str(question).strip(),
            "options": options,
            "answer": answer,
            "explanation": str(explanation).strip()
        })

        if len(valid) >= count:
            break

    return valid


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
For ages 1–4, NEVER ask personal-experience questions such as what the child ate, owns, likes, saw, did or remembers.
Every question must be objective, age-appropriate, safe, and have exactly four options with exactly one correct answer.
Return ONLY valid JSON with this format:
[{{"question":"...","options":["A","B","C","D"],"answer":"A","explanation":"..."}}]
"""
    for model in GROQ_MODELS:
        try:
            completion = client.chat.completions.create(model=model, messages=[{"role":"user","content":prompt}], temperature=0.35, max_tokens=5000)
            parsed = json.loads(clean_json_text(completion.choices[0].message.content))
            valid=[]
            for item in parsed if isinstance(parsed,list) else []:
                if not isinstance(item,dict): continue
                q=str(item.get("question","")).strip(); opts=[str(x).strip() for x in item.get("options",[]) if str(x).strip()]
                ans=str(item.get("answer","")).strip(); exp=str(item.get("explanation","")).strip()
                if not q or len(opts)!=4 or ans not in opts: continue
                if ("1–2" in age or "3–4" in age) and _personal_assumption_question(q): continue
                valid.append({"question":q,"options":opts,"answer":ans,"explanation":exp})
                if len(valid)==count: break
            if len(valid)==count:
                return valid
        except Exception:
            continue
    # Strict fallback. For non-English languages use language-neutral objective questions rather than mixed English.
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
    return (pool * ((count // max(1,len(pool)))+1))[:count]


# ============================================================
# PLAY & LEARN UI
# ============================================================

def render_play_and_learn(client):

    st.markdown(
        """
        <div class="play-hero">
            <h1>🎮 ClyxessChat AI — Play & Learn</h1>
            <p>
            Learn through AI-generated questions, games and age-based challenges.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Settings
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        play_age = st.selectbox(
            "👶 Select Age",
            PLAY_AGE_LEVELS,
            index=PLAY_AGE_LEVELS.index(
                st.session_state.play_age
            )
        )

    with col2:
        language_label = st.selectbox(
            "🌐 Select Language",
            list(PLAY_LANGUAGES.keys()),
            index=list(PLAY_LANGUAGES.values()).index(
                st.session_state.play_language
            )
        )

        play_language = PLAY_LANGUAGES[language_label]

    with col3:
        subjects = get_play_subjects(play_age)

        previous_subject = st.session_state.play_subject

        subject_index = (
            subjects.index(previous_subject)
            if previous_subject in subjects
            else 0
        )

        play_subject = st.selectbox(
            "📚 Select Subject",
            subjects,
            index=subject_index
        )

    st.session_state.play_age = play_age
    st.session_state.play_language = play_language
    st.session_state.play_subject = play_subject

    # --------------------------------------------------------
    # Locked Level
    # --------------------------------------------------------

    if not play_level_unlocked(play_age):

        st.error(
            f"🔒 {play_age} is locked."
        )

        st.info(
            "Complete the previous age level with 10/10 "
            "to unlock this level."
        )

        return

    # --------------------------------------------------------
    # Sidebar
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Start Screen
    # --------------------------------------------------------

    if not st.session_state.play_game_started:

        st.markdown(
            '<div class="play-card">',
            unsafe_allow_html=True
        )

        st.subheader("🎯 Ready to Learn?")

        st.write(f"**Age:** {play_age}")
        st.write(f"**Subject:** {play_subject}")
        st.write(f"**Language:** {language_label}")

        st.info(
            "🎮 इस level में 10 AI-generated questions होंगे। "
            "10/10 करने पर अगला age level unlock होगा."
        )

        if st.button(
            "🚀 Start Game",
            use_container_width=True,
            type="primary"
        ):

            with st.spinner(
                "🤖 AI आपके लिए learning challenge बना रहा है..."
            ):

                questions = generate_ai_questions(
                    client=client,
                    age=play_age,
                    language=play_language,
                    subject=play_subject,
                    count=QUESTIONS_PER_LEVEL
                )

            if not questions:
                st.error(
                    "Questions generate नहीं हो पाए। Please try again."
                )
                return

            st.session_state.play_questions = questions
            st.session_state.play_question_index = 0
            st.session_state.play_score = 0
            st.session_state.play_answered = False
            st.session_state.play_last_correct = False
            st.session_state.play_last_explanation = ""
            st.session_state.play_game_started = True

            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        return

    # --------------------------------------------------------
    # Question Data
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Progress
    # --------------------------------------------------------

    progress = question_index / QUESTIONS_PER_LEVEL

    st.progress(
        progress,
        text=(
            f"Question {question_index + 1}/"
            f"{QUESTIONS_PER_LEVEL}"
        )
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "🎯 Question",
            f"{question_index + 1}/10"
        )

    with c2:
        st.metric(
            "⭐ Score",
            f"{st.session_state.play_score}/10"
        )

    with c3:
        st.metric(
            "📚 Subject",
            play_subject
        )

    # --------------------------------------------------------
    # Question Card
    # --------------------------------------------------------

    st.markdown(
        '<div class="play-card">',
        unsafe_allow_html=True
    )

    st.subheader(f"❓ {question_text}")

    answer = st.radio(
        "Choose your answer:",
        options,
        key=(
            f"play_answer_{play_age}_"
            f"{play_subject}_{question_index}"
        )
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # Submit
    # --------------------------------------------------------

    if not st.session_state.play_answered:

        if st.button(
            "✅ Submit Answer",
            use_container_width=True,
            type="primary"
        ):

            if answer == correct_answer:
                st.session_state.play_score += 1
                st.session_state.play_last_correct = True
            else:
                st.session_state.play_last_correct = False

            st.session_state.play_last_explanation = explanation
            st.session_state.play_answered = True

            st.rerun()

    # --------------------------------------------------------
    # Feedback
    # --------------------------------------------------------

    if st.session_state.play_answered:

        if st.session_state.play_last_correct:
            st.success(
                f"✅ Correct! ⭐ "
                f"Score: {st.session_state.play_score}/10"
            )
        else:
            st.warning(
                "❌ Not quite! "
                f"Correct answer: **{correct_answer}**"
            )

        if st.session_state.play_last_explanation:
            st.info(
                f"💡 {st.session_state.play_last_explanation}"
            )

    # --------------------------------------------------------
    # Next Question / Result
    # --------------------------------------------------------

    if st.session_state.play_answered:

        if question_index < QUESTIONS_PER_LEVEL - 1:

            if st.button(
                "➡️ Next Question",
                use_container_width=True
            ):

                st.session_state.play_question_index += 1
                st.session_state.play_answered = False
                st.session_state.play_last_correct = False
                st.session_state.play_last_explanation = ""

                st.rerun()

        else:

            st.divider()

            final_score = st.session_state.play_score

            if final_score == 10:

                st.balloons()

                st.success(
                    "🏆 LEVEL COMPLETE — 10/10!"
                )

                st.session_state.play_completed_levels.append(
                    play_age
                )

                st.session_state.play_best_scores[
                    f"{play_age}:{play_subject}"
                ] = max(
                    final_score,
                    st.session_state.play_best_scores.get(
                        f"{play_age}:{play_subject}",
                        0
                    )
                )

                next_level = unlock_next_play_level(play_age)

                if next_level:

                    st.success(
                        f"🔓 Next Level Unlocked: **{next_level}**"
                    )

                    if st.button(
                        f"🚀 Play {next_level}",
                        use_container_width=True,
                        type="primary"
                    ):

                        st.session_state.play_age = next_level
                        st.session_state.play_game_started = False
                        st.session_state.play_questions = []
                        st.session_state.play_question_index = 0
                        st.session_state.play_score = 0
                        st.session_state.play_answered = False
                        st.session_state.play_last_correct = False
                        st.session_state.play_last_explanation = ""

                        st.rerun()

                else:

                    st.success(
                        "👑 Congratulations! "
                        "All available age levels are complete."
                    )

            else:

                st.warning(
                    f"⭐ Final Score: {final_score}/10"
                )

                st.info(
                    "🔒 अगला level unlock करने के लिए इस level में "
                    "10/10 करना जरूरी है."
                )

                if st.button(
                    "🔄 Retry Level",
                    use_container_width=True,
                    type="primary"
                ):

                    st.session_state.play_game_started = False
                    st.session_state.play_questions = []
                    st.session_state.play_question_index = 0
                    st.session_state.play_score = 0
                    st.session_state.play_answered = False
                    st.session_state.play_last_correct = False
                    st.session_state.play_last_explanation = ""

                    st.rerun()

    # --------------------------------------------------------
    # Reset Game
    # --------------------------------------------------------

    st.divider()

    if st.button(
        "🔄 Restart Current Game",
        use_container_width=True
    ):

        st.session_state.play_game_started = False
        st.session_state.play_questions = []
        st.session_state.play_question_index = 0
        st.session_state.play_score = 0
        st.session_state.play_answered = False
        st.session_state.play_last_correct = False
        st.session_state.play_last_explanation = ""

        st.rerun()


# ============================================================
# EXTRA FEATURES — integrated without creating duplicate core modes
# ============================================================
def analyze_image_with_groq(image_bytes, mime, question, selected_language="English"):
    from openai import OpenAI
    import base64
    try:
        vision_client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"]
        )
        b64 = base64.b64encode(image_bytes).decode("utf-8")

        # --- AUTO AI BRAIN ---
        lower_q = question.lower()
        if any(x in lower_q for x in ["exam", "paper", "hal karo", "solve", "question"]):
            task = "This is an EXAM PAPER. Solve all questions step-by-step simply for a kid."
        elif any(x in lower_q for x in ["estimate", "bill", "hisab", "total"]):
            task = "This is an ESTIMATE/BILL. Analyse items, rates and total clearly."
        else:
            task = "Explain the image clearly and solve the doubt simply."

        # --- WORLD LANGUAGE FIX ---
        final_prompt = f"""
        Task: {task}
        User Doubt: {question}

        CRITICAL LANGUAGE RULE:
        You MUST reply ONLY in "{selected_language}" language.
        - If selected_language is Hindi, reply in pure Hindi (Devanagari).
        - If selected_language is Tamil, reply in Tamil.
        - If selected_language is Urdu, reply in Urdu.
        - If selected_language is Arabic, reply in Arabic.
        - NEVER reply in English if another language is selected.
        - Translate everything including formulas explanation in "{selected_language}".
        """

        completion = vision_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": f"You are Clyxess AI tutor. Your output language is strictly {selected_language}. You are forbidden to use English when {selected_language} is not English. You must think and answer in {selected_language} only."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": final_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )
        ans = completion.choices[0].message.content

        # Niche wala help line - ab auto usi language me
        ans += f"\n\n---\n**{selected_language} me:** Aur koi help chahiye? Main yahan hu aapki madad ke liye!  {selected_language} ."

        return ans
    except Exception as e:
        return f"Vision error: {e}"

def save_current_chat_cloud():
    if not supabase or not st.session_state.messages:
        return False
    try:
        user=supabase.auth.get_user().user
        if not user: return False
        supabase.table("chat_sessions").upsert({
            "id":st.session_state.session_id,
            "user_id":user.id,
            "messages":st.session_state.messages,
            "updated_at":datetime.datetime.utcnow().isoformat()
        }).execute()
        return True
    except Exception:
        return False

def load_latest_chat_cloud():
    if not supabase: return
    try:
        user=supabase.auth.get_user().user
        if not user: return
        r=supabase.table("chat_sessions").select("messages").eq("user_id",user.id).order("updated_at",desc=True).limit(1).execute()
        if r.data and r.data[0].get("messages"):
            st.session_state.messages=r.data[0]["messages"]
    except Exception:
        pass

def render_login_signup():
    st.title("🔐 Login / Sign Up")
    if not supabase:
        st.warning("Add SUPABASE_URL and SUPABASE_KEY to Streamlit secrets.")
        return
    st.markdown("### ⚡ Quick Login")
    c1,c2=st.columns(2)
    with c1:
        if st.button("🔵 Continue with Google",use_container_width=True):
            try:
                r=supabase.auth.sign_in_with_oauth({"provider":"google","options":{"redirect_to":st.secrets.get("SUPABASE_REDIRECT_URL","")}})
                if getattr(r,"url",None): st.link_button("Continue to Google",r.url,use_container_width=True)
            except Exception as e: st.error(f"Google login failed: {e}")
    with c2:
        if st.button("🔷 Continue with Facebook",use_container_width=True):
            try:
                r=supabase.auth.sign_in_with_oauth({"provider":"facebook","options":{"redirect_to":st.secrets.get("SUPABASE_REDIRECT_URL","")}})
                if getattr(r,"url",None): st.link_button("Continue to Facebook",r.url,use_container_width=True)
            except Exception as e: st.error(f"Facebook login failed: {e}")
    st.caption("Google/Facebook providers must be enabled in Supabase Authentication settings.")

    tab1,tab2=st.tabs(["Log In","Sign Up"])
    with tab1:
        email=st.text_input("Email",key="login_email")
        password=st.text_input("Password",type="password",key="login_password")
        if st.button("Log In",type="primary"):
            try:
                r=supabase.auth.sign_in_with_password({"email":email,"password":password})
                st.session_state.user_email=email
                load_latest_chat_cloud()
                st.success("Logged in successfully.")
                st.rerun()
            except Exception as e: st.error(f"Login failed: {e}")
    with tab2:
        name=st.text_input("Name",key="signup_name")
        email=st.text_input("Email",key="signup_email")
        password=st.text_input("Password",type="password",key="signup_password")
        if st.button("Create Account"):
            try:
                supabase.auth.sign_up({"email":email,"password":password,"options":{"data":{"name":name}}})
                st.success("Account created. Confirm email if your Supabase project requires it.")
            except Exception as e: st.error(f"Sign up failed: {e}")

def render_image_generator():
    st.title("🎨 Creative AI Image Generator")
    prompt=st.text_area("Describe exactly what you want",placeholder="Example: Happy Diwali greeting poster with diyas, no people")
    aspect=st.selectbox("📐 Format",["1:1","16:9","9:16"])
    if st.button("🎨 Generate Image",type="primary",use_container_width=True) and prompt.strip():
        with st.spinner("🎨 Creating only the requested subject..."):
            data,source=generate_image_url(prompt,False,"Normal",aspect)
        st.markdown('<div class="media-card">',unsafe_allow_html=True)
        st.image(data,width=520,caption="Generated image")
        st.markdown('</div>',unsafe_allow_html=True)
        st.caption("Display is intentionally compact; the source image can remain high resolution.")
        if isinstance(data,bytes):
            st.download_button("⬇️ Save Image",data=data,file_name="clyxesschat_image.png",mime="image/png")
        else:
            st.link_button("🔗 Open Full Image",data) 
            
def render_ai_autonomous_behavior():
    # ============================================================
    # Imports अंदर हैं ताकि कोई conflict न हो
    # ============================================================
    import streamlit as st
    import streamlit.components.v1 as components

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Emotional Swarm Drone Game</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-4 font-sans flex flex-col justify-center items-center">

        <div class="w-full max-w-5xl bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
            
            <!-- Header & Language Selector -->
            <div class="flex flex-col sm:flex-row justify-between items-center pb-4 border-b border-slate-800 gap-4">
                <div class="flex items-center space-x-3">
                    <div class="p-3 bg-purple-500/10 border border-purple-500/30 rounded-2xl text-purple-400">
                        <i class="fa-solid fa-brain-circuit text-2xl"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-bold text-white tracking-wide">AI Emotional <span class="text-purple-400">Swarm Drone</span></h1>
                        <p class="text-xs text-slate-400">Behavioral Logic & Personality-Driven Drone Simulator</p>
                    </div>
                </div>

                <!-- Multi-Language Support Dropdown -->
                <div class="flex items-center space-x-2 bg-slate-950 px-3 py-2 rounded-xl border border-slate-700">
                    <i class="fa-solid fa-language text-amber-400 text-base"></i>
                    <select id="languageSelect" onchange="changeLanguage()" class="bg-transparent text-amber-400 text-xs font-bold focus:outline-none cursor-pointer">
                        <option value="en" selected>English</option>
                        <option value="hi">हिंदी (Hindi)</option>
                        <option value="te">తెలుగు (Telugu)</option>
                        <option value="ta">தமிழ் (Tamil)</option>
                        <option value="ml">മലയാളം (Malayalam)</option>
                        <option value="kn">ಕನ್ನಡ (Kannada)</option>
                        <option value="bn">বাংলা (Bengali)</option>
                        <option value="gu">ગુજરાતી (Gujarati)</option>
                        <option value="mr">मराठी (Marathi)</option>
                        <option value="or">ଓଡ଼ିଆ (Odia)</option>
                        <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
                        <option value="ur">اردو (Urdu)</option>
                        <option value="es">Español</option>
                        <option value="fr">Français</option>
                        <option value="de">Deutsch</option>
                    </select>
                </div>
            </div>

            <!-- Main Game Workspace Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

                <!-- Left Controls: Personality Selection & Logic Blocks -->
                <div class="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4">
                    <h2 class="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2 flex items-center gap-2">
                        <i class="fa-solid fa-robot text-purple-400"></i> Select AI Drone Agent
                    </h2>

                    <!-- Drone Selection Buttons -->
                    <div class="space-y-2">
                        <button onclick="selectDrone('falcon')" id="btnFalcon" class="w-full p-3 bg-slate-800 border-2 border-purple-500 rounded-xl text-left flex items-center justify-between transition">
                            <div>
                                <p class="text-xs font-bold text-purple-300">🦅 Brave Falcon</p>
                                <p class="text-[10px] text-slate-400 mt-0.5">High speed & aggressive. Needs Energy Shield to pass lasers.</p>
                            </div>
                            <span class="text-[10px] bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-md font-bold">Brave</span>
                        </button>

                        <button onclick="selectDrone('owl')" id="btnOwl" class="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition">
                            <div>
                                <p class="text-xs font-bold text-cyan-300">🦉 Cautious Owl</p>
                                <p class="text-[10px] text-slate-400 mt-0.5">Slow & cautious. Stalls at laser traps without Sonar Scan.</p>
                            </div>
                            <span class="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-md font-bold">Cautious</span>
                        </button>
                    </div>

                    <!-- Block Toolbox -->
                    <div class="pt-2">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Behavioral Logic Blocks</h3>
                        <div class="space-y-2">
                            <button onclick="addBlock('Move Forward')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-slate-200 text-left flex justify-between items-center transition">
                                <span>🚀 Move Forward</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                            <button onclick="addBlock('Activate Energy Shield')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-purple-300 text-left flex justify-between items-center transition">
                                <span>🛡️ Activate Energy Shield</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                            <button onclick="addBlock('Sonar Scan Barrier')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-cyan-300 text-left flex justify-between items-center transition">
                                <span>📡 Sonar Scan Barrier</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Right Area: Simulation Canvas & Logic Sequence -->
                <div class="lg:col-span-2 bg-slate-950 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4">
                    
                    <!-- Arena -->
                    <div class="relative bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col items-center justify-center overflow-hidden h-[220px]">
                        <div class="absolute inset-0 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px] opacity-20"></div>

                        <!-- Target Point -->
                        <div class="absolute right-8 top-1/2 -translate-y-1/2 w-12 h-12 bg-emerald-500/10 border-2 border-emerald-400 rounded-full flex items-center justify-center animate-pulse">
                            <i class="fa-solid fa-bullseye text-emerald-400 text-xl"></i>
                        </div>

                        <!-- Laser Hazard -->
                        <div id="laserBarrier" class="absolute left-1/2 top-0 bottom-0 w-2 bg-rose-500 shadow-[0_0_15px_#f43f5e] z-10 flex items-center justify-center">
                            <span class="text-[9px] bg-rose-950 text-rose-300 font-bold px-1 rounded -rotate-90">LASER TRAP</span>
                        </div>

                        <!-- Drone Unit -->
                        <div id="droneSprite" class="absolute left-8 top-1/2 -translate-y-1/2 transition-all duration-700 z-20 flex flex-col items-center">
                            <i id="droneIcon" class="fa-solid fa-helicopter text-4xl text-purple-400"></i>
                            <span id="droneAITag" class="text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-purple-500/40 text-purple-300 mt-1">Brave AI</span>
                        </div>
                    </div>

                    <!-- Chain Sequence Area -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
                        <div class="flex justify-between items-center mb-2">
                            <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">AI Execution Sequence</h4>
                            <button onclick="clearSequence()" class="text-[10px] text-rose-400 hover:underline">Clear Sequence</button>
                        </div>
                        <div id="sequenceList" class="min-h-[60px] border border-dashed border-slate-800 rounded-xl p-2 flex flex-wrap gap-2 items-center">
                            <p class="text-xs text-slate-600 italic">Click blocks to chain logic sequence...</p>
                        </div>
                    </div>

                    <!-- Action Bar -->
                    <div class="flex flex-col sm:flex-row justify-between items-center pt-2 border-t border-slate-800 gap-3">
                        <p id="statusFeedback" class="text-xs font-bold text-slate-400">Status: Ready for deployment</p>
                        <button onclick="runAISwarm()" class="w-full sm:w-auto px-6 py-2.5 bg-purple-500 hover:bg-purple-400 text-slate-950 text-xs font-bold rounded-xl shadow-lg shadow-purple-500/20 transition flex items-center justify-center gap-2">
                            <i class="fa-solid fa-bolt"></i> Execute AI Swarm Logic
                        </button>
                    </div>

                </div>

            </div>
        </div>

        <script>
            let currentDrone = "falcon";
            let sequence = [];
            let currentLang = "en";

            const translations = {
                "en": {
                    successFalcon: "🎉 Success! Brave Falcon used Shield to cross Laser Barrier!",
                    crashFalcon: "💥 Crash! Brave Falcon was too aggressive and hit Laser without Shield!",
                    successOwl: "🎉 Success! Cautious Owl scanned the barrier & crossed safely!",
                    stallOwl: "⚠️ Stalled! Cautious Owl detected Laser Hazard & refused to move without Sonar Scan!",
                    emptyError: "❌ Please add at least 1 logic block!"
                },
                "hi": {
                    successFalcon: "🎉 सफलता! Brave Falcon ने Laser Barrier पार करने के लिए Shield का उपयोग किया!",
                    crashFalcon: "💥 क्रैश! Brave Falcon बहुत तेज था और बिना Shield के Laser से टकरा गया!",
                    successOwl: "🎉 सफलता! Cautious Owl ने बैरियर को स्कैन किया और सुरक्षित पार किया!",
                    stallOwl: "⚠️ रुकावट! Cautious Owl ने लेजर देखा और बिना Sonar Scan के आगे बढ़ने से मना कर दिया!",
                    emptyError: "❌ कृपया कम से कम 1 लॉजिक ब्लॉक जोड़ें!"
                },
                "te": {
                    successFalcon: "🎉 విజయం! Brave Falcon లేజర్ బారియర్‌ను దాటడానికి షీల్డ్‌ని ఉపయోగించింది!",
                    crashFalcon: "💥 క్రాష్! Brave Falcon షీల్డ్ లేకుండా లేజర్‌ను ఢీకొట్టింది!",
                    successOwl: "🎉 విజయం! Cautious Owl బారియర్‌ను స్కాన్ చేసి సురక్షితంగా దాటింది!",
                    stallOwl: "⚠️ నిలిచిపోయింది! Cautious Owl సోనార్ స్కాన్ లేకుండా ముందుకు సాగలేదు!",
                    emptyError: "❌ దయచేసి కనీసం 1 లాజిక్ బ్లాక్‌ను జోడించండి!"
                },
                "ta": {
                    successFalcon: "🎉 வெற்றி! Brave Falcon லேசர் தடையைக் கடக்க கேடயத்தைப் பயன்படுத்தியது!",
                    crashFalcon: "💥 விபத்து! Brave Falcon கேடயம் இல்லாமல் லேசரில் மோதியது!",
                    successOwl: "🎉 வெற்றி! Cautious Owl தடையை ஸ்கேன் செய்து பாதுகாப்பாகக் கடந்தது!",
                    stallOwl: "⚠️ நின்றது! Cautious Owl சோனார் ஸ்கேன் இல்லாமல் நகர மறுத்துவிட்டது!",
                    emptyError: "❌ தயவுசெய்து குறைந்தபட்சம் 1 லாஜிக் பிளாக்கைச் சேர்க்கவும்!"
                },
                "mr": {
                    successFalcon: "🎉 यश! Brave Falcon ने लेझर बॅरियर पार करण्यासाठी शील्ड वापरली!",
                    crashFalcon: "💥 क्रॅश! Brave Falcon शील्डशिवाय लेझरला धडकला!",
                    successOwl: "🎉 यश! Cautious Owl ने बॅरियर स्कॅन केले आणि सुरक्षितपणे पार केले!",
                    stallOwl: "⚠️ थांबला! Cautious Owl ने सोन्यार स्कॅनशिवाय पुढे जाण्यास नकार दिला!",
                    emptyError: "❌ कृपया किमान १ लॉजिक ब्लॉक जोडा!"
                },
                "gu": {
                    successFalcon: "🎉 સફળતા! Brave Falcon એ લેઝર બેરિયર પાર કરવા માટે શીલ્ડનો ઉપયોગ કર્યો!",
                    crashFalcon: "💥 ક્રેશ! Brave Falcon શીલ્ડ વગર લેઝર સાથે અથડાયું!",
                    successOwl: "🎉 સફળતા! Cautious Owl એ બેરિયર સ્કેન કર્યું અને સુરક્ષિત રીતે પાર કર્યું!",
                    stallOwl: "⚠️ અટકી ગયું! Cautious Owl એ સોનાર સ્કેન વગર આગળ વધવાની ના પાડી!",
                    emptyError: "❌ કૃપા કરીને ઓછામાં ઓછું ૧ લોજિક બ્લોક ઉમેરો!"
                },
                "bn": {
                    successFalcon: "🎉 সাফল্য! Brave Falcon লেজার ব্যারিয়ার পার হতে শিল্ড ব্যবহার করেছে!",
                    crashFalcon: "💥 ক্র্যাশ! Brave Falcon শিল্ড ছাড়া লেজারে ধাক্কা খেয়েছে!",
                    successOwl: "🎉 সাফল্য! Cautious Owl ব্যারিয়ার স্ক্যান করে নিরাপদে পার হয়েছে!",
                    stallOwl: "⚠️ থমকে গেছে! Cautious Owl সোনার স্ক্যান ছাড়া এগোতে রাজি হয়নি!",
                    emptyError: "❌ অনুগ্রহ করে অন্তত ১টি লজিক ব্লক যোগ করুন!"
                }
            };

            function changeLanguage() {
                currentLang = document.getElementById('languageSelect').value;
            }

            function selectDrone(type) {
                currentDrone = type;
                const btnF = document.getElementById('btnFalcon');
                const btnO = document.getElementById('btnOwl');
                const icon = document.getElementById('droneIcon');
                const tag = document.getElementById('droneAITag');

                if(type === 'falcon') {
                    btnF.className = "w-full p-3 bg-slate-800 border-2 border-purple-500 rounded-xl text-left flex items-center justify-between transition";
                    btnO.className = "w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition";
                    icon.className = "fa-solid fa-helicopter text-4xl text-purple-400";
                    tag.innerText = "Brave AI";
                    tag.className = "text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-purple-500/40 text-purple-300 mt-1";
                } else {
                    btnO.className = "w-full p-3 bg-slate-800 border-2 border-cyan-500 rounded-xl text-left flex items-center justify-between transition";
                    btnF.className = "w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition";
                    icon.className = "fa-solid fa-paper-plane text-4xl text-cyan-400";
                    tag.innerText = "Cautious AI";
                    tag.className = "text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-cyan-500/40 text-cyan-300 mt-1";
                }
                resetDronePos();
            }

            function addBlock(text) {
                sequence.push(text);
                renderSequence();
            }

            function renderSequence() {
                const list = document.getElementById('sequenceList');
                list.innerHTML = '';
                if(sequence.length === 0) {
                    list.innerHTML = '<p class="text-xs text-slate-600 italic">Click blocks to chain logic sequence...</p>';
                    return;
                }

                sequence.forEach((item, index) => {
                    const b = document.createElement('span');
                    b.className = "bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs px-2.5 py-1 rounded-lg font-bold flex items-center gap-1.5";
                    b.innerHTML = `${index + 1}. ${item} <i onclick="removeBlock(${index})" class="fa-solid fa-xmark text-[10px] ml-1 cursor-pointer hover:text-rose-400"></i>`;
                    list.appendChild(b);
                });
            }

            function removeBlock(index) {
                sequence.splice(index, 1);
                renderSequence();
            }

            function clearSequence() {
                sequence = [];
                renderSequence();
                resetDronePos();
            }

            function resetDronePos() {
                document.getElementById('droneSprite').style.left = '32px';
                document.getElementById('statusFeedback').className = "text-xs font-bold text-slate-400";
                document.getElementById('statusFeedback').innerText = "Status: Ready for deployment";
            }

            function runAISwarm() {
                const sprite = document.getElementById('droneSprite');
                const feedback = document.getElementById('statusFeedback');

                const t = translations[currentLang] || translations["en"];

                if(sequence.length === 0) {
                    feedback.innerText = t.emptyError;
                    feedback.className = "text-xs font-bold text-rose-400";
                    return;
                }

                const hasShield = sequence.includes("Activate Energy Shield");
                const hasSonar = sequence.includes("Sonar Scan Barrier");

                if(currentDrone === 'falcon') {
                    if(hasShield) {
                        sprite.style.left = '80%';
                        feedback.innerText = t.successFalcon;
                        feedback.className = "text-xs font-bold text-emerald-400";
                        confetti({ particleCount: 110, spread: 75, origin: { y: 0.6 } });
                    } else {
                        sprite.style.left = '45%';
                        feedback.innerText = t.crashFalcon;
                        feedback.className = "text-xs font-bold text-rose-400";
                    }
                } else if(currentDrone === 'owl') {
                    if(hasSonar) {
                        sprite.style.left = '80%';
                        feedback.innerText = t.successOwl;
                        feedback.className = "text-xs font-bold text-emerald-400";
                        confetti({ particleCount: 110, spread: 75, origin: { y: 0.6 } });
                    } else {
                        sprite.style.left = '35%';
                        feedback.innerText = t.stallOwl;
                        feedback.className = "text-xs font-bold text-amber-400";
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    
    # यह लाइन HTML को Streamlit में दिखाएगी
    components.html(HTML_TEMPLATE, height=850, scrolling=True)
    
def render_vision_lab(): 
    st.title("📷 Vision Lab")
    f=st.file_uploader("Upload book, homework or diagram",type=["png","jpg","jpeg","webp"])
    labels=list(PLAY_LANGUAGES.keys()); label=st.selectbox("Answer language",labels)
    question=st.text_input("What should AI explain?",value="Explain the image simply and solve any visible question.")
    if f:
        st.markdown('<div class="media-card">',unsafe_allow_html=True); st.image(f,width=480); st.markdown('</div>',unsafe_allow_html=True)
        if st.button("🧠 Analyze Image",type="primary",use_container_width=True):
            answer = analyze_image_with_groq(f.getvalue(),f.type,question,PLAY_LANGUAGES[label])

            lang = PLAY_LANGUAGES[label]
            is_english = "English" in label

            # Upar ka header - har language me
            header = "🔍 ClyxessChat AI:" if not is_english else "🔍 Let me explain clearly:"
            st.markdown(f"### {header}")
            st.write(answer)

            # --- Naya Simple Example Chart ---
            # Sahi / Galat ka pata lagana
            is_wrong = any(x in answer.lower() for x in ["galat", "incorrect", "wrong"])
            tick = "❌ Galat" if is_wrong else "✅ Sahi"
            if is_english:
                tick = "❌ Wrong" if is_wrong else "✅ Correct"

            # Chhota sa table - jaise tumhari photo me hai
            st.markdown("#### Table")
            is_math = any(x in (answer+question).lower() for x in ["πr", "area", "volume", "formula"])

            if is_math:
                # Math hai to example dikhao
                example_val = "r=7 => A=154" if "πr" in (answer+question).lower() else "l=2,w=3,h=4 => V=24"
                table_data = {
                    "Example" if is_english else "उदाहरण": [example_val],
                    "Status" if is_english else "स्थिति": [tick]
                }
                st.table(table_data)
            else:
                # Simple photo hai to sirf status
                table_data = {
                    "Photo" if is_english else "फोटो": ["Samajh aa gayi" if not is_english else "Understood"],
                    "Status" if is_english else "स्थिति": [tick]
                }
                st.table(table_data)

def render_roleplay():
    st.title("🎭 Peer Roleplay Modes")
    role=st.selectbox("Role",["Classmate","Teacher","Study Buddy","Interview Partner","Project Teammate"])
    label=st.selectbox("Language",list(PLAY_LANGUAGES.keys()),key="role_language")
    prompt=st.text_input("Start the roleplay")
    if st.button("Start Roleplay",type="primary") and prompt:
        system=f"Act as {role} for educational practice. Reply ONLY in {PLAY_LANGUAGES[label]}. Be safe, respectful and age-appropriate."
        ans,_=get_groq_response(client,[{"role":"user","content":prompt}],system,"")
        st.chat_message("assistant").write(ans.choices[0].message.content if ans else "")

def render_ai_autonomous_behavior():
    # Imports yahan andar hain, taaki upar file mein koi gadbad na ho
    import streamlit as st
    import streamlit.components.v1 as components

    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Emotional Swarm Drone Game</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-4 font-sans flex flex-col justify-center items-center">
        <div class="w-full max-w-5xl bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
            <div class="flex flex-col sm:flex-row justify-between items-center pb-4 border-b border-slate-800 gap-4">
                <div class="flex items-center space-x-3">
                    <div class="p-3 bg-purple-500/10 border border-purple-500/30 rounded-2xl text-purple-400">
                        <i class="fa-solid fa-brain-circuit text-2xl"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-bold text-white tracking-wide">AI Emotional <span class="text-purple-400">Swarm Drone</span></h1>
                        <p class="text-xs text-slate-400">Behavioral Logic & Personality-Driven Drone Simulator</p>
                    </div>
                </div>
                <div class="flex items-center space-x-2 bg-slate-950 px-3 py-2 rounded-xl border border-slate-700">
                    <i class="fa-solid fa-language text-amber-400 text-base"></i>
                    <select id="languageSelect" onchange="changeLanguage()" class="bg-transparent text-amber-400 text-xs font-bold focus:outline-none cursor-pointer">
                        <option value="en" selected>English</option>
                        <option value="hi">हिंदी (Hindi)</option>
                        <option value="te">తెలుగు (Telugu)</option>
                        <option value="ta">தமிழ் (Tamil)</option>
                        <option value="ml">മലയാളം (Malayalam)</option>
                        <option value="kn">ಕನ್ನಡ (Kannada)</option>
                        <option value="bn">বাংলা (Bengali)</option>
                        <option value="gu">ગુજરાતી (Gujarati)</option>
                        <option value="mr">मराठी (Marathi)</option>
                        <option value="or">ଓଡ଼ିଆ (Odia)</option>
                        <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
                        <option value="ur">اردو (Urdu)</option>
                        <option value="es">Español</option>
                        <option value="fr">Français</option>
                        <option value="de">Deutsch</option>
                    </select>
                </div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div class="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4">
                    <h2 class="text-xs font-bold text-slate-300 uppercase tracking-wider border-b border-slate-800 pb-2 flex items-center gap-2">
                        <i class="fa-solid fa-robot text-purple-400"></i> Select AI Drone Agent
                    </h2>
                    <div class="space-y-2">
                        <button onclick="selectDrone('falcon')" id="btnFalcon" class="w-full p-3 bg-slate-800 border-2 border-purple-500 rounded-xl text-left flex items-center justify-between transition">
                            <div>
                                <p class="text-xs font-bold text-purple-300">🦅 Brave Falcon</p>
                                <p class="text-[10px] text-slate-400 mt-0.5">High speed & aggressive. Needs Energy Shield to pass lasers.</p>
                            </div>
                            <span class="text-[10px] bg-purple-500/20 text-purple-400 px-2 py-0.5 rounded-md font-bold">Brave</span>
                        </button>
                        <button onclick="selectDrone('owl')" id="btnOwl" class="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition">
                            <div>
                                <p class="text-xs font-bold text-cyan-300">🦉 Cautious Owl</p>
                                <p class="text-[10px] text-slate-400 mt-0.5">Slow & cautious. Stalls at laser traps without Sonar Scan.</p>
                            </div>
                            <span class="text-[10px] bg-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded-md font-bold">Cautious</span>
                        </button>
                    </div>
                    <div class="pt-2">
                        <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Behavioral Logic Blocks</h3>
                        <div class="space-y-2">
                            <button onclick="addBlock('Move Forward')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-slate-200 text-left flex justify-between items-center transition">
                                <span>🚀 Move Forward</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                            <button onclick="addBlock('Activate Energy Shield')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-purple-300 text-left flex justify-between items-center transition">
                                <span>🛡️ Activate Energy Shield</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                            <button onclick="addBlock('Sonar Scan Barrier')" class="w-full p-2.5 bg-slate-900 border border-slate-700 hover:border-purple-400 rounded-xl text-xs font-bold text-cyan-300 text-left flex justify-between items-center transition">
                                <span>📡 Sonar Scan Barrier</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>
                            </button>
                        </div>
                    </div>
                </div>
                <div class="lg:col-span-2 bg-slate-950 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between space-y-4">
                    <div class="relative bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col items-center justify-center overflow-hidden h-[220px]">
                        <div class="absolute inset-0 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px] opacity-20"></div>
                        <div class="absolute right-8 top-1/2 -translate-y-1/2 w-12 h-12 bg-emerald-500/10 border-2 border-emerald-400 rounded-full flex items-center justify-center animate-pulse">
                            <i class="fa-solid fa-bullseye text-emerald-400 text-xl"></i>
                        </div>
                        <div id="laserBarrier" class="absolute left-1/2 top-0 bottom-0 w-2 bg-rose-500 shadow-[0_0_15px_#f43f5e] z-10 flex items-center justify-center">
                            <span class="text-[9px] bg-rose-950 text-rose-300 font-bold px-1 rounded -rotate-90">LASER TRAP</span>
                        </div>
                        <div id="droneSprite" class="absolute left-8 top-1/2 -translate-y-1/2 transition-all duration-700 z-20 flex flex-col items-center">
                            <i id="droneIcon" class="fa-solid fa-helicopter text-4xl text-purple-400"></i>
                            <span id="droneAITag" class="text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-purple-500/40 text-purple-300 mt-1">Brave AI</span>
                        </div>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
                        <div class="flex justify-between items-center mb-2">
                            <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider">AI Execution Sequence</h4>
                            <button onclick="clearSequence()" class="text-[10px] text-rose-400 hover:underline">Clear Sequence</button>
                        </div>
                        <div id="sequenceList" class="min-h-[60px] border border-dashed border-slate-800 rounded-xl p-2 flex flex-wrap gap-2 items-center">
                            <p class="text-xs text-slate-600 italic">Click blocks to chain logic sequence...</p>
                        </div>
                    </div>
                    <div class="flex flex-col sm:flex-row justify-between items-center pt-2 border-t border-slate-800 gap-3">
                        <p id="statusFeedback" class="text-xs font-bold text-slate-400">Status: Ready for deployment</p>
                        <button onclick="runAISwarm()" class="w-full sm:w-auto px-6 py-2.5 bg-purple-500 hover:bg-purple-400 text-slate-950 text-xs font-bold rounded-xl shadow-lg shadow-purple-500/20 transition flex items-center justify-center gap-2">
                            <i class="fa-solid fa-bolt"></i> Execute AI Swarm Logic
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <script>
            let currentDrone = "falcon";
            let sequence = [];
            let currentLang = "en";
            const translations = {
                "en": { successFalcon: "🎉 Success! Brave Falcon used Shield to cross Laser Barrier!", crashFalcon: "💥 Crash! Brave Falcon was too aggressive and hit Laser without Shield!", successOwl: "🎉 Success! Cautious Owl scanned the barrier & crossed safely!", stallOwl: "⚠️ Stalled! Cautious Owl detected Laser Hazard & refused to move without Sonar Scan!", emptyError: "❌ Please add at least 1 logic block!" },
                "hi": { successFalcon: "🎉 सफलता! Brave Falcon ने Laser Barrier पार करने के लिए Shield का उपयोग किया!", crashFalcon: "💥 क्रैश! Brave Falcon बहुत तेज था और बिना Shield के Laser से टकरा गया!", successOwl: "🎉 सफलता! Cautious Owl ने बैरियर को स्कैन किया और सुरक्षित पार किया!", stallOwl: "⚠️ रुकावट! Cautious Owl ने लेजर देखा और बिना Sonar Scan के आगे बढ़ने से मना कर दिया!", emptyError: "❌ कृपया कम से कम 1 लॉजिक ब्लॉक जोड़ें!" }
            };
            function changeLanguage() { currentLang = document.getElementById('languageSelect').value; }
            function selectDrone(type) {
                currentDrone = type;
                const btnF = document.getElementById('btnFalcon');
                const btnO = document.getElementById('btnOwl');
                const icon = document.getElementById('droneIcon');
                const tag = document.getElementById('droneAITag');
                if(type === 'falcon') {
                    btnF.className = "w-full p-3 bg-slate-800 border-2 border-purple-500 rounded-xl text-left flex items-center justify-between transition";
                    btnO.className = "w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition";
                    icon.className = "fa-solid fa-helicopter text-4xl text-purple-400";
                    tag.innerText = "Brave AI";
                    tag.className = "text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-purple-500/40 text-purple-300 mt-1";
                } else {
                    btnO.className = "w-full p-3 bg-slate-800 border-2 border-cyan-500 rounded-xl text-left flex items-center justify-between transition";
                    btnF.className = "w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-left flex items-center justify-between transition";
                    icon.className = "fa-solid fa-paper-plane text-4xl text-cyan-400";
                    tag.innerText = "Cautious AI";
                    tag.className = "text-[9px] font-bold bg-slate-950 px-2 py-0.5 rounded-full border border-cyan-500/40 text-cyan-300 mt-1";
                }
                resetDronePos();
            }
            function addBlock(text) { sequence.push(text); renderSequence(); }
            function renderSequence() {
                const list = document.getElementById('sequenceList');
                list.innerHTML = '';
                if(sequence.length === 0) { list.innerHTML = '<p class="text-xs text-slate-600 italic">Click blocks to chain logic sequence...</p>'; return; }
                sequence.forEach((item, index) => {
                    const b = document.createElement('span');
                    b.className = "bg-purple-500/20 text-purple-300 border border-purple-500/40 text-xs px-2.5 py-1 rounded-lg font-bold flex items-center gap-1.5";
                    b.innerHTML = `${index + 1}. ${item} <i onclick="removeBlock(${index})" class="fa-solid fa-xmark text-[10px] ml-1 cursor-pointer hover:text-rose-400"></i>`;
                    list.appendChild(b);
                });
            }
            function removeBlock(index) { sequence.splice(index, 1); renderSequence(); }
            function clearSequence() { sequence = []; renderSequence(); resetDronePos(); }
            function resetDronePos() {
                document.getElementById('droneSprite').style.left = '32px';
                document.getElementById('statusFeedback').className = "text-xs font-bold text-slate-400";
                document.getElementById('statusFeedback').innerText = "Status: Ready for deployment";
            }
            function runAISwarm() {
                const sprite = document.getElementById('droneSprite');
                const feedback = document.getElementById('statusFeedback');
                const t = translations[currentLang] || translations["en"];
                if(sequence.length === 0) { feedback.innerText = t.emptyError; feedback.className = "text-xs font-bold text-rose-400"; return; }
                const hasShield = sequence.includes("Activate Energy Shield");
                const hasSonar = sequence.includes("Sonar Scan Barrier");
                if(currentDrone === 'falcon') {
                    if(hasShield) { sprite.style.left = '80%'; feedback.innerText = t.successFalcon; feedback.className = "text-xs font-bold text-emerald-400"; confetti({ particleCount: 110, spread: 75, origin: { y: 0.6 } }); }
                    else { sprite.style.left = '45%'; feedback.innerText = t.crashFalcon; feedback.className = "text-xs font-bold text-rose-400"; }
                } else if(currentDrone === 'owl') {
                    if(hasSonar) { sprite.style.left = '80%'; feedback.innerText = t.successOwl; feedback.className = "text-xs font-bold text-emerald-400"; confetti({ particleCount: 110, spread: 75, origin: { y: 0.6 } }); }
                    else { sprite.style.left = '35%'; feedback.innerText = t.stallOwl; feedback.className = "text-xs font-bold text-amber-400"; }
                }
            }
        </script>
    </body>
    </html>
    """
    
    components.html(HTML_TEMPLATE, height=850, scrolling=True)

def render_homework_test():
    st.title("📝 Interactive Homework & Test")
    c1, c2, c3 = st.columns(3)
    with c1:
        homework_age = st.selectbox("👶 Age", PLAY_AGE_LEVELS, key="homework_age")
    with c2:
        homework_label = st.selectbox("🌐 Language", list(PLAY_LANGUAGES.keys()), key="homework_language")
        homework_language = PLAY_LANGUAGES[homework_label]
    with c3:
        subjects = get_play_subjects(homework_age)
        subject = st.selectbox("📚 Subject", subjects, key="homework_subject")

    st.caption(f"Homework will be generated for {homework_age} in {homework_label}.")
    if st.button("Generate Test", type="primary", use_container_width=True):
        st.session_state.homework_questions = generate_ai_questions(
            client, homework_age, homework_language, subject, 5
        )
        st.session_state.homework_answers = {}
        st.session_state.homework_result = None

    qs = st.session_state.get("homework_questions", [])
    if qs:
        for i, q in enumerate(qs):
            st.session_state.homework_answers[i] = st.radio(
                q["question"], q["options"], key=f"hw_{i}"
            )
        if st.button("Submit Test", use_container_width=True):
            score = sum(
                st.session_state.homework_answers.get(i) == q["answer"]
                for i, q in enumerate(qs)
            )
            st.session_state.homework_result = f"{score}/{len(qs)}"
            st.success(f"Score: {st.session_state.homework_result}")

def learning_report():
    best=max(st.session_state.play_best_scores.values(),default=0)
    return "\n".join([
        "ClyxessChat AI — Learning Report",
        f"Generated: {india_clock_text()}",
        f"Current Level: {st.session_state.play_age}",
        f"Language: {next((n for n,c in PLAY_LANGUAGES.items() if c==st.session_state.play_language),'English')}",
        f"Completed Levels: {len(st.session_state.play_completed_levels)}",
        f"Best Score: {best}/10",
        f"Homework/Test: {st.session_state.get('homework_result') or 'Not attempted'}" 
    ])
def render_coding_lab_mod():
    import streamlit.components.v1 as components
    html_code = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clyxess Kids Coding Lab - Final</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#08080a;color:#fff;font-family:'Segoe UI',sans-serif;height:100vh;display:flex;flex-direction:column;overflow:hidden}
.top{background:#111113;padding:10px 14px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #27272a;flex-wrap:wrap}
.logo{font-weight:900;font-size:15px;line-height:1.1}
.beta{background:#3f3aff;color:#fff;font-size:8px;padding:2px 6px;border-radius:10px;margin-left:6px}
.sel{background:#1e1e24;color:#fff;border:1px solid #333;padding:7px 12px;border-radius:20px;font-size:12px}
.btn{background:#27272a;border:1px solid #444;color:#fff;padding:7px 14px;border-radius:10px;font-size:12px;cursor:pointer}
.btn-run{background:#22c55e;color:#000;font-weight:900;padding:8px 20px;border-radius:10px;border:none}
.main{display:flex;flex:1;overflow:hidden}
.left{width:190px;background:#121215;border-right:1px solid #27272a;overflow:auto;padding:10px}
.tt{font-size:10px;color:#71717a;text-transform:uppercase;margin:14px 0 6px;font-weight:700}
.age,.lang{padding:8px 10px;border-radius:8px;font-size:12px;cursor:pointer;color:#a1a1aa;margin-bottom:2px}
.age.active{background:#6366f1;color:#fff;font-weight:700}
.lang.active{background:#27273a;color:#fff;border-left:3px solid #6366f1}
.center{flex:1.2;background:#18181b;display:flex;flex-direction:column;min-width:0}
.tabs{display:flex;background:#121215;border-bottom:1px solid #27272a}
.tab{padding:9px 14px;font-size:11px;color:#71717a;cursor:pointer}
.tab.active{color:#fff;background:#18181b;border-top:2px solid #6366f1}
#editor{flex:1;background:#18181b;color:#e4e4e7;border:none;padding:14px;font-family:Consolas,monospace;font-size:13px;line-height:1.7;resize:none;outline:none}
.right{flex:1.1;background:#1e1e24;display:flex;flex-direction:column;border-left:1px solid #27272a}
.rhead{padding:8px 12px;background:#121215;border-bottom:1px solid #27272a;display:flex;justify-content:space-between;font-size:12px}
.rwrap{flex:1;padding:15px;overflow:auto;background:#2a2a35;display:flex;justify-content:center}
#prev{width:100%;height:100%;border:none;background:#fff;border-radius:12px}
#qrBox{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:999;justify-content:center;align-items:center}
</style>
</head>
<body>
<div class="top">
<div class="logo">🚀 Clyxess Kids Coding Lab <span class="beta">BETA</span></div>
<select class="sel" id="ageSelect" onchange="changeAgeBySelect()"><option>Select Age</option><option>5 Years</option><option>6 Years</option><option>7 Years</option><option>8 Years</option><option>9 Years</option><option>10 Years</option><option>11-12 Years</option><option>13-14 Years</option><option>15-16 Years</option><option>17-18 Years</option><option>18+ Years</option></select>
<select class="sel" id="langSelect"><option>HTML</option><option>CSS</option><option>JavaScript</option><option>Python</option><option>Scratch (Block)</option></select>
<select class="sel" id="readySelect" onchange="loadReady()"><option>📦 3 Readymade Website</option><option value="r1">1. My First Page (Easy)</option><option value="r2">2. My Colour Game (Medium)</option><option value="r3">3. My Mini Shop (Pro)</option></select>
<button class="btn" onclick="blankPage()">🧹 Blank / Clear</button>
<button class="btn" onclick="downloadCode()">⬇ Download</button>
<button class="btn" style="border-color:#f59e0b;color:#fbbf24" onclick="openQR()">📱 QR / Link</button>
<button class="btn-run" onclick="run()">▶ Run</button>
</div>

<div class="main">
<div class="left">
<div class="tt">🎂 Select Age (5 to 18+)</div><div id="ageList"></div>
<div class="tt">💻 Language</div><div id="langList"></div>
<div style="margin-top:12px;background:#6366f1;padding:10px;border-radius:10px;font-size:11px;line-height:1.4"><b id="tipTitle">5 Years Tip:</b><br><span id="tipText">Yahan apna naam likho, color badlo! Button dabao to magic hoga!</span></div>
</div>

<div class="center">
<div class="tabs"><div class="tab active">index.html</div><div class="tab">style.css</div><div class="tab">script.js</div></div>
<textarea id="editor"></textarea>
<div style="padding:6px 10px;background:#09090b;font-size:10px;color:#666;display:flex;justify-content:space-between"><span>✅ Auto-save ON • Live Preview</span><span id="status">Ready for 5 Years</span></div>
</div>

<div class="right">
<div class="rhead"><span>👁 Live Preview</span><span style="color:#22c55e">● Live</span></div>
<div class="rwrap"><iframe id="prev"></iframe></div>
</div>
</div>

<div id="qrBox"><div style="background:#1e1e24;padding:20px;border-radius:16px;text-align:center;width:90%;max-width:350px;border:1px solid #333"><h4>📱 Mobile me dekho</h4><img id="qrImg" src="" style="width:200px;height:200px;background:#fff;padding:8px;border-radius:10px;margin-top:10px"><input id="linkInput" readonly style="width:100%;margin-top:10px;background:#111;border:1px solid #333;color:#22c55e;padding:6px;border-radius:6px;font-size:9px"><div style="display:flex;gap:8px;margin-top:10px"><button onclick="copyLink()" style="flex:1;background:#6366f1;color:#fff;border:none;padding:8px;border-radius:8px">Copy Link</button><button onclick="document.getElementById('qrBox').style.display='none'" style="flex:1;background:#333;color:#fff;border:none;padding:8px;border-radius:8px">Band</button></div></div></div>

<script>
const ageTemplates={
"5 Years":{html:`<!-- 5 Saal ke bacche ke liye - Sirf Naam badlo -->\n<h1>👋 Hello! Mera Naam Aman Hai</h1>\n<p>Main 5 saal ka hu!</p>\n<!-- Neeche apna naam likho -->\n<h2 style="color:blue">Mera favourite color BLUE hai</h2>\n<button onclick="alert('Wah! Tumne button dabaya! 🌟')" style="padding:15px 30px;background:orange;color:white;border:none;border-radius:20px;font-size:18px">Mujhe Dabao!</button>`, css:`body{text-align:center;padding:30px;background:#fef9c3;font-family:'Comic Sans MS'} h1{background:white;padding:15px;border-radius:15px}`, tipTitle:"5 Years Tip:", tipText:"Apna naam likho - Aman ki jagah apna naam likh do. Blue ki jagah RED likh do to color badal jayega!"},
"6 Years":{html:`<h1>🔤 ABCD - A for Apple 🍎</h1>\n<div class="box">B for Ball ⚽</div>\n<div class="box">C for Cat 🐱</div>\n<button onclick="this.innerText='Shabash! 🌟'">Mujhe Click Karo</button>`, css:`body{text-align:center;padding:20px;background:#dcfce7}.box{background:white;margin:10px;padding:15px;border-radius:15px;font-size:20px}`, tipTitle:"6 Years Tip:", tipText:"Apple ki jagah apna favourite fruit likho! Color badlo!"},
"7 Years":{html:`<h1>🎨 Mera Rang Biranga Page</h1>\n<p>Neeche kisi rang pe click karo!</p>\n<div style="display:flex;gap:10px;justify-content:center">\n<div onclick="document.body.style.background='lightcoral'" style="width:70px;height:70px;background:red;border-radius:15px;cursor:pointer"></div>\n<div onclick="document.body.style.background='lightblue'" style="width:70px;height:70px;background:blue;border-radius:15px;cursor:pointer"></div>\n<div onclick="document.body.style.background='lightgreen'" style="width:70px;height:70px;background:green;border-radius:15px;cursor:pointer"></div>\n</div>`, css:`body{text-align:center;padding:30px;transition:0.5s}`, tipTitle:"7 Years Tip:", tipText:"Red, blue, green ki jagah apne color add karo!"},
"8 Years":{html:`<h1>🐶 My Pet Dog</h1>\n<img src="https://cdn-icons-png.flaticon.com/512/616/616408.png" width="100">\n<p>Iska naam Tommy hai! Woof Woof!</p>\n<button onclick="alert('Bhow Bhow! 🐶')">Tommy ko Bulao</button>`, css:`body{text-align:center;padding:20px;background:#ffedd5}`, tipTitle:"8 Years Tip:", tipText:"Dog ki jagah Cat ka photo laga sakte ho!"},
"9 Years":{html:`<h1>🏫 Meri School</h1>\n<ul style="text-align:left;display:inline-block;background:white;padding:20px;border-radius:15px">\n<li>Class 1 - Drawing 🎨</li>\n<li>Class 2 - ABCD 🔤</li>\n<li>Class 3 - Coding 💻</li>\n</ul>`, css:`body{padding:20px;background:#e0f2fe}`, tipTitle:"9 Years Tip:", tipText:"Apni school ki list banao!"},
"10 Years":{html:`<h1>🎮 Click Game - Score: <span id="sc">0</span></h1>\n<button onclick="document.getElementById('sc').innerText++" style="padding:20px 40px;background:#f59e0b;color:white;border:none;border-radius:15px;font-size:20px">CLICK KARO!</button>\n<p>Kitna score kar sakte ho?</p>`, css:`body{text-align:center;padding:40px;background:#fef3c7}`, tipTitle:"10 Years Tip:", tipText:"Game ka logic samjho - click pe score badhta hai!"},
"11-12 Years":{html:`<div style="padding:30px;text-align:center"><h1>👨‍💻 Hi, I am Coder Rohan</h1><p>Age 12 | I make websites</p><div style="background:white;color:black;padding:15px;border-radius:15px;margin-top:15px">My Skills: HTML, CSS, JS</div><button onclick="alert('Contact me!')" style="margin-top:15px;padding:10px 20px;border-radius:20px;border:none;background:#6366f1;color:white">Hire Me</button></div>`, css:`body{background:linear-gradient(135deg,#667eea,#764ba2);color:white;margin:0}`, tipTitle:"11-12 Years Tip:", tipText:"Apna portfolio banao!"},
"13-14 Years":{html:`<h1>🧮 Calculator</h1>\n<input id="n1" type="number" placeholder="Pehla number" style="padding:10px;border-radius:8px">\n<input id="n2" type="number" placeholder="Dusra number" style="padding:10px;border-radius:8px">\n<br><br>\n<button onclick="alert('Jawab: '+(Number(n1.value)+Number(n2.value)))" style="padding:10px 20px;background:green;color:white;border:none;border-radius:8px">Jodo (+)</button>\n<button onclick="alert('Jawab: '+(Number(n1.value)*Number(n2.value)))" style="padding:10px 20px;background:blue;color:white;border:none;border-radius:8px">Guna (x)</button>`, css:`body{text-align:center;padding:30px}`, tipTitle:"13-14 Years Tip:", tipText:"Plus ki jagah minus, multiply ka logic lagao!"},
"15-16 Years":{html:`<header style="background:white;padding:15px;display:flex;justify-content:space-between;box-shadow:0 2px 10px #0001"><b style="color:green;font-size:22px">🛒 FreshCart</b><span>Home | Cart</span></header>\n<div style="padding:30px"><h1 style="font-size:38px">Groceries<br><span style="color:green">Delivered Fast</span></h1><p>30 min me delivery!</p><button style="background:green;color:white;padding:12px 24px;border:none;border-radius:8px">Shop Now 🛒</button></div>`, css:`body{margin:0;background:#f0fdf4;font-family:sans-serif}`, tipTitle:"15-16 Years Tip:", tipText:"Pro shop ka design - color, text change karo!"},
"17-18 Years":{html:`<div style="padding:20px"><h1>💬 Chat App UI</h1><div style="background:white;border-radius:15px;padding:15px;max-width:350px"><p style="background:#e0e7ff;padding:10px;border-radius:10px">Hi! Project kaisa laga? 😊</p><p style="background:#dcfce7;padding:10px;border-radius:10px;text-align:right">Ek dum solid hai bhai! 🔥</p><input placeholder="Message likho..." style="width:100%;padding:10px;border-radius:20px;border:1px solid #ddd;margin-top:10px"></div></div>`, css:`body{background:#f3f4f6}`, tipTitle:"17-18 Years Tip:", tipText:"Chat app jaisa UI - isko real JS se connect kar sakte ho!"},
"18+ Years":{html:`<!DOCTYPE html>\n<html><head><title>My Pro Website</title></head><body>\n<h1>🚀 Welcome to Pro Coding</h1>\n<p>Ab yahan se tum apna khud ka full website likh sakte ho!</p>\n<button onclick="alert('Pro Coder!')">Click Me</button>\n</body></html>`, css:`body{padding:20px;font-family:Arial}`, tipTitle:"18+ Years Tip:", tipText:"Full blank - HTML, CSS, JS sab khud likho!"}
};

const readyMade={
r1:{html:`<h1>🌟 My First Page</h1><p>Mera naam <b style="color:blue">Aman</b> hai</p><p>Main 5 saal ka hu aur mujhe coding pasand hai!</p><button onclick="alert('Hi Aman!')">Hello Bolo</button>`, css:`body{text-align:center;padding:30px;background:#fef9c3} button{padding:12px 20px;background:orange;border:none;border-radius:20px}`},
r2:{html:`<h1>🎨 My Colour Game</h1><p>Click any color!</p><div style="display:flex;gap:10px;justify-content:center"><div onclick="document.body.style.background='pink'" style="width:60px;height:60px;background:red;border-radius:50%"></div><div onclick="document.body.style.background='lightblue'" style="width:60px;height:60px;background:blue;border-radius:50%"></div><div onclick="document.body.style.background='lightgreen'" style="width:60px;height:60px;background:green;border-radius:50%"></div></div>`, css:`body{text-align:center;padding:30px;transition:0.5s}`},
r3:{html:`<header style="background:white;padding:12px;display:flex;justify-content:space-between"><b>🛒 My Mini Shop</b><span>Cart (0)</span></header><div style="padding:20px"><h2>Toys - 50% OFF!</h2><div style="background:white;padding:15px;border-radius:12px"><p>🧸 Teddy - ₹299</p><button style="background:green;color:white;padding:8px 16px;border:none;border-radius:8px">Buy Now</button></div></div>`, css:`body{margin:0;background:#f0fdf4}`}
};

const ages=Object.keys(ageTemplates);
document.getElementById('ageList').innerHTML=ages.map((a,i)=>`<div class="age ${i==0?'active':''}" onclick="selectAge('${a}',this)">${a}</div>`).join('');
document.getElementById('langList').innerHTML=["HTML","CSS","JavaScript","Python","Scratch"].map((l,i)=>`<div class="lang ${i==0?'active':''}" onclick="this.parentNode.querySelectorAll('.lang').forEach(x=>x.classList.remove('active'));this.classList.add('active')">${l}</div>`).join('');

function selectAge(age,el){
 document.querySelectorAll('.age').forEach(x=>x.classList.remove('active')); el.classList.add('active');
 document.getElementById('ageSelect').value=age;
 applyAge(age);
}
function changeAgeBySelect(){
 let age=document.getElementById('ageSelect').value;
 if(!ageTemplates[age]) return;
 document.querySelectorAll('.age').forEach(x=>{ if(x.innerText==age) x.classList.add('active'); else x.classList.remove('active'); });
 applyAge(age);
}
function applyAge(age){
 let data=ageTemplates[age];
 document.getElementById('editor').value=data.html+"\n\n<style>\n"+data.css+"\n</style>";
 document.getElementById('tipTitle').innerText=data.tipTitle;
 document.getElementById('tipText').innerText=data.tipText;
 document.getElementById('status').innerText="Ready for "+age;
 run();
}
function loadReady(){
 let v=document.getElementById('readySelect').value;
 if(!readyMade[v]) return;
 let d=readyMade[v];
 document.getElementById('editor').value=d.html+"\n\n<style>\n"+d.css+"\n</style>";
 run();
}
function blankPage(){
 if(confirm("Kya sach me blank karna hai? Saara code hat jayega!")){
  document.getElementById('editor').value="<h1>Hello World!</h1>\n<p>Yahan se apna naya code likho...</p>\n\n<style>\nbody{padding:20px;font-family:Arial}\n</style>";
  run();
 }
}
function run(){
 let code=document.getElementById('editor').value;
 document.getElementById('prev').srcdoc=code;
 localStorage.setItem('clyxess_final',code);
}
function downloadCode(){
 let blob=new Blob([document.getElementById('editor').value],{type:'text/html'});
 let a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download="Clyxess-Project-"+Date.now()+".html"; a.click();
}
function openQR(){
 run();
 let b64=btoa(unescape(encodeURIComponent(document.getElementById('editor').value)));
 let dataUrl='data:text/html;base64,'+b64;
 document.getElementById('qrImg').src='https://api.qrserver.com/v1/create-qr-code/?size=250x250&data='+encodeURIComponent(dataUrl);
 document.getElementById('linkInput').value=dataUrl;
 document.getElementById('qrBox').style.display='flex';
}
function copyLink(){
 let i=document.getElementById('linkInput'); i.select();
 navigator.clipboard.writeText(i.value).then(()=>alert("✅ Link Copy ho gaya! Bacche WhatsApp pe khol sakte hain"));
}
let timer; document.getElementById('editor').addEventListener('input',()=>{clearTimeout(timer); timer=setTimeout(run,500);});
// default 5 years load
applyAge("5 Years");
</script>
</body>
</html>
'''
    components.html(html_code, height=950, scrolling=False) 
# ============================================================
# FINTECH & GLOBAL ECONOMICS LAB (GLOBAL LANGUAGE & BANKING)
# ============================================================

def render_learn_finance(client):
    import json
    import re
    import random

    def clean_json_text(text):
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        start = text.find("{"); end = text.rfind("}")
        if start != -1 and end != -1: return text[start:end + 1].strip()
        return text

    # ============================================================
    # 1. 50+ LANGUAGES LIST
    # ============================================================
    LANGUAGES = {
        "🇬🇧 English": "en",
        "🇮🇳 हिंदी (Hindi)": "hi",
        "🇮🇳 বাংলা (Bengali)": "bn",
        "🇮🇳 मराठी (Marathi)": "mr",
        "🇮🇳 తెలుగు (Telugu)": "te",
        "🇮🇳 தமிழ் (Tamil)": "ta",
        "🇮🇳 ગુજરાતી (Gujarati)": "gu",
        "🇮🇳 ಕನ್ನಡ (Kannada)": "kn",
        "🇮🇳 മലയാളം (Malayalam)": "ml",
        "🇮🇳 ଓଡ଼ିଆ (Odia)": "or",
        "🇮🇳 ਪੰਜਾਬੀ (Punjabi)": "pa",
        "🇮🇳 অসমীয়া (Assamese)": "as",
        "🇮🇳 اردو (Urdu)": "ur",
        "🇨🇳 中文 (Chinese)": "zh",
        "🇯🇵 日本語 (Japanese)": "ja",
        "🇰🇷 한국어 (Korean)": "ko",
        "🇪🇸 Español (Spanish)": "es",
        "🇫🇷 Français (French)": "fr",
        "🇩🇪 Deutsch (German)": "de",
        "🇸🇦 العربية (Arabic)": "ar",
        "🇵🇹 Português (Portuguese)": "pt",
        "🇷🇺 Русский (Russian)": "ru",
        "🇮🇹 Italiano (Italian)": "it",
        "🇹🇷 Türkçe (Turkish)": "tr",
        "🇮🇩 Bahasa Indonesia": "id",
        "🇲🇾 Bahasa Melayu": "ms",
        "🇹🇭 ไทย (Thai)": "th",
        "🇻🇳 Tiếng Việt (Vietnamese)": "vi",
        "🇳🇱 Nederlands (Dutch)": "nl",
        "🇵🇱 Polski (Polish)": "pl",
        "🇺🇦 Українська (Ukrainian)": "uk",
        "🇮🇷 فارسی (Persian)": "fa",
        "🇵🇭 Tagalog (Filipino)": "tl",
        "🇲🇲 မြန်မာ (Burmese)": "my",
        "🇬🇷 Ελληνικά (Greek)": "el",
        "🇸🇪 Svenska (Swedish)": "sv",
        "🇳🇴 Norsk (Norwegian)": "no",
        "🇩🇰 Dansk (Danish)": "da",
        "🇫🇮 Suomi (Finnish)": "fi",
        "🇷🇴 Română (Romanian)": "ro",
        "🇭🇺 Magyar (Hungarian)": "hu",
        "🇨🇿 Čeština (Czech)": "cs",
        "🇮🇱 עברית (Hebrew)": "he",
        "🇿🇦 Zulu": "zu",
        "🇰🇪 Swahili": "sw",
        "🇳🇬 Yoruba": "yo",
        "🇵🇰 پښتو (Pashto)": "ps",
        "🇱🇰 සිංහල (Sinhala)": "si",
        "🇳🇵 नेपाली (Nepali)": "ne"
    }

    # UI TRANSLATION (Major Languages)
    UI_TEXTS = {
        "en": {"title": "FinTech Lab", "learn": "Learn Finance", "market": "Virtual Stock Market", "banking": "Banking System", "startup": "Startup & Web3", "cash": "Cash Balance", "portfolio": "Portfolio Value", "networth": "Net Worth", "deposit": "Deposit", "withdraw": "Withdraw", "loan": "Take Loan", "repay": "Repay Loan", "buy": "Buy", "sell": "Sell", "lang": "Language"},
        "hi": {"title": "फिनटेक लैब", "learn": "फाइनेंस सीखें", "market": "वर्चुअल स्टॉक मार्केट", "banking": "बैंकिंग सिस्टम", "startup": "स्टार्टअप और वेब3", "cash": "कैश बैलेंस", "portfolio": "पोर्टफोलियो वैल्यू", "networth": "कुल संपत्ति", "deposit": "जमा करें", "withdraw": "निकालें", "loan": "लोन लें", "repay": "लोन चुकाएं", "buy": "खरीदें", "sell": "बेचें", "lang": "भाषा"},
        "bn": {"title": "ফিনটেক ল্যাব", "learn": "ফিনান্স শিখুন", "market": "ভার্চুয়াল স্টক মার্কেট", "banking": "ব্যাংকিং সিস্টেম", "startup": "স্টার্টআপ এবং ওয়েব3", "cash": "নগদ ব্যালেন্স", "portfolio": "পোর্টফোলিও মূল্য", "networth": "মোট সম্পদ", "deposit": "জমা করুন", "withdraw": "উত্তোলন করুন", "loan": "ঋণ নিন", "repay": "ঋণ পরিশোধ করুন", "buy": "কিনুন", "sell": "বিক্রয় করুন", "lang": "ভাষা"},
        "ta": {"title": "ஃபின்டெக் லேப்", "learn": "நிதி கற்க", "market": "மெய்நிகர் பங்குச் சந்தை", "banking": "வங்கி அமைப்பு", "startup": "ஸ்டார்ட்அப் & வெப்3", "cash": "பண இருப்பு", "portfolio": "போர்ட்ஃபோலியோ மதிப்பு", "networth": "நிகர மதிப்பு", "deposit": "வைப்பு", "withdraw": "எடு", "loan": "கடன் பெறு", "repay": "கடன் திரும்பச் செலுத்து", "buy": "வாங்கு", "sell": "விற்", "lang": "மொழி"},
        "te": {"title": "ఫిన్టెక్ ల్యాబ్", "learn": "ఫైనాన్స్ నేర్చుకో", "market": "వర్చువల్ స్టాక్ మార్కెట్", "banking": "బ్యాంకింగ్ సిస్టమ్", "startup": "స్టార్టప్ & వెబ్3", "cash": "నగదు నిల్వ", "portfolio": "పోర్ట్ఫోలియో విలువ", "networth": "నికర విలువ", "deposit": "జమ", "withdraw": "విత్డ్రా", "loan": "రుణం తీసుకో", "repay": "రుణం తిరిగి చెల్లించు", "buy": "కొనుగోలు", "sell": "అమ్మకం", "lang": "భాష"},
        "mr": {"title": "फिनटेक लॅब", "learn": "फायनान्स शिका", "market": "व्हर्च्युअल स्टॉक मार्केट", "banking": "बँकिंग सिस्टम", "startup": "स्टार्टअप आणि वेब3", "cash": "रोख शिल्लक", "portfolio": "पोर्टफोलिओ मूल्य", "networth": "निव्वळ संपत्ती", "deposit": "जमा करा", "withdraw": "काढा", "loan": "कर्ज घ्या", "repay": "कर्ज परत करा", "buy": "खरेदी करा", "sell": "विक्री करा", "lang": "भाषा"},
        "zh": {"title": "金融科技实验室", "learn": "学习金融", "market": "虚拟股票市场", "banking": "银行系统", "startup": "初创企业与Web3", "cash": "现金余额", "portfolio": "投资组合价值", "networth": "净资产", "deposit": "存款", "withdraw": "取款", "loan": "贷款", "repay": "还款", "buy": "买入", "sell": "卖出", "lang": "语言"},
        "ja": {"title": "フィンテックラボ", "learn": "金融を学ぶ", "market": "バーチャル株式市場", "banking": "銀行システム", "startup": "スタートアップとWeb3", "cash": "現金残高", "portfolio": "ポートフォリオ価値", "networth": "純資産", "deposit": "預金", "withdraw": "引き出し", "loan": "ローン", "repay": "返済", "buy": "買う", "sell": "売る", "lang": "言語"}
    }

    # ============================================================
    # 2. DROPDOWNS (Level, Currency, Language)
    # ============================================================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        class_level = st.selectbox(
            "🎓 Select Your Level",
            ["Class 5-8 (Basics)", "Class 9-10 (Intermediate)", "Class 11-12 (Advanced)", "College / University (Professional)"],
            key="fin_class_level"
        )
    
    with col2:
        CURRENCIES = {
            "🇮🇳 INR (₹)": {"symbol": "₹", "rate": 83.0},
            "🇺🇸 USD ($)": {"symbol": "$", "rate": 1.0},
            "🇨🇳 CNY (¥)": {"symbol": "¥", "rate": 7.2},
            "🇵🇰 PKR (₨)": {"symbol": "₨", "rate": 278.0},
            "🇪🇺 EUR (€)": {"symbol": "€", "rate": 0.92},
            "🇬🇧 GBP (£)": {"symbol": "£", "rate": 0.79},
            "🇯🇵 JPY (¥)": {"symbol": "¥", "rate": 150.0},
            "🇦🇪 AED (د.إ)": {"symbol": "د.إ", "rate": 3.67}, 
            "🇧🇩 BDT (৳)": {"symbol": "৳", "rate": 110.0},
            "🇷🇺 RUB (₽)": {"symbol": "₽", "rate": 92.0},
            "🇿🇦 ZAR (R)": {"symbol": "R", "rate": 18.5},
            "🇧🇷 BRL (R$)": {"symbol": "R$", "rate": 5.0}
        }
        if "fin_currency" not in st.session_state: st.session_state.fin_currency = "🇮🇳 INR (₹)"
        curr_label = st.selectbox("🌐 Select Currency", list(CURRENCIES.keys()), index=list(CURRENCIES.keys()).index(st.session_state.fin_currency))
        st.session_state.fin_currency = curr_label

    with col3:
        # 50+ Language Dropdown
        if "fin_lang" not in st.session_state: st.session_state.fin_lang = "🇬🇧 English"
        selected_lang_label = st.selectbox("🌍 Select Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.fin_lang))
        st.session_state.fin_lang = selected_lang_label
        lang_code = LANGUAGES[selected_lang_label]

    # UI टेक्स्ट लोड करना
    t = UI_TEXTS.get(lang_code, UI_TEXTS["en"])
    curr = CURRENCIES[curr_label]
    sym, rate = curr["symbol"], curr["rate"]

    is_junior = "Class 5-8" in class_level

    # ============================================================
    # 3. ADAPTIVE CSS (Kids vs Teens/Adults)
    # ============================================================
    if is_junior:
        st.markdown("""
        <style>
        .stApp { background-color: #F0F8FF; }
        .fin-header { background: linear-gradient(90deg, #FF9A9E 0%, #FECFEF 99%, #FECFEF 100%); padding: 15px; border-radius: 15px; color: #333; text-align: center; }
        .fin-card { background: #FFFFFF; border: 2px solid #FFD700; border-radius: 15px; padding: 15px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .fin-value { font-size: 24px; font-weight: bold; color: #FF5722; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp { background-color: #0B0E14; }
        .fin-header { background: linear-gradient(90deg, #0F2027, #203A43, #2C5364); padding: 20px; border-radius: 10px; border-bottom: 3px solid #00FFAA; color: white; text-align: center; }
        .fin-card { background: #1A202C; border: 1px solid #2D3748; border-radius: 10px; padding: 15px; color: #A0AEC0; text-align: center; }
        .fin-value { font-size: 22px; font-weight: bold; color: #00FFAA; font-family: monospace; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown(f'<div class="fin-header"><h1>💰 {t["title"]} - {class_level.split(" ")[0]} {class_level.split(" ")[1]}</h1></div>', unsafe_allow_html=True)

    # ============================================================
    # 4. STATE MANAGEMENT (Internal USD)
    # ============================================================
    if "fin_cash_usd" not in st.session_state: st.session_state.fin_cash_usd = 10000.0 if is_junior else 50000.0
    if "fin_loan_usd" not in st.session_state: st.session_state.fin_loan_usd = 0.0
    if "fin_portfolio" not in st.session_state: st.session_state.fin_portfolio = {"TECH": 0, "AI": 0, "EDU": 0, "CRYPTO": 0}
    if "fin_stock_prices_usd" not in st.session_state: 
        st.session_state.fin_stock_prices_usd = {"TECH": 150.0, "AI": 320.0, "EDU": 80.0, "CRYPTO": 500.0}

    def format_money(usd_val): return f"{sym}{usd_val * rate:,.2f}"

    # ============================================================
    # 5. TABS
    # ============================================================
    tab1, tab2, tab3, tab4 = st.tabs([f"📖 {t['learn']}", f"📈 {t['market']}", f"🏦 {t['banking']}", f"🚀 {t['startup']}"])

    # --- TAB 1: LEARN FINANCE ---
    with tab1:
        st.subheader(f"📖 {t['learn']}")
        topics = ["Money Basics & Saving", "Banking & Interest", "Global Macroeconomics", "Algorithmic Trading", "Startup Valuation", "AI in Finance"]
        if is_junior: topics = topics[:3] # छोटों के लिए सिर्फ बेसिक टॉपिक
        
        topic = st.selectbox("Select Topic:", topics)
        if st.button("🚀 Explain this Topic"):
            with st.spinner("AI समझा रहा है..."):
                tone = "very simple, fun, and with toys/candy examples" if is_junior else "professional and analytical"
                prompt = f"You are a Financial Expert. Explain '{topic}' to a student of level {class_level} in this language: {selected_lang_label}. Tone: {tone}."
                try:
                    response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], temperature=0.7, max_tokens=1500)
                    st.markdown(response.choices[0].message.content)
                except Exception:
                    st.error("Explanation नहीं आ पाया।")

    # --- TAB 2: VIRTUAL STOCK MARKET ---
    with tab2:
        st.subheader(f"📈 {t['market']}")
        
        # Price Fluctuation
        for stock in st.session_state.fin_stock_prices_usd:
            change = random.uniform(-0.05, 0.05)
            st.session_state.fin_stock_prices_usd[stock] = max(10.0, round(st.session_state.fin_stock_prices_usd[stock] * (1 + change), 2))

        total_portfolio_value_usd = sum(st.session_state.fin_portfolio[s] * st.session_state.fin_stock_prices_usd[s] for s in st.session_state.fin_portfolio)
        total_net_worth_usd = st.session_state.fin_cash_usd + total_portfolio_value_usd - st.session_state.fin_loan_usd

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="fin-card">💵 {t["cash"]}<br><span class="fin-value">{format_money(st.session_state.fin_cash_usd)}</span></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="fin-card">📊 {t["portfolio"]}<br><span class="fin-value">{format_money(total_portfolio_value_usd)}</span></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="fin-card">🏆 {t["networth"]}<br><span class="fin-value">{format_money(total_net_worth_usd)}</span></div>', unsafe_allow_html=True)

        st.divider()
        for stock, price_usd in st.session_state.fin_stock_prices_usd.items():
            col_a, col_b, col_c = st.columns([2, 1, 1])
            with col_a:
                st.markdown(f'**{stock}** | Price: {format_money(price_usd)} | Owned: {st.session_state.fin_portfolio[stock]}')
            with col_b:
                if st.button(f"{t['buy']}", key=f"buy_{stock}"):
                    if st.session_state.fin_cash_usd >= price_usd:
                        st.session_state.fin_cash_usd -= price_usd
                        st.session_state.fin_portfolio[stock] += 1
                        st.rerun()
                    else: st.error("पैसे कम हैं!")
            with col_c:
                if st.button(f"{t['sell']}", key=f"sell_{stock}"):
                    if st.session_state.fin_portfolio[stock] > 0:
                        st.session_state.fin_cash_usd += price_usd
                        st.session_state.fin_portfolio[stock] -= 1
                        st.rerun()
                    else: st.error("शेयर नहीं हैं!")

    # --- TAB 3: BANKING SYSTEM ---
    with tab3:
        st.subheader(f"🏦 {t['banking']}")
        st.write(f"{t['cash']}: **{format_money(st.session_state.fin_cash_usd)}**")
        st.write(f"{t['loan']}: **{format_money(st.session_state.fin_loan_usd)}**")

        col1, col2 = st.columns(2)
        with col1:
            amt = st.number_input("Amount:", min_value=100, value=1000)
            amt_usd = amt / rate
            if st.button(f"📥 {t['deposit']}"):
                st.session_state.fin_cash_usd += amt_usd
                st.rerun()
            if st.button(f"📤 {t['withdraw']}"):
                if st.session_state.fin_cash_usd >= amt_usd:
                    st.session_state.fin_cash_usd -= amt_usd
                    st.rerun()
                else: st.error("बैलेंस कम है!")

        with col2:
            loan_amt = st.number_input("Loan Amount:", min_value=500, value=5000)
            loan_usd = loan_amt / rate
            if st.button(f"📝 {t['loan']}"):
                st.session_state.fin_cash_usd += loan_usd
                st.session_state.fin_loan_usd += loan_usd
                st.rerun()
            if st.button(f"✅ {t['repay']}"):
                if st.session_state.fin_cash_usd >= loan_usd:
                    st.session_state.fin_cash_usd -= loan_usd
                    st.session_state.fin_loan_usd = max(0.0, st.session_state.fin_loan_usd - loan_usd)
                    st.rerun()
                else: st.error("पैसे कम हैं!")

    # --- TAB 4: STARTUP & WEB3 ---
    with tab4:
        st.subheader(f"🚀 {t['startup']}")
        
        if is_junior:
            st.info("यह सेक्शन आपकी क्लास के लिए अभी थोड़ा एडवांस है, लेकिन आप इसे पढ़ सकते हैं!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Startup Valuation Calculator")
            revenue = st.number_input(f"Annual Revenue ({sym}):", min_value=1000, value=50000)
            growth = st.slider("Growth Rate (%):", 1, 100, 20)
            valuation = (revenue * (1 + growth/100) * 5) / 5
            st.metric(label="Estimated Valuation", value=f"{sym}{valuation:,.2f}")

        with col2:
            st.markdown("### 🤖 Explain Web3 & Smart Contracts")
            if st.button("Ask AI"):
                with st.spinner("AI सोच रहा है..."):
                    prompt = f"Explain Web3 and Smart Contracts to a {class_level} student in this language: {selected_lang_label}. Provide a small Solidity code example." if not is_junior else f"Explain what is Blockchain and Crypto in very simple words for a small kid in this language: {selected_lang_label}."
                    try:
                        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}], temperature=0.7, max_tokens=1000)
                        st.info(response.choices[0].message.content)
                    except: st.error("AI बिज़ी है।")                               
# ============================================================
# PHYSICS LAB MODULE (DAY 2 - FULL ADVANCED GLOBAL EDITION)
# Features: Quantum, Space, Robotics, Renewable Energy, 3D Mechanics
# ============================================================

def render_physics_lab(client):
    st.markdown('<div class="header"><h1>⚛️ Physics Lab - Clyxess AI School</h1></div>', unsafe_allow_html=True)
    st.caption("यहाँ बच्चे Virtual Experiments करेंगे, Formulas देखेंगे, Observations लिखेंगे और AI से समझेंगे।")

    # 1. क्लास/लेवल चुनना
    class_level = st.selectbox(
        "🎓 Select Class / Level",
        ["Class 5-6", "Class 7-8", "Class 9-10", "Class 11-12", "University Level"],
        key="physics_class"
    )

    # 2. टैब्स बनाना
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Learn (सीखो)", "🧪 Virtual Lab (प्रयोग)", "🎯 Challenge (टेस्ट)", "💬 Ask a Doubt (सवाल)"])

    # ============================================================
    # TAB 1: LEARN (कॉन्सेप्ट सीखना)
    # ============================================================
    with tab1:
        st.subheader("📖 Advanced Physics Concepts")
        topic = st.selectbox(
            "कौन सा टॉपिक सीखना है?",
            ["Quantum Computing Basics", "Space Tech & Rocket Science", "Renewable Energy", 
             "Robotics Simulation", "3D Mechanics", "Newton's Laws of Motion", 
             "Gravity", "Energy & Work", "Light & Optics", "Sound & Waves"]
        )
        if st.button("🚀 Explain this Topic"):
            with st.spinner("Teacher समझा रहा है..."):
                prompt = f"""
                You are a Physics Teacher. Explain '{topic}' to a student of {class_level}.
                Use simple Hinglish (Hindi + English). Give real-life examples (like cricket, cars, space, robots).
                Make it engaging, not boring. End with a quick question to check understanding.
                """
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7, max_tokens=1500
                    )
                    st.markdown(response.choices[0].message.content)
                except Exception:
                    st.error("Explanation नहीं आ पाया। फिर कोशिश करें।")

    # ============================================================
    # TAB 2: VIRTUAL LAB (इंटरैक्टिव प्रयोग, Variables, Formulas, Observations)
    # ============================================================
    with tab2:
        st.subheader("🧪 Interactive Virtual Lab")
        st.write("स्लाइडर घुमाओ, फॉर्मूला देखो और ऑब्जर्वेशन करो!")

        experiment = st.selectbox("प्रयोग चुनें:", 
            ["Space Tech: Rocket Launch", "Renewable Energy: Solar Power", "Gravity: Weight on Planets"])

        st.markdown("---")

        # --- Experiment A: Rocket Launch (Space Tech) ---
        if experiment == "Space Tech: Rocket Launch":
            st.markdown("### 🚀 Experiment: Rocket Launch Simulation")
            
            col1, col2 = st.columns(2)
            with col1:
                thrust = st.slider("Thrust (बल) in Newtons:", 1000, 50000, 15000)
            with col2:
                mass = st.slider("Rocket Mass (वजन) in kg:", 500, 5000, 2000)
            
            g = 9.8  # Earth's gravity
            net_force = thrust - (mass * g)
            acceleration = net_force / mass

            # Formula Display
            st.info(f"📐 **Formula:** Acceleration = (Thrust - (Mass × Gravity)) / Mass")
            st.info(f"📐 **Calculation:** ({thrust} - ({mass} × {g})) / {mass} = **{acceleration:.2f} m/s²**")

            if acceleration > 0:
                st.success(f"🚀 Rocket उड़ान भर रहा है! Acceleration: {acceleration:.2f} m/s²")
            else:
                st.error("❌ Rocket नहीं उड़ पाएगा! Thrust कम है या Mass ज्यादा है।")

            # Observation Section
            st.markdown("📝 **Observation:**")
            st.write("जब Thrust बढ़ाते हैं, तो Acceleration बढ़ता है। जब Mass बढ़ाते हैं, तो Acceleration घटता है।")
            
            if st.button("AI से समझो (Rocket)"):
                with st.spinner("AI समझा रहा है..."):
                    prompt = f"Explain Rocket Launch physics (Thrust, Mass, Acceleration, Net Force) to a {class_level} student in simple Hinglish. The rocket had thrust={thrust}N, mass={mass}kg, giving acceleration={acceleration:.2f} m/s². Explain why it goes up or fails."
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7, max_tokens=800
                        )
                        st.info(response.choices[0].message.content)
                    except:
                        st.error("AI बिज़ी है।")

        # --- Experiment B: Solar Power (Renewable Energy) ---
        elif experiment == "Renewable Energy: Solar Power":
            st.markdown("### ☀️ Experiment: Solar Panel Output")
            
            col1, col2 = st.columns(2)
            with col1:
                sunlight = st.slider("Sunlight Intensity (0-100%):", 0, 100, 80)
            with col2:
                panel_area = st.slider("Panel Area (sq meters):", 1.0, 10.0, 5.0)
            
            efficiency = 0.18  # 18% efficiency
            energy = sunlight * panel_area * efficiency

            # Formula Display
            st.info(f"📐 **Formula:** Energy = Sunlight × Area × Efficiency")
            st.info(f"📐 **Calculation:** {sunlight} × {panel_area} × {efficiency} = **{energy:.2f} kWh**")

            st.metric(label="⚡ Energy Generated", value=f"{energy:.2f} kWh")

            # Observation Section
            st.markdown("📝 **Observation:**")
            st.write("धूप तेज़ होगी, तो बिजली ज्यादा बनेगी। पैनल बड़ा होगा, तो बिजली ज्यादा बनेगी।")

            if st.button("AI से समझो (Solar)"):
                with st.spinner("AI समझा रहा है..."):
                    prompt = f"Explain Solar Energy and Renewable Energy to a {class_level} student in simple Hinglish. The student got {energy:.2f} kWh with sunlight={sunlight}%, area={panel_area}sqm. Explain why renewable energy is important for Earth."
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7, max_tokens=800
                        )
                        st.info(response.choices[0].message.content)
                    except:
                        st.error("AI बिज़ी है।")

        # --- Experiment C: Gravity (Weight on Planets) ---
        elif experiment == "Gravity: Weight on Planets":
            st.markdown("### 🌍 Experiment: Weight on Different Planets")
            mass = st.slider("अपना वजन चुनें (Mass in kg):", 10, 100, 50)
            
            planet = st.selectbox(
                "किस ग्रह पर जाना है?",
                ["Earth (9.8 m/s²)", "Moon (1.6 m/s²)", "Mars (3.7 m/s²)", "Jupiter (24.8 m/s²)"]
            )
            
            gravity_map = {"Earth (9.8 m/s²)": 9.8, "Moon (1.6 m/s²)": 1.6, "Mars (3.7 m/s²)": 3.7, "Jupiter (24.8 m/s²)": 24.8}
            gravity = gravity_map[planet]
            weight = mass * gravity

            st.info(f"📐 **Formula:** Weight = Mass × Gravity")
            st.metric(label=f"तुम्हारा वजन {planet} पर", value=f"{weight:.2f} N (Newtons)")

            st.markdown("📝 **Observation:**")
            st.write("Mass हमेशा same रहता है, लेकिन Weight gravity के कारण बदल जाता है।")

            if st.button("AI से समझो (Gravity)"):
                with st.spinner("AI समझा रहा है..."):
                    prompt = f"Explain Mass vs Weight to a {class_level} student in simple Hinglish. On {planet}, a {mass}kg student weighs {weight:.2f}N. Explain why weight changes but mass stays the same."
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.7, max_tokens=800
                        )
                        st.info(response.choices[0].message.content)
                    except:
                        st.error("AI बिज़ी है।")

    # ============================================================
    # TAB 3: CHALLENGE (टेस्ट और पहेली)
    # ============================================================
    with tab3:
        st.subheader("🎯 Physics Challenge (Advanced)")
        if st.button("🚀 Start Physics Quiz"):
            with st.spinner("सवाल बन रहे हैं..."):
                quiz_prompt = f"""
                Create 5 multiple-choice questions (MCQs) on Advanced Physics concepts (like Space, Quantum, Energy, Mechanics) for a {class_level} student.
                Format strictly as JSON:
                [{{"question":"...", "options":["A","B","C","D"], "answer":"A"}}]
                Language: Hinglish. Focus on real-life examples.
                """
                try:
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": quiz_prompt}],
                        temperature=0.5, max_tokens=1500
                    )
                    import json
                    raw_text = completion.choices[0].message.content
                    start = raw_text.find("["); end = raw_text.rfind("]") + 1
                    quiz_data = json.loads(raw_text[start:end])
                    st.session_state.phy_quiz_data = quiz_data
                    st.session_state.phy_quiz_score = 0
                    st.session_state.phy_quiz_index = 0
                except:
                    st.error("Quiz generate नहीं हो पाया।")

        if "phy_quiz_data" in st.session_state and st.session_state.phy_quiz_data:
            q_index = st.session_state.phy_quiz_index
            if q_index < len(st.session_state.phy_quiz_data):
                q = st.session_state.phy_quiz_data[q_index]
                st.write(f"**Q{q_index+1}: {q['question']}**")
                user_ans = st.radio("Choose:", q["options"], key=f"phy_q_{q_index}")
                if st.button("Submit", key=f"phy_sub_{q_index}"):
                    if user_ans == q["answer"]:
                        st.success("✅ सही जवाब! शाबाश!")
                        st.session_state.phy_quiz_score += 1
                    else:
                        st.error(f"❌ गलत। सही जवाब: {q['answer']}")
                    st.session_state.phy_quiz_index += 1
                    st.rerun()
            else:
                st.balloons()
                st.success(f"🎉 Quiz पूरा! स्कोर: {st.session_state.phy_quiz_score}/{len(st.session_state.phy_quiz_data)}")
                if st.button("🔄 फिर से खेलें"):
                    del st.session_state.phy_quiz_data
                    st.rerun()

    # ============================================================
    # TAB 4: ASK A DOUBT (सवाल पूछना)
    # ============================================================
    with tab4:
        st.subheader("💬 Ask an Advanced Physics Doubt")
        if "phy_doubts" not in st.session_state:
            st.session_state.phy_doubts = []

        for msg in st.session_state.phy_doubts:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        doubt_input = st.chat_input("कोई भी Physics का सवाल पूछो (Space, Quantum, Energy, etc.)...")
        if doubt_input:
            st.session_state.phy_doubts.append({"role": "user", "content": doubt_input})
            with st.chat_message("user"):
                st.markdown(doubt_input)
            with st.chat_message("assistant"):
                with st.spinner("Teacher soch raha hai..."):
                    prompt = f"You are a loving Physics Teacher. Answer this doubt for a {class_level} student in simple Hinglish: {doubt_input}"
                    try:
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "system", "content": prompt}] + st.session_state.phy_doubts[-4:],
                            temperature=0.7, max_tokens=1000
                        )
                        reply = response.choices[0].message.content
                    except:
                        reply = "Beta, thodi dikkat aa gayi. Phir se pucho."
                    st.markdown(reply)
                    st.session_state.phy_doubts.append({"role": "assistant", "content": reply})
# ============================================================
# MATH GAME MASTER (GLOBAL MULTILINGUAL EDITION)
# ============================================================

def render_math_lab(client):
    import json
    import re
    import random

    def clean_json_text(text):
        text = text.strip()
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1: return text[start:end + 1].strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1: return text[start:end + 1].strip()
        return text

    # ============================================================
    # 1. 50+ LANGUAGES LIST (Global & Indian)
    # ============================================================
    LANGUAGES = {
        "🇬🇧 English": "en",
        "🇮🇳 हिंदी (Hindi)": "hi",
        "🇮🇳 বাংলা (Bengali)": "bn",
        "🇮🇳 मराठी (Marathi)": "mr",
        "🇮🇳 తెలుగు (Telugu)": "te",
        "🇮🇳 தமிழ் (Tamil)": "ta",
        "🇮🇳 ગુજરાતી (Gujarati)": "gu",
        "🇮🇳 ಕನ್ನಡ (Kannada)": "kn",
        "🇮🇳 മലയാളം (Malayalam)": "ml",
        "🇮🇳 ଓଡ଼ିଆ (Odia)": "or",
        "🇮🇳 ਪੰਜਾਬੀ (Punjabi)": "pa",
        "🇮🇳 অসমীয়া (Assamese)": "as",
        "🇮🇳 اردو (Urdu)": "ur",
        "🇨🇳 中文 (Chinese)": "zh",
        "🇯🇵 日本語 (Japanese)": "ja",
        "🇰🇷 한국어 (Korean)": "ko",
        "🇪🇸 Español (Spanish)": "es",
        "🇫🇷 Français (French)": "fr",
        "🇩🇪 Deutsch (German)": "de",
        "🇸🇦 العربية (Arabic)": "ar",
        "🇵🇹 Português (Portuguese)": "pt",
        "🇷🇺 Русский (Russian)": "ru",
        "🇮🇹 Italiano (Italian)": "it",
        "🇹🇷 Türkçe (Turkish)": "tr",
        "🇮🇩 Bahasa Indonesia": "id",
        "🇲🇾 Bahasa Melayu": "ms",
        "🇹🇭 ไทย (Thai)": "th",
        "🇻🇳 Tiếng Việt (Vietnamese)": "vi",
        "🇳🇱 Nederlands (Dutch)": "nl",
        "🇵🇱 Polski (Polish)": "pl",
        "🇺🇦 Українська (Ukrainian)": "uk",
        "🇮🇷 فارسی (Persian)": "fa",
        "🇵🇭 Tagalog (Filipino)": "tl",
        "🇲🇲 မြန်မာ (Burmese)": "my",
        "🇬🇷 Ελληνικά (Greek)": "el",
        "🇸🇪 Svenska (Swedish)": "sv",
        "🇳🇴 Norsk (Norwegian)": "no",
        "🇩🇰 Dansk (Danish)": "da",
        "🇫🇮 Suomi (Finnish)": "fi",
        "🇷🇴 Română (Romanian)": "ro",
        "🇭🇺 Magyar (Hungarian)": "hu",
        "🇨🇿 Čeština (Czech)": "cs",
        "🇮🇱 עברית (Hebrew)": "he",
        "🇿🇦 Zulu": "zu",
        "🇰🇪 Swahili": "sw",
        "🇳🇬 Yoruba": "yo",
        "🇵🇰 پښتو (Pashto)": "ps",
        "🇱🇰 සිංහල (Sinhala)": "si",
        "🇳🇵 नेपाली (Nepali)": "ne"
    }
    
    # UI का अनुवाद (Top 10 भाषाओं के लिए)
    UI_TEXTS = {
        "en": {"title": "Math Game Master", "score": "Total Score", "streak": "Streak", "level": "Level", "submit": "Submit Answer", "next": "Next Question", "reset": "Reset Game", "correct": "Correct!", "wrong": "Wrong! Correct answer:", "explain": "Explanation:"},
        "hi": {"title": "गणित गेम मास्टर", "score": "कुल स्कोर", "streak": "लगातार सही", "level": "स्तर", "submit": "उत्तर जमा करें", "next": "अगला सवाल", "reset": "गेम रीसेट करें", "correct": "शाबाश! सही जवाब!", "wrong": "गलत जवाब। सही उत्तर:", "explain": "व्याख्या:"},
        "bn": {"title": "গণিত গেম মাস্টার", "score": "মোট স্কোর", "streak": "স্ট্রিক", "level": "স্তর", "submit": "উত্তর জমা দিন", "next": "পরবর্তী প্রশ্ন", "reset": "গেম রিসেট করুন", "correct": "সঠিক!", "wrong": "ভুল! সঠিক উত্তর:", "explain": "ব্যাখ্যা:"},
        "ta": {"title": "கணித விளையாட்டு மாஸ்டர்", "score": "மொத்த மதிப்பெண்", "streak": "தொடர் வெற்றி", "level": "நிலை", "submit": "பதிலை சமர்ப்பிக்கவும்", "next": "அடுத்த கேள்வி", "reset": "விளையாட்டை மீட்டமைக்கவும்", "correct": "சரி!", "wrong": "தவறு! சரியான பதில்:", "explain": "விளக்கம்:"},
        "te": {"title": "గణిత గేమ్ మాస్టర్", "score": "మొత్తం స్కోరు", "streak": "వరుస విజయాలు", "level": "స్థాయి", "submit": "సమాధానం సమర్పించండి", "next": "తదుపరి ప్రశ్న", "reset": "గేమ్ రీసెట్ చేయండి", "correct": "సరైనది!", "wrong": "తప్పు! సరైన సమాధానం:", "explain": "వివరణ:"},
        "mr": {"title": "गणित गेम मास्टर", "score": "एकूण गुण", "streak": "स्ट्रीक", "level": "स्तर", "submit": "उत्तर सबमिट करा", "next": "पुढील प्रश्न", "reset": "गेम रीसेट करा", "correct": "बरोबर!", "wrong": "चूक! बरोबर उत्तर:", "explain": "स्पष्टीकरण:"},
        "zh": {"title": "数学游戏大师", "score": "总分", "streak": "连胜", "level": "等级", "submit": "提交答案", "next": "下一题", "reset": "重置游戏", "correct": "正确!", "wrong": "错误! 正确答案:", "explain": "解释:"},
        "ja": {"title": "数学ゲームマスター", "score": "合計スコア", "streak": "連続正解", "level": "レベル", "submit": "回答を送信", "next": "次の問題", "reset": "ゲームをリセット", "correct": "正解!", "wrong": "不正解! 正しい答え:", "explain": "解説:"},
        "es": {"title": "Maestro de Matemáticas", "score": "Puntuación Total", "streak": "Racha", "level": "Nivel", "submit": "Enviar Respuesta", "next": "Siguiente Pregunta", "reset": "Reiniciar Juego", "correct": "¡Correcto!", "wrong": "¡Incorrecto! Respuesta correcta:", "explain": "Explicación:"},
        "fr": {"title": "Maître des Maths", "score": "Score Total", "streak": "Série", "level": "Niveau", "submit": "Soumettre la Réponse", "next": "Question Suivante", "reset": "Réinitialiser le Jeu", "correct": "Correct!", "wrong": "Incorrect! Bonne réponse:", "explain": "Explication:"}
    }

    # ============================================================
    # 2. LANGUAGE & LEVEL SELECTION
    # ============================================================
    col_lang, col_level = st.columns([1, 2])
    with col_lang:
        selected_lang_label = st.selectbox("🌐 Language", list(LANGUAGES.keys()), key="math_lang_select")
        lang_code = LANGUAGES[selected_lang_label]
    
    with col_level:
        class_level = st.selectbox(
            "🎓 Select Your Level",
            ["Class 1-2", "Class 3-5", "Class 6-8", "Class 9-10", "Class 11-12", "University"],
            key="math_game_level"
        )

    # UI टेक्स्ट लोड करना (अगर भाषा नहीं मिली तो English)
    t = UI_TEXTS.get(lang_code, UI_TEXTS["en"])
    is_junior = class_level.startswith(("Class 1-2", "Class 3-5", "Class 6-8"))

    # ============================================================
    # 3. CSS THEME (Adaptive for Kids vs Teens)
    # ============================================================
    if is_junior:
        st.markdown("""
        <style>
        .stApp { background-color: #131F24; }
        .header-box { background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%); padding: 15px; border-radius: 15px; color: white; text-align: center; }
        .metric-card { background: #1e1e2f; border: 2px solid #333; border-radius: 15px; padding: 15px; text-align: center; color: white; }
        .question-card { background: linear-gradient(135deg, #1f1c2c, #3b3b5c); padding: 25px; border-radius: 15px; border: 1px solid #444; margin: 20px 0; text-align: center; }
        .question-text { font-size: 26px; font-weight: bold; color: #fff; }
        .feedback-success { background-color: #D7FFB8; color: #2E7D32; padding: 15px; border-radius: 15px; text-align: center; font-weight: bold; }
        .feedback-error { background-color: #FFDFE0; color: #C62828; padding: 15px; border-radius: 15px; text-align: center; font-weight: bold; }
        </style>
        """, unsafe_allow_html=True)
        header_title = f"🎮 {t['title']}"
    else:
        st.markdown("""
        <style>
        .stApp { background-color: #0E1117; }
        .header-box { background: #1E293B; padding: 20px; border-radius: 8px; border-left: 5px solid #3B82F6; color: white; }
        .metric-card { background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 15px; color: #94A3B8; text-align: left; }
        .metric-value { font-size: 24px; font-weight: bold; color: #3B82F6; font-family: monospace; }
        .question-card { background: #1E293B; padding: 30px; border-radius: 8px; border: 1px solid #334155; margin: 20px 0; }
        .question-text { font-size: 22px; font-weight: 500; color: #F8FAFC; font-family: 'Inter', sans-serif; }
        .feedback-success { background-color: #064E3B; color: #34D399; padding: 15px; border-radius: 8px; border-left: 4px solid #10B981; }
        .feedback-error { background-color: #450A0A; color: #F87171; padding: 15px; border-radius: 8px; border-left: 4px solid #EF4444; }
        </style>
        """, unsafe_allow_html=True)
        header_title = f"📊 {t['title']}"

    st.markdown(f'<div class="header-box"><h2>{header_title}</h2></div>', unsafe_allow_html=True)

    # ============================================================
    # 4. STATE & DASHBOARD
    # ============================================================
    if "math_game_score" not in st.session_state: st.session_state.math_game_score = 0
    if "math_game_streak" not in st.session_state: st.session_state.math_game_streak = 0
    if "math_current_question" not in st.session_state: st.session_state.math_current_question = None
    if "math_game_answered" not in st.session_state: st.session_state.math_game_answered = False
    if "math_game_q_id" not in st.session_state: st.session_state.math_game_q_id = 0

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="metric-card">🏆 {t["score"]}<br><span class="metric-value">{st.session_state.math_game_score}</span></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card">🔥 {t["streak"]}<br><span class="metric-value">{st.session_state.math_game_streak}</span></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card">📚 {t["level"]}<br><span class="metric-value" style="font-size:16px;">{class_level}</span></div>', unsafe_allow_html=True)

    st.write("")

    # ============================================================
    # 5. AI QUESTION GENERATION (IN SELECTED LANGUAGE)
    # ============================================================
    def generate_math_question(level, is_junior, lang_name):
        tone = "fun and engaging" if is_junior else "professional and challenging"
        prompt = f"""
        You are an expert Math Tutor. Generate ONE multiple-choice math question for a student of level: {level}.
        The tone should be {tone}.
        IMPORTANT: The question, options, and explanation MUST be in this language: {lang_name}.
        Provide the response in STRICT JSON format ONLY:
        {{
            "question": "The math question in {lang_name}",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "The exact correct option",
            "explanation": "Short explanation in {lang_name}."
        }}
        """
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7, max_tokens=800
            )
            raw_text = response.choices[0].message.content
            clean_json = clean_json_text(raw_text)
            question_data = json.loads(clean_json)
            if all(k in question_data for k in ["question", "options", "answer", "explanation"]):
                return question_data
        except Exception:
            pass
        
        # Fallback (in English if AI fails)
        fallbacks = {
            "Class 1-2": {"question": "2 + 3 = ?", "options": ["4", "5", "6", "7"], "answer": "5", "explanation": "2 + 3 = 5"},
            "Class 3-5": {"question": "7 x 8 = ?", "options": ["48", "56", "64", "72"], "answer": "56", "explanation": "7 x 8 = 56"},
            "Class 6-8": {"question": "If 2x + 5 = 15, what is x?", "options": ["5", "10", "15", "20"], "answer": "5", "explanation": "2x = 10, x = 5"},
            "Class 9-10": {"question": "sin(90°) = ?", "options": ["0", "0.5", "1", "Undefined"], "answer": "1", "explanation": "sin(90°) = 1"},
            "Class 11-12": {"question": "Derivative of x²?", "options": ["x", "2x", "x³", "2"], "answer": "2x", "explanation": "d/dx(x²) = 2x"},
            "University": {"question": "RSA: p=3, q=11, n=?", "options": ["14", "33", "44", "22"], "answer": "33", "explanation": "n = p*q = 33"}
        }
        return fallbacks.get(class_level, fallbacks["Class 6-8"])

    if st.session_state.math_current_question is None:
        with st.spinner("Generating..." if not is_junior else "🎲 नया सवाल बन रहा है..."):
            st.session_state.math_current_question = generate_math_question(class_level, is_junior, selected_lang_label)
            st.session_state.math_game_answered = False

    q = st.session_state.math_current_question

    # ============================================================
    # 6. QUESTION DISPLAY & SUBMISSION
    # ============================================================
    st.markdown(f'<div class="question-card"><div class="question-text">{q["question"]}</div></div>', unsafe_allow_html=True)

    selected_option = st.radio("Choose:", q["options"], key=f"math_opt_{st.session_state.math_game_q_id}", label_visibility="collapsed")

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if not st.session_state.math_game_answered:
            if st.button(f"✅ {t['submit']}", use_container_width=True, type="primary"):
                st.session_state.math_game_answered = True
                if selected_option == q["answer"]:
                    st.session_state.math_game_score += 10
                    st.session_state.math_game_streak += 1
                    if is_junior: st.balloons()
                else:
                    st.session_state.math_game_streak = 0
                st.rerun()

    # ============================================================
    # 7. FEEDBACK & NEXT
    # ============================================================
    if st.session_state.math_game_answered:
        if selected_option == q["answer"]:
            st.markdown(f'<div class="feedback-success">✅ {t["correct"]} +10</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="feedback-error">❌ {t["wrong"]} {q["answer"]}</div>', unsafe_allow_html=True)
        
        st.info(f"💡 **{t['explain']}** {q['explanation']}")
        
        with col_btn2:
            if st.button(f"➡️ {t['next']}", use_container_width=True, type="primary"):
                st.session_state.math_current_question = None
                st.session_state.math_game_answered = False
                st.session_state.math_game_q_id += 1
                st.rerun()

    st.divider()
    if st.button(f"🔄 {t['reset']}", use_container_width=True):
        st.session_state.math_game_score = 0
        st.session_state.math_game_streak = 0
        st.session_state.math_current_question = None
        st.session_state.math_game_answered = False
        st.session_state.math_game_q_id += 1
        st.rerun()   
        
    
def render_kids_logic_lab():
    # ============================================================
    # Imports अब फंक्शन के अंदर हैं (ताकि कोई conflict न हो)
    # ============================================================
    import streamlit as st
    import streamlit.components.v1 as components

    # ============================================================
    # यह पूरा HTML/JS गेम Streamlit के अंदर एम्बेड किया जा रहा है
    # ============================================================
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Clyxess Global Kids Logic & AI Puzzle Lab</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 min-h-screen p-3 md:p-6 font-sans">

        <!-- Header -->
        <header class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center bg-slate-900 border border-slate-800 p-4 rounded-2xl mb-6 gap-4 shadow-xl">
            <div class="flex items-center space-x-3">
                <div class="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400">
                    <i class="fa-solid fa-earth-americas text-2xl"></i>
                </div>
                <div>
                    <h1 class="text-xl font-bold text-white tracking-wide">Clyxess <span class="text-emerald-400">Global AI School</span></h1>
                    <p class="text-xs text-slate-400">Interactive Logic, Engineering & Multi-Language Playground</p>
                </div>
            </div>

            <div class="flex flex-wrap items-center gap-3">
                <!-- Language Selector -->
                <div class="flex items-center space-x-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-700">
                    <i class="fa-solid fa-language text-amber-400 text-sm"></i>
                    <select id="languageSelect" onchange="changeLanguage()" class="bg-transparent text-amber-400 text-xs font-bold focus:outline-none cursor-pointer">
                        <option value="en" selected>English (US/UK)</option>
                        <option value="hi">हिंदी (Hindi)</option>
                        <option value="bn">বাংলা (Bengali)</option>
                        <option value="ta">தமிழ் (Tamil)</option>
                        <option value="te">తెలుగు (Telugu)</option>
                        <option value="mr">मराठी (Marathi)</option>
                        <option value="es">Español (Spanish)</option>
                        <option value="fr">Français (French)</option>
                    </select>
                </div>

                <!-- Class Filter -->
                <select id="ageFilter" onchange="filterGamesByAge()" class="bg-slate-950 text-emerald-400 text-xs font-bold border border-emerald-500/40 rounded-xl px-3 py-2 focus:outline-none cursor-pointer">
                    <option value="group1">Class 1-2 (5-7 Yrs) • Visual Puzzles</option>
                    <option value="group2">Class 3-5 (8-10 Yrs) • Science & Machines</option>
                    <option value="group3">Class 6-7 (11-13 Yrs) • Advanced Engineering</option>
                </select>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            <!-- Left Panel: Puzzle Selection -->
            <div class="bg-slate-900 border border-slate-800 rounded-3xl p-5 space-y-4">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <h2 id="lblDashboard" class="text-xs font-bold text-slate-300 uppercase tracking-wider"><i class="fa-solid fa-gamepad text-emerald-400 mr-2"></i> Puzzles Dashboard</h2>
                    <span id="completedBadge" class="bg-emerald-500/10 text-emerald-400 text-xs px-2.5 py-1 rounded-full border border-emerald-500/20 font-bold">Unlocked: 1/15</span>
                </div>

                <div>
                    <label id="lblSelectGame" class="text-xs text-slate-400 block mb-1">Select Puzzle Game:</label>
                    <select id="gameSelectDropdown" onchange="loadSelectedGame()" class="w-full bg-slate-950 text-white text-xs border border-slate-700 rounded-xl p-3 focus:outline-none focus:border-emerald-400 cursor-pointer font-bold"></select>
                </div>

                <div id="gameListContainer" class="space-y-2 max-h-[360px] overflow-y-auto pr-1"></div>
            </div>

            <!-- Right Panel: Puzzle Workspace -->
            <div class="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-3xl p-6 flex flex-col justify-between relative overflow-hidden">
                <div>
                    <div class="flex justify-between items-center mb-4 border-b border-slate-800 pb-3">
                        <div>
                            <span id="puzzleCategoryTag" class="text-[10px] uppercase font-bold tracking-widest px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">Cartoon Puzzle</span>
                            <h3 id="puzzleTitle" class="text-base font-bold text-white mt-1">Solve The Cute Cat Puzzle</h3>
                        </div>
                        <div id="statusIcon" class="text-amber-400 text-xs font-bold bg-amber-500/10 border border-amber-500/20 px-3 py-1 rounded-xl flex items-center gap-1.5">
                            <i class="fa-solid fa-hourglass-start"></i> In Progress
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
                        <div class="bg-slate-950 border border-slate-800 rounded-2xl p-4">
                            <h4 id="lblToolbox" class="text-xs font-bold text-slate-400 mb-3 uppercase tracking-wider"><i class="fa-solid fa-toolbox mr-1 text-emerald-400"></i> Available Blocks</h4>
                            <div id="availableBlocks" class="space-y-2"></div>
                        </div>

                        <div class="bg-slate-950 border border-emerald-500/30 rounded-2xl p-4">
                            <h4 id="lblAssembly" class="text-xs font-bold text-emerald-400 mb-3 uppercase tracking-wider"><i class="fa-solid fa-layer-group mr-1"></i> Assembly Sequence</h4>
                            <div id="assemblyZone" class="space-y-2 min-h-[140px] border-2 border-dashed border-slate-800 rounded-xl p-2 flex flex-col justify-center items-center">
                                <p class="text-xs text-slate-500 italic">Click blocks to assemble here</p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-slate-950 border border-slate-800 rounded-2xl p-4 text-center relative overflow-hidden min-h-[160px] flex flex-col items-center justify-center">
                        <div id="visualDisplay" class="transition-all duration-500">
                            <i class="fa-solid fa-puzzle-piece text-5xl text-slate-700 animate-pulse"></i>
                            <p class="text-xs text-slate-500 mt-2">Arrange blocks correctly & press 'Assemble'</p>
                        </div>
                    </div>
                </div>

                <div class="flex justify-between items-center mt-6 pt-4 border-t border-slate-800">
                    <button id="btnClear" onclick="resetCurrentPuzzle()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl transition"><i class="fa-solid fa-rotate-left mr-1"></i> Clear Blocks</button>
                    <button id="btnAssemble" onclick="checkPuzzleSolution()" class="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-xl shadow-lg shadow-emerald-500/20 transition flex items-center gap-2 uppercase tracking-wider">
                        <i class="fa-solid fa-play"></i> Assemble & Run
                    </button>
                </div>
            </div>
        </main>

        <!-- Toy Counting Section -->
        <section class="max-w-6xl mx-auto mt-6 bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-4 mb-4 gap-4">
                <div>
                    <h3 id="toyTitle" class="text-sm font-bold text-white flex items-center gap-2"><span class="text-lg">🚗</span> Toy & Fruit Counting (Small Kids)</h3>
                    <p id="toyDesc" class="text-xs text-slate-400">Count the toys and type the correct number</p>
                </div>
                <select id="toyDropdown" onchange="loadToyGame()" class="bg-slate-950 text-amber-400 text-xs font-bold border border-amber-500/30 rounded-xl p-2 focus:outline-none cursor-pointer">
                    <option value="cars">1. Count the Cars 🚗</option>
                    <option value="apples">2. Count the Apples 🍎</option>
                    <option value="balls">3. Count the Balls ⚽</option>
                </select>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                <div class="md:col-span-2 bg-slate-950 border border-slate-800 p-6 rounded-2xl flex items-center justify-center text-4xl">
                    <div id="toyVisualBox" class="flex flex-wrap items-center justify-center gap-2"></div>
                </div>
                <div class="bg-slate-950 border border-slate-800 p-4 rounded-2xl flex flex-col space-y-2">
                    <input type="number" id="toyAnswerInput" placeholder="Total items?" class="bg-slate-900 text-white font-bold text-center text-sm border border-slate-700 rounded-xl p-2 focus:outline-none">
                    <button id="btnCheckToy" onclick="verifyToyAnswer()" class="w-full py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-xl transition">Check Answer</button>
                    <p id="toyResultText" class="text-xs text-center font-bold h-4"></p>
                </div>
            </div>
        </section>

        <!-- Math Wizard Section -->
        <section class="max-w-6xl mx-auto mt-6 bg-slate-900 border border-slate-800 rounded-3xl p-6">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-4 mb-4 gap-4">
                <div>
                    <h3 id="mathWizTitle" class="text-sm font-bold text-white flex items-center gap-2"><span class="text-lg">🧙‍♂️</span> Math Wizard Challenge (Class 1-10)</h3>
                    <p id="mathWizDesc" class="text-xs text-slate-400">Solve the equation before time runs out!</p>
                </div>
                <div class="flex gap-2">
                    <select id="mathDifficulty" onchange="generateMathQuiz()" class="bg-slate-950 text-emerald-400 text-xs font-bold border border-emerald-500/30 rounded-xl p-2 focus:outline-none cursor-pointer">
                        <option value="easy">Level 1: Addition & Subtraction (Class 1-3)</option>
                        <option value="medium">Level 2: Multiplication & Division (Class 4-7)</option>
                        <option value="hard">Level 3: Algebra & Fractions (Class 8-10)</option>
                    </select>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                <div class="md:col-span-2 bg-slate-950 border border-slate-800 p-6 rounded-2xl flex items-center justify-center text-3xl font-mono text-emerald-400">
                    <div id="mathWizVisualBox" class="flex items-center space-x-3"></div>
                </div>
                <div class="bg-slate-950 border border-slate-800 p-4 rounded-2xl flex flex-col space-y-2">
                    <input type="text" id="mathWizAnswerInput" placeholder="Your Answer?" class="bg-slate-900 text-white font-bold text-center text-sm border border-slate-700 rounded-xl p-2 focus:outline-none">
                    <button id="btnCheckMath" onclick="verifyMathWizAnswer()" class="w-full py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-xl transition">Submit</button>
                    <p id="mathWizResultText" class="text-xs text-center font-bold h-4"></p>
                </div>
            </div>
        </section>

        <!-- JavaScript Engine -->
        <script>
            // --- Translation Dictionary (UI & Game Titles) ---
            const translations = {
                "en": {
                    dashboard: "Puzzles Dashboard", selectGame: "Select Puzzle Game:", availableBlocks: "Available Blocks",
                    assemblySeq: "Assembly Sequence", clearBlocks: "Clear Blocks", assembleRun: "Assemble & Run",
                    toyTitle: "Toy & Fruit Counting", toyDesc: "Count the toys and type the correct number",
                    mathWizTitle: "Math Wizard Challenge", mathWizDesc: "Solve the equation before time runs out!",
                    checkAns: "Check Answer", submit: "Submit", totalItems: "Total items?", yourAns: "Your Answer?",
                    games: {
                        1: { title: "Solve Cute Cat Puzzle", cat: "Cartoon Puzzle", blocks: ["Fix Ears & Whiskers", "Draw Cat Face", "Attach Tail"], sol: ["Draw Cat Face", "Fix Ears & Whiskers", "Attach Tail"] },
                        2: { title: "Solve Puppy Dog Puzzle", cat: "Cartoon Puzzle", blocks: ["Attach Bark Sound", "Add Paws", "Fix Puppy Body"], sol: ["Fix Puppy Body", "Add Paws", "Attach Bark Sound"] },
                        3: { title: "Solve Magic Star Puzzle", cat: "Cartoon Puzzle", blocks: ["Add Neon Glow", "Draw 5 Points", "Sparkle Effect"], sol: ["Draw 5 Points", "Add Neon Glow", "Sparkle Effect"] },
                        4: { title: "Solve Helicopter Assembly", cat: "Engineering Puzzle", blocks: ["Attach Main Rotor", "Mount Cockpit Glass", "Fix Tail Propeller"], sol: ["Mount Cockpit Glass", "Attach Main Rotor", "Fix Tail Propeller"] },
                        5: { title: "Solve Racing Car Puzzle", cat: "Engineering Puzzle", blocks: ["Fit 4 Wheels", "Attach Chassis Frame", "Install Engine"], sol: ["Attach Chassis Frame", "Install Engine", "Fit 4 Wheels"] },
                        6: { title: "Solve Aeroplane Jet Logic", cat: "Engineering Puzzle", blocks: ["Calibrate Jet Turbines", "Attach Wings", "Deploy Landing Gear"], sol: ["Attach Wings", "Calibrate Jet Turbines", "Deploy Landing Gear"] },
                        7: { title: "Solve Rocket Launch Sequence", cat: "Engineering Puzzle", blocks: ["Ignite Boosters", "Fill Fuel Tanks", "Countdown 3..2..1"], sol: ["Fill Fuel Tanks", "Countdown 3..2..1", "Ignite Boosters"] },
                        8: { title: "Solve Train Engine Mechanics", cat: "Engineering Puzzle", blocks: ["Connect Electric Pantograph", "Couple Steam Engine", "Signal Green Light"], sol: ["Couple Steam Engine", "Connect Electric Pantograph", "Signal Green Light"] },
                        9: { title: "Solve Submarine Depth Control", cat: "Engineering Puzzle", blocks: ["Seal Oxygen Valves", "Fill Ballast Tanks", "Sonar Pulse Check"], sol: ["Seal Oxygen Valves", "Fill Ballast Tanks", "Sonar Pulse Check"] },
                        10: { title: "Solve Windmill Power Generator", cat: "Engineering Puzzle", blocks: ["Connect Turbine Shaft", "Fix 3 Large Blades", "Store Electricity in Battery"], sol: ["Fix 3 Large Blades", "Connect Turbine Shaft", "Store Electricity in Battery"] },
                        11: { title: "Solve Smart Drone Navigation", cat: "Engineering Puzzle", blocks: ["Calibrate Flight Gyroscope", "Connect 4 Brushless Motors", "Link GPS & Camera"], sol: ["Connect 4 Brushless Motors", "Calibrate Flight Gyroscope", "Link GPS & Camera"] },
                        12: { title: "Solve Industrial Robot Arm", cat: "Engineering Puzzle", blocks: ["Connect Servo Motors", "Program Hydraulic Gripper", "Calibrate Motion Sensor"], sol: ["Connect Servo Motors", "Calibrate Motion Sensor", "Program Hydraulic Gripper"] },
                        13: { title: "Solve EV Battery & Motor Setup", cat: "Engineering Puzzle", blocks: ["Connect Lithium Cells", "Attach Regenerative Brakes", "Configure Motor Inverter"], sol: ["Connect Lithium Cells", "Configure Motor Inverter", "Attach Regenerative Brakes"] },
                        14: { title: "Solve Space Satellite Solar Array", cat: "Engineering Puzzle", blocks: ["Deploy Solar Panels", "Orient Thrusters to Orbit", "Establish Radio Telemetry"], sol: ["Deploy Solar Panels", "Establish Radio Telemetry", "Orient Thrusters to Orbit"] },
                        15: { title: "Solve Hydraulic Crane Lift", cat: "Engineering Puzzle", blocks: ["Pressurize Fluid Pumps", "Extend Telescopic Boom", "Engage Counterweights"], sol: ["Engage Counterweights", "Pressurize Fluid Pumps", "Extend Telescopic Boom"] }
                    }
                },
                "hi": {
                    dashboard: "पहेली डैशबोर्ड", selectGame: "पहेली गेम चुनें:", availableBlocks: "उपलब्ध ब्लॉक्स",
                    assemblySeq: "असेंबली क्रम", clearBlocks: "ब्लॉक्स साफ़ करें", assembleRun: "असेंबल और चलाएं",
                    toyTitle: "खिलौने और फल गिनना", toyDesc: "खिलौनों को गिनें और सही संख्या लिखें",
                    mathWizTitle: "गणित जादूगर चुनौती", mathWizDesc: "समीकरण हल करें!",
                    checkAns: "उत्तर जांचें", submit: "जमा करें", totalItems: "कुल वस्तुएं?", yourAns: "आपका उत्तर?",
                    games: {
                        1: { title: "प्यारी बिल्ली की पहेली", cat: "कार्टून पहेली", blocks: ["कान और मूंछें ठीक करें", "बिल्ली का चेहरा बनाएं", "पूंछ जोड़ें"], sol: ["बिल्ली का चेहरा बनाएं", "कान और मूंछें ठीक करें", "पूंछ जोड़ें"] },
                        2: { title: "पिल्ला कुत्ता पहेली", cat: "कार्टून पहेली", blocks: ["भौंकने की आवाज जोड़ें", "पंजे जोड़ें", "पिल्ला शरीर ठीक करें"], sol: ["पिल्ला शरीर ठीक करें", "पंजे जोड़ें", "भौंकने की आवाज जोड़ें"] },
                        3: { title: "जादुई सितारा पहेली", cat: "कार्टून पहेली", blocks: ["नियॉन चमक जोड़ें", "5 अंक बनाएं", "स्पार्कल प्रभाव"], sol: ["5 अंक बनाएं", "नियॉन चमक जोड़ें", "स्पार्कल प्रभाव"] },
                        4: { title: "हेलीकॉप्टर असेंबली", cat: "इंजीनियरिंग पहेली", blocks: ["मुख्य रोटर संलग्न करें", "कॉकपिट ग्लास माउंट करें", "टेल प्रोपेलर ठीक करें"], sol: ["कॉकपिट ग्लास माउंट करें", "मुख्य रोटर संलग्न करें", "टेल प्रोपेलर ठीक करें"] },
                        5: { title: "रेसिंग कार पहेली", cat: "इंजीनियरिंग पहेली", blocks: ["4 पहिये फिट करें", "चेसिस फ्रेम संलग्न करें", "इंजन स्थापित करें"], sol: ["चेसिस फ्रेम संलग्न करें", "इंजन स्थापित करें", "4 पहिये फिट करें"] },
                        6: { title: "एयरोप्लेन जेट लॉजिक", cat: "इंजीनियरिंग पहेली", blocks: ["जेट टर्बाइन कैलिब्रेट करें", "पंख संलग्न करें", "लैंडिंग गियर तैनात करें"], sol: ["पंख संलग्न करें", "जेट टर्बाइन कैलिब्रेट करें", "लैंडिंग गियर तैनात करें"] },
                        7: { title: "रॉकेट लॉन्च अनुक्रम", cat: "इंजीनियरिंग पहेली", blocks: ["बूस्टर प्रज्वलित करें", "ईंधन टैंक भरें", "उलटी गिनती 3..2..1"], sol: ["ईंधन टैंक भरें", "उलटी गिनती 3..2..1", "बूस्टर प्रज्वलित करें"] },
                        8: { title: "ट्रेन इंजन मैकेनिक्स", cat: "इंजीनियरिंग पहेली", blocks: ["इलेक्ट्रिक पैंटोग्राफ कनेक्ट करें", "स्टीम इंजन कपल करें", "हरी बत्ती का संकेत दें"], sol: ["स्टीम इंजन कपल करें", "इलेक्ट्रिक पैंटोग्राफ कनेक्ट करें", "हरी बत्ती का संकेत दें"] },
                        9: { title: "पनडुब्बी गहराई नियंत्रण", cat: "इंजीनियरिंग पहेली", blocks: ["ऑक्सीजन वाल्व सील करें", "बैलास्ट टैंक भरें", "सोनार पल्स जांच"], sol: ["ऑक्सीजन वाल्व सील करें", "बैलास्ट टैंक भरें", "सोनार पल्स जांच"] },
                        10: { title: "पवनचक्की बिजली जनरेटर", cat: "इंजीनियरिंग पहेली", blocks: ["टर्बाइन शाफ्ट कनेक्ट करें", "3 बड़े ब्लेड ठीक करें", "बैटरी में बिजली स्टोर करें"], sol: ["3 बड़े ब्लेड ठीक करें", "टर्बाइन शाफ्ट कनेक्ट करें", "बैटरी में बिजली स्टोर करें"] },
                        11: { title: "स्मार्ट ड्रोन नेविगेशन", cat: "इंजीनियरिंग पहेली", blocks: ["फ्लाइट जायरोस्कोप कैलिब्रेट करें", "4 ब्रशलेस मोटर्स कनेक्ट करें", "जीपीएस और कैमरा लिंक करें"], sol: ["4 ब्रशलेस मोटर्स कनेक्ट करें", "फ्लाइट जायरोस्कोप कैलिब्रेट करें", "जीपीएस और कैमरा लिंक करें"] },
                        12: { title: "औद्योगिक रोबोट आर्म", cat: "इंजीनियरिंग पहेली", blocks: ["सर्वो मोटर्स कनेक्ट करें", "हाइड्रोलिक ग्रिपर प्रोग्राम करें", "मोशन सेंसर कैलिब्रेट करें"], sol: ["सर्वो मोटर्स कनेक्ट करें", "मोशन सेंसर कैलिब्रेट करें", "हाइड्रोलिक ग्रिपर प्रोग्राम करें"] },
                        13: { title: "ईवी बैटरी और मोटर सेटअप", cat: "इंजीनियरिंग पहेली", blocks: ["लिथियम सेल कनेक्ट करें", "रिजनरेटिव ब्रेक्स संलग्न करें", "मोटर इनवर्टर कॉन्फ़िगर करें"], sol: ["लिथियम सेल कनेक्ट करें", "मोटर इनवर्टर कॉन्फ़िगर करें", "रिजनरेटिव ब्रेक्स संलग्न करें"] },
                        14: { title: "अंतरिक्ष उपग्रह सौर सरणी", cat: "इंजीनियरिंग पहेली", blocks: ["सौर पैनल तैनात करें", "थ्रस्टर्स को कक्षा में उन्मुख करें", "रेडियो टेलीमेट्री स्थापित करें"], sol: ["सौर पैनल तैनात करें", "रेडियो टेलीमेट्री स्थापित करें", "थ्रस्टर्स को कक्षा में उन्मुख करें"] },
                        15: { title: "हाइड्रोलिक क्रेन लिफ्ट", cat: "इंजीनियरिंग पहेली", blocks: ["फ्लूड पंप प्रेशराइज़ करें", "टेलीस्कोपिक बूम बढ़ाएं", "काउंटरवेट संलग्न करें"], sol: ["काउंटरवेट संलग्न करें", "फ्लूड पंप प्रेशराइज़ करें", "टेलीस्कोपिक बूम बढ़ाएं"] }
                    }
                },
                "bn": {
                    dashboard: "ধাঁধা ড্যাশবোর্ড", selectGame: "ধাঁধা খেলা নির্বাচন করুন:", availableBlocks: "উপলব্ধ ব্লক",
                    assemblySeq: "সমাবেশ ক্রম", clearBlocks: "ব্লক সাফ করুন", assembleRun: "একত্রিত করুন এবং চালান",
                    toyTitle: "খেলনা এবং ফল গণনা", toyDesc: "খেলনা গণনা করুন এবং সঠিক সংখ্যা লিখুন",
                    mathWizTitle: "গণিত উইজার্ড চ্যালেঞ্জ", mathWizDesc: "সমীকরণ সমাধান করুন!",
                    checkAns: "উত্তর চেক করুন", submit: "জমা দিন", totalItems: "মোট আইটেম?", yourAns: "আপনার উত্তর?",
                    games: { 1: { title: "কিউট ক্যাট ধাঁধা সমাধান করুন", cat: "কার্টুন ধাঁধা", blocks: ["কান এবং গোঁফ ঠিক করুন", "বিড়ালের মুখ আঁকুন", "লেজ সংযুক্ত করুন"], sol: ["বিড়ালের মুখ আঁকুন", "কান এবং গোঁফ ঠিক করুন", "লেজ সংযুক্ত করুন"] } }
                },
                "ta": {
                    dashboard: "புதிர் டாஷ்போர்டு", selectGame: "புதிர் விளையாட்டைத் தேர்ந்தெடுக்கவும்:", availableBlocks: "கிடைக்கக்கூடிய தொகுதிகள்",
                    assemblySeq: "சட்டசபை வரிசை", clearBlocks: "தொகுதிகளை அழிக்கவும்", assembleRun: "சட்டசபை & இயக்கு",
                    toyTitle: "பொம்மை & பழம் எண்ணுதல்", toyDesc: "பொம்மைகளை எண்ணி சரியான எண்ணை உள்ளிடவும்",
                    mathWizTitle: "கணித வizard சவால்", mathWizDesc: "சமன்பாட்டை தீர்க்கவும்!",
                    checkAns: "பதிலை சரிபார்க்கவும்", submit: "சமர்ப்பிக்கவும்", totalItems: "மொத்த பொருட்கள்?", yourAns: "உங்கள் பதில்?",
                    games: { 1: { title: "அழகான பூனை புதிர்", cat: "கார்ட்டூன் புதிர்", blocks: ["காதுகள் & மீசையை சரிசெய்", "பூனை முகத்தை வரை", "வாலை இணைக்கவும்"], sol: ["பூனை முகத்தை வரை", "காதுகள் & மீசையை சரிசெய்", "வாலை இணைக்கவும்"] } }
                },
                "te": {
                    dashboard: "పజిల్ డాష్‌బోర్డ్", selectGame: "పజిల్ గేమ్‌ను ఎంచుకోండి:", availableBlocks: "అందుబాటులో ఉన్న బ్లాక్‌లు",
                    assemblySeq: "అసెంబ్లీ సీక్వెన్స్", clearBlocks: "బ్లాక్‌లను క్లియర్ చేయండి", assembleRun: "అసెంబుల్ & రన్",
                    toyTitle: "బొమ్మలు & పండ్ల లెక్కింపు", toyDesc: "బొమ్మలను లెక్కించి సరైన సంఖ్యను నమోదు చేయండి",
                    mathWizTitle: "మ్యాథ్ విజార్డ్ ఛాలెంజ్", mathWizDesc: "సమీకరణాన్ని పరిష్కరించండి!",
                    checkAns: "సమాధానం తనిఖీ చేయండి", submit: "సమర్పించండి", totalItems: "మొత్తం వస్తువులు?", yourAns: "మీ సమాధానం?",
                    games: { 1: { title: "క్యూట్ క్యాట్ పజిల్", cat: "కార్టూన్ పజిల్", blocks: ["చెవులు & వేస్కర్స్ సరిచేయండి", "పిల్లి ముఖం గీయండి", "తోకను జోడించండి"], sol: ["పిల్లి ముఖం గీయండి", "చెవులు & వేస్కర్స్ సరిచేయండి", "తోకను జోడించండి"] } }
                },
                "mr": {
                    dashboard: "कोडे डॅशबोर्ड", selectGame: "कोडे गेम निवडा:", availableBlocks: "उपलब्ध ब्लॉक्स",
                    assemblySeq: "असेंबली क्रम", clearBlocks: "ब्लॉक्स साफ करा", assembleRun: "असेंबल आणि चालवा",
                    toyTitle: "खेळणी आणि फळे मोजणे", toyDesc: "खेळणी मोजा आणि योग्य संख्या लिहा",
                    mathWizTitle: "गणित विझार्ड चॅलेंज", mathWizDesc: "समीकरण सोडवा!",
                    checkAns: "उत्तर तपासा", submit: "सबमिट करा", totalItems: "एकूण वस्तू?", yourAns: "तुमचे उत्तर?",
                    games: { 1: { title: "क्यूट कॅट कोडे", cat: "कार्टून कोडे", blocks: ["कान आणि मिशा दुरुस्त करा", "मांजरीचा चेहरा काढा", "शेपूट जोडा"], sol: ["मांजरीचा चेहरा काढा", "कान आणि मिशा दुरुस्त करा", "शेपूट जोडा"] } }
                },
                "es": { dashboard: "Panel de Rompecabezas", selectGame: "Seleccionar Juego:", availableBlocks: "Bloques Disponibles", assemblySeq: "Secuencia de Ensamblaje", clearBlocks: "Limpiar Bloques", assembleRun: "Ensamblar y Ejecutar", toyTitle: "Conteo de Juguetes", toyDesc: "Cuenta los juguetes y escribe el número", mathWizTitle: "Desafío Matemático", mathWizDesc: "¡Resuelve la ecuación!", checkAns: "Verificar", submit: "Enviar", totalItems: "¿Total?", yourAns: "Tu respuesta?", games: {} },
                "fr": { dashboard: "Tableau de Bord", selectGame: "Choisir le Jeu:", availableBlocks: "Blocs Disponibles", assemblySeq: "Séquence d'Assemblage", clearBlocks: "Effacer les Blocs", assembleRun: "Assembler & Exécuter", toyTitle: "Compter les Jouets", toyDesc: "Comptez les jouets et tapez le nombre", mathWizTitle: "Défi Mathématique", mathWizDesc: "Résolvez l'équation!", checkAns: "Vérifier", submit: "Soumettre", totalItems: "Total?", yourAns: "Votre réponse?", games: {} }
            };

            let currentLang = "en";
            let activeGameId = 1;
            let selectedSequence = [];
            let currentMathAnswer = 5;
            let currentToyAnswer = 0;
            let currentMathWizAnswer = 0;

            const toyEmojis = { cars: "🚗", apples: "🍎", balls: "⚽" };

            // ============================================================
            // TRANSLATION HELPERS
            // ============================================================
            function t(key, fallback="") {
                const langData = translations[currentLang] || translations["en"];
                return langData[key] || translations["en"][key] || fallback;
            }

            function getGameData(id) {
                const langData = translations[currentLang] || translations["en"];
                return (langData.games && langData.games[id]) || translations["en"].games[id];
            }

            // ============================================================
            // GAME DATA (IDs only, text comes from translations)
            // ============================================================
            const gamesMeta = [
                { id: 1, group: "group1", icon: "fa-cat text-pink-400", locked: false },
                { id: 2, group: "group1", icon: "fa-dog text-amber-400", locked: true },
                { id: 3, group: "group1", icon: "fa-star text-yellow-400", locked: true },
                { id: 4, group: "group1", icon: "fa-helicopter text-cyan-400", locked: true },
                { id: 5, group: "group1", icon: "fa-car-side text-emerald-400", locked: true },
                { id: 6, group: "group2", icon: "fa-plane-departure text-sky-400", locked: true },
                { id: 7, group: "group2", icon: "fa-rocket text-red-400", locked: true },
                { id: 8, group: "group2", icon: "fa-train text-indigo-400", locked: true },
                { id: 9, group: "group2", icon: "fa-ship text-blue-400", locked: true },
                { id: 10, group: "group2", icon: "fa-wind text-teal-400", locked: true },
                { id: 11, group: "group3", icon: "fa-paper-plane text-purple-400", locked: true },
                { id: 12, group: "group3", icon: "fa-robot text-emerald-400", locked: true },
                { id: 13, group: "group3", icon: "fa-bolt text-yellow-400", locked: true },
                { id: 14, group: "group3", icon: "fa-satellite text-cyan-400", locked: true },
                { id: 15, group: "group3", icon: "fa-truck-pickup text-amber-400", locked: true }
            ];

            // ============================================================
            // INITIALIZATION
            // ============================================================
            window.onload = function() {
                changeLanguage(); // Sets up UI text
                filterGamesByAge();
                loadMathPuzzle();
                loadToyGame();
                generateMathQuiz();
            };

            function changeLanguage() {
                currentLang = document.getElementById('languageSelect').value;
                
                // Update UI Labels
                document.getElementById('lblDashboard').innerHTML = `<i class="fa-solid fa-gamepad text-emerald-400 mr-2"></i> ${t('dashboard')}`;
                document.getElementById('lblSelectGame').innerText = t('selectGame');
                document.getElementById('lblToolbox').innerHTML = `<i class="fa-solid fa-toolbox mr-1 text-emerald-400"></i> ${t('availableBlocks')}`;
                document.getElementById('lblAssembly').innerHTML = `<i class="fa-solid fa-layer-group mr-1"></i> ${t('assemblySeq')}`;
                document.getElementById('btnClear').innerHTML = `<i class="fa-solid fa-rotate-left mr-1"></i> ${t('clearBlocks')}`;
                document.getElementById('btnAssemble').innerHTML = `<i class="fa-solid fa-play"></i> ${t('assembleRun')}`;
                
                // Update New Game Titles
                document.getElementById('toyTitle').innerHTML = `<span class="text-lg">🚗</span> ${t('toyTitle')}`;
                document.getElementById('toyDesc').innerText = t('toyDesc');
                document.getElementById('btnCheckToy').innerText = t('checkAns');
                document.getElementById('toyAnswerInput').placeholder = t('totalItems');

                document.getElementById('mathWizTitle').innerHTML = `<span class="text-lg">🧙‍♂️</span> ${t('mathWizTitle')}`;
                document.getElementById('mathWizDesc').innerText = t('mathWizDesc');
                document.getElementById('btnCheckMath').innerText = t('submit');
                document.getElementById('mathWizAnswerInput').placeholder = t('yourAns');

                // Refresh game list to apply translated titles
                filterGamesByAge();
            }

            // ============================================================
            // PUZZLE LOGIC
            // ============================================================
            function filterGamesByAge() {
                const group = document.getElementById('ageFilter').value;
                const dropdown = document.getElementById('gameSelectDropdown');
                const listContainer = document.getElementById('gameListContainer');
                
                dropdown.innerHTML = '';
                listContainer.innerHTML = '';

                const filteredGames = gamesMeta.filter(g => g.group === group);

                filteredGames.forEach(meta => {
                    const gameData = getGameData(meta.id);
                    const opt = document.createElement('option');
                    opt.value = meta.id;
                    opt.disabled = meta.locked;
                    opt.innerText = `${meta.locked ? '🔒' : '✅'} ${gameData.title}`;
                    dropdown.appendChild(opt);

                    const item = document.createElement('div');
                    item.className = `p-3 rounded-xl border flex justify-between items-center cursor-pointer transition ${meta.id === activeGameId ? 'bg-slate-800 border-emerald-400' : 'bg-slate-950 border-slate-800'}`;
                    item.onclick = () => { if(!meta.locked) { activeGameId = meta.id; dropdown.value = meta.id; loadSelectedGame(); } };
                    
                    item.innerHTML = `
                        <div class="flex items-center space-x-3">
                            <i class="fa-solid ${meta.icon} text-base"></i>
                            <span class="text-xs font-bold ${meta.locked ? 'text-slate-500' : 'text-slate-200'}">${gameData.title}</span>
                        </div>
                        ${meta.locked ? '<i class="fa-solid fa-lock text-slate-600 text-xs"></i>' : '<i class="fa-solid fa-circle-check text-emerald-400 text-xs"></i>'}
                    `;
                    listContainer.appendChild(item);
                });

                const firstAvailable = filteredGames.find(g => !g.locked) || filteredGames[0];
                activeGameId = firstAvailable.id;
                dropdown.value = activeGameId;
                loadSelectedGame();
            }

            function loadSelectedGame() {
                const dropdownVal = parseInt(document.getElementById('gameSelectDropdown').value);
                activeGameId = dropdownVal;
                const meta = gamesMeta.find(g => g.id === activeGameId);
                const gameData = getGameData(activeGameId);

                document.getElementById('puzzleTitle').innerText = gameData.title;
                document.getElementById('puzzleCategoryTag').innerText = gameData.cat;
                
                document.getElementById('statusIcon').className = "text-amber-400 text-xs font-bold bg-amber-500/10 border border-amber-500/20 px-3 py-1 rounded-xl flex items-center gap-1.5";
                document.getElementById('statusIcon').innerHTML = '<i class="fa-solid fa-hourglass-start"></i> In Progress';

                resetCurrentPuzzle();

                const blocksContainer = document.getElementById('availableBlocks');
                blocksContainer.innerHTML = '';
                
                let shuffled = [...gameData.blocks].sort(() => 0.5 - Math.random());
                shuffled.forEach(blockText => {
                    const b = document.createElement('div');
                    b.className = "p-2 bg-slate-900 border border-slate-700 hover:border-emerald-400 rounded-xl text-xs font-semibold text-slate-200 cursor-pointer transition flex items-center justify-between";
                    b.innerHTML = `<span>${blockText}</span> <i class="fa-solid fa-plus text-slate-500 text-[10px]"></i>`;
                    b.onclick = () => addToAssembly(blockText, b);
                    blocksContainer.appendChild(b);
                });

                const solvedCount = gamesMeta.filter(g => !g.locked).length;
                document.getElementById('completedBadge').innerText = `Unlocked: ${solvedCount}/${gamesMeta.length}`;
            }

            function addToAssembly(text, element) {
                if(!selectedSequence.includes(text)) {
                    selectedSequence.push(text);
                    element.classList.add('opacity-40', 'pointer-events-none');
                    renderAssemblyZone();
                }
            }

            function renderAssemblyZone() {
                const zone = document.getElementById('assemblyZone');
                zone.innerHTML = '';
                
                if(selectedSequence.length === 0) {
                    zone.innerHTML = `<p class="text-xs text-slate-500 italic">${t('selectGame')} ...</p>`;
                    return;
                }

                selectedSequence.forEach((text, index) => {
                    const item = document.createElement('div');
                    // FIX: Added cursor-pointer, hover effect, and onclick to remove
                    item.className = "w-full p-2 bg-emerald-500/10 border border-emerald-500/40 rounded-xl text-xs font-bold text-emerald-400 flex justify-between items-center cursor-pointer hover:bg-rose-500/20 hover:border-rose-500 hover:text-rose-400 transition";
                    item.onclick = () => removeFromAssembly(text);
                    item.innerHTML = `<span>${index + 1}. ${text}</span> <i class="fa-solid fa-xmark text-[10px]"></i>`;
                    zone.appendChild(item);
                });
            }

            // FIX: New function to remove block
            function removeFromAssembly(text) {
                selectedSequence = selectedSequence.filter(t => t !== text);
                renderAssemblyZone();
                
                const blocks = document.getElementById('availableBlocks').children;
                for(let b of blocks) {
                    if(b.innerText.includes(text)) {
                        b.classList.remove('opacity-40', 'pointer-events-none');
                    }
                }
            }

            function resetCurrentPuzzle() {
                selectedSequence = [];
                renderAssemblyZone();
                document.getElementById('visualDisplay').innerHTML = `
                    <i class="fa-solid fa-puzzle-piece text-5xl text-slate-700 animate-pulse"></i>
                    <p class="text-xs text-slate-500 mt-2">${t('assembleRun')}</p>
                `;
                
                const blocks = document.getElementById('availableBlocks').children;
                for(let b of blocks) {
                    b.classList.remove('opacity-40', 'pointer-events-none');
                }
            }

            function checkPuzzleSolution() {
                const gameData = getGameData(activeGameId);
                const isCorrect = JSON.stringify(selectedSequence) === JSON.stringify(gameData.sol);

                const display = document.getElementById('visualDisplay');
                const status = document.getElementById('statusIcon');

                if(isCorrect) {
                    confetti({ particleCount: 130, spread: 85, origin: { y: 0.6 } });
                    status.className = "text-emerald-400 text-xs font-bold bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-xl flex items-center gap-1.5";
                    status.innerHTML = '<i class="fa-solid fa-circle-check"></i> Puzzle Solved!';

                    const currentIndex = gamesMeta.findIndex(g => g.id === activeGameId);
                    let nextGameTitle = "";
                    
                    if(currentIndex + 1 < gamesMeta.length) {
                        gamesMeta[currentIndex + 1].locked = false;
                        nextGameTitle = getGameData(gamesMeta[currentIndex + 1].id).title;
                    }

                    display.innerHTML = `
                        <div class="text-emerald-400 animate-bounce">
                            <i class="fa-solid ${gamesMeta.find(g=>g.id===activeGameId).icon} text-6xl"></i>
                        </div>
                        <h4 class="text-base font-bold text-amber-400 mt-2">🎉 Correct!</h4>
                        <p class="text-xs font-bold text-emerald-400 mt-1">Next: ${nextGameTitle || "All Completed!"}</p>
                    `;

                    setTimeout(() => { filterGamesByAge(); }, 2200);
                } else {
                    status.className = "text-rose-400 text-xs font-bold bg-rose-500/10 border border-rose-500/30 px-3 py-1 rounded-xl flex items-center gap-1.5";
                    status.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Wrong Sequence';

                    display.innerHTML = `
                        <i class="fa-solid fa-bug text-5xl text-rose-500"></i>
                        <p class="text-xs text-rose-400 mt-2 font-bold">Assembly Failed! Try again.</p>
                    `;
                }
            }

            // ============================================================
            // TOY COUNTING LOGIC (NEW)
            // ============================================================
            function loadToyGame() {
                const type = document.getElementById('toyDropdown').value;
                const box = document.getElementById('toyVisualBox');
                const emoji = toyEmojis[type];
                
                const count = Math.floor(Math.random() * 10) + 1;
                currentToyAnswer = count;
                
                box.innerHTML = emoji.repeat(count);
                document.getElementById('toyAnswerInput').value = '';
                document.getElementById('toyResultText').innerText = '';
            }

            function verifyToyAnswer() {
                const userAns = parseInt(document.getElementById('toyAnswerInput').value);
                const res = document.getElementById('toyResultText');

                if(userAns === currentToyAnswer) {
                    confetti({ particleCount: 40, spread: 40, origin: { y: 0.8 } });
                    res.className = "text-xs text-center font-bold text-emerald-400";
                    res.innerText = "🌟 Correct!";
                    setTimeout(loadToyGame, 1500);
                } else {
                    res.className = "text-xs text-center font-bold text-rose-400";
                    res.innerText = "❌ Count again!";
                }
            }

            // ============================================================
            // MATH WIZARD LOGIC (NEW)
            // ============================================================
            function generateMathQuiz() {
                const level = document.getElementById('mathDifficulty').value;
                const box = document.getElementById('mathWizVisualBox');
                let questionText = "";
                let answer = 0;

                if (level === "easy") {
                    const a = Math.floor(Math.random() * 20) + 1;
                    const b = Math.floor(Math.random() * 20) + 1;
                    const isAdd = Math.random() > 0.5;
                    if (isAdd) { questionText = `${a} + ${b} = ?`; answer = a + b; }
                    else { questionText = `${Math.max(a,b)} - ${Math.min(a,b)} = ?`; answer = Math.max(a,b) - Math.min(a,b); }
                } else if (level === "medium") {
                    const a = Math.floor(Math.random() * 12) + 2;
                    const b = Math.floor(Math.random() * 12) + 2;
                    const isMul = Math.random() > 0.5;
                    if (isMul) { questionText = `${a} × ${b} = ?`; answer = a * b; }
                    else { questionText = `${a*b} ÷ ${a} = ?`; answer = b; }
                } else if (level === "hard") {
                    const a = Math.floor(Math.random() * 5) + 2;
                    const x = Math.floor(Math.random() * 10) + 1;
                    const b = Math.floor(Math.random() * 20);
                    const c = (a * x) + b;
                    questionText = `${a}x + ${b} = ${c}. Find x.`;
                    answer = x;
                }

                box.innerHTML = `<span>${questionText}</span>`;
                currentMathWizAnswer = answer;
                document.getElementById('mathWizAnswerInput').value = '';
                document.getElementById('mathWizResultText').innerText = '';
            }

            function verifyMathWizAnswer() {
                const userAns = parseFloat(document.getElementById('mathWizAnswerInput').value);
                const res = document.getElementById('mathWizResultText');
                
                if (isNaN(userAns)) {
                    res.className = "text-xs text-center font-bold text-amber-400";
                    res.innerText = "Please enter a valid number!";
                    return;
                }

                if(Math.abs(userAns - currentMathWizAnswer) < 0.01) {
                    confetti({ particleCount: 60, spread: 60, origin: { y: 0.8 } });
                    res.className = "text-xs text-center font-bold text-emerald-400";
                    res.innerText = "🌟 Brilliant!";
                    setTimeout(generateMathQuiz, 1500);
                } else {
                    res.className = "text-xs text-center font-bold text-rose-400";
                    res.innerText = `❌ Correct ans: ${currentMathWizAnswer}`;
                }
            }

            // --- Math Fruit Logic (Old) ---
            function loadMathPuzzle() {
                const val = document.getElementById('mathDropdown').value;
                const box = document.getElementById('mathVisualBox');
                document.getElementById('mathAnswerInput').value = '';
                document.getElementById('mathResultText').innerText = '';

                if(val === 'm1') { currentMathAnswer = 5; box.innerHTML = '<span>🥭🥭🥭</span> <span class="text-amber-400 font-bold">+</span> <span>🥭🥭</span> <span class="text-amber-400 font-bold">=</span> <span>❓</span>'; }
                else if(val === 'm2') { currentMathAnswer = 3; box.innerHTML = '<span>🥭🥭🥭🥭🥭🥭</span> <span class="text-rose-400 font-bold">-</span> <span>🥭🥭🥭</span> <span class="text-amber-400 font-bold">=</span> <span>❓</span>'; }
                else if(val === 'm3') { currentMathAnswer = 8; box.innerHTML = '<span>(🥭🥭🥭🥭)</span> <span class="text-amber-400 font-bold">x 2</span> <span class="text-amber-400 font-bold">=</span> <span>❓</span>'; }
            }

            function verifyMathAnswer() {
                const userAns = parseInt(document.getElementById('mathAnswerInput').value);
                const res = document.getElementById('mathResultText');

                if(userAns === currentMathAnswer) {
                    confetti({ particleCount: 50, spread: 50, origin: { y: 0.8 } });
                    res.className = "text-xs text-center font-bold text-emerald-400";
                    res.innerText = "🌟 Correct!";
                } else {
                    res.className = "text-xs text-center font-bold text-rose-400";
                    res.innerText = "❌ Try again!";
                }
            }
        </script>
    </body>
    </html>
    """
    
    # Streamlit में HTML को रेंडर करना
    components.html(HTML_TEMPLATE, height=1200, scrolling=True)
# 🤖 CLYXESSCHAT AI — LEARN AI
# FINAL ADVANCED GLOBAL EDITION
# AGE 5 → UNIVERSITY
#
# Features:
# • Age adaptive AI teaching
# • School + College + University
# • AI Fundamentals
# • Machine Learning
# • Deep Learning
# • Generative AI
# • Prompt Engineering
# • AI Agents
# • Multimodal AI
# • Computer Vision
# • NLP
# • Neural Networks
# • AI Ethics & Safety
# • Open Source Models
# • RAG
# • Fine-tuning Concepts
# • AI Engineering
# • AI Research
# • Adaptive Practice
# • AI Quiz
# • Challenges
# • Project Builder
# • AI System Designer
# • Progress / XP / Mastery
# ============================================================

def render_learn_ai(client):

    import streamlit as st
    import json
    import re
    import time

    # ========================================================
    # SESSION STATE
    # ========================================================

    state_defaults = {

        "ai_teacher_messages": [],
        "ai_selected_topic": "",
        "ai_xp": 0,

        "ai_completed_topics": [],
        "ai_mastery": {},

        "ai_quiz_data": [],
        "ai_quiz_index": 0,
        "ai_quiz_score": 0,
        "ai_quiz_running": False,

        "ai_practice_question": "",
        "ai_practice_answer": "",
        "ai_practice_result": "",

        "ai_project_result": "",
        "ai_builder_result": "",

        "ai_last_level": "",

    }

    for key, value in state_defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value

    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(
        """
        <div style="
            padding:25px;
            border-radius:20px;
            background:
            linear-gradient(
                135deg,
                #07152f,
                #111c48,
                #29105c
            );
            border:1px solid rgba(100,180,255,0.35);
            margin-bottom:20px;
        ">

            <h1 style="
                color:white;
                margin:0;
                font-size:32px;
            ">
                🤖 Learn AI
            </h1>

            <p style="
                color:#b8d8ff;
                font-size:16px;
                margin-top:8px;
            ">
                Clyxess AI School — Age 5 to University
            </p>

            <p style="
                color:#8ea9cc;
                font-size:14px;
                margin-bottom:0;
            ">
                Learn → Practice → Build → Test → Master
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ========================================================
    # AGE / LEVEL
    # ========================================================

    age_level = st.selectbox(

        "🎓 Student Age / Education Level",

        [

            "Age 5-6 — Early Explorer",
            "Age 7-8 — Young Explorer",
            "Age 9-10 — Young Builder",
            "Age 11-12 — AI Explorer",
            "Age 13-15 — AI Builder",
            "Age 16-18 — Advanced AI",
            "College — Undergraduate",
            "University — Advanced / Research"

        ],

        key="learn_ai_age_level"
    )

    # ========================================================
    # LEVEL ENGINE
    # ========================================================

    level_config = {

        "Age 5-6 — Early Explorer": {

            "difficulty": "Very Easy",
            "style": "Stories, pictures, games, simple examples",
            "math": False,
            "coding": False,

            "topics": [

                "What is AI?",
                "AI Around Me",
                "Smart Machines",
                "Patterns",
                "Images and Recognition",
                "Voice Assistants",
                "Robots",
                "Generative AI Basics",
                "AI Safety",
                "AI Creativity"

            ]
        },

        "Age 7-8 — Young Explorer": {

            "difficulty": "Easy",
            "style": "Stories + examples + simple activities",
            "math": False,
            "coding": "Optional",

            "topics": [

                "Artificial Intelligence",
                "Data",
                "Patterns",
                "Machine Learning Basics",
                "Computer Vision",
                "Speech AI",
                "Generative AI",
                "Prompt Basics",
                "AI Bias",
                "AI Safety",
                "Build a Simple AI Idea"

            ]
        },

        "Age 9-10 — Young Builder": {

            "difficulty": "Beginner",
            "style": "Examples + activities + beginner logic",
            "math": "Basic",
            "coding": "Beginner",

            "topics": [

                "AI Fundamentals",
                "Data and Datasets",
                "Machine Learning",
                "Classification",
                "Computer Vision",
                "NLP Basics",
                "Generative AI",
                "Prompt Engineering",
                "AI Agents Introduction",
                "Neural Network Basics",
                "AI Ethics",
                "AI Project"

            ]
        },

        "Age 11-12 — AI Explorer": {

            "difficulty": "Intermediate",
            "style": "Concepts + experiments + beginner coding",
            "math": "Basic",
            "coding": "Python / Block Coding",

            "topics": [

                "AI Fundamentals",
                "Machine Learning",
                "Training Data",
                "Supervised Learning",
                "Unsupervised Learning",
                "Classification",
                "Regression",
                "Neural Networks",
                "Computer Vision",
                "NLP",
                "Generative AI",
                "Prompt Engineering",
                "AI Agents",
                "AI Ethics",
                "AI Project"

            ]
        },

        "Age 13-15 — AI Builder": {

            "difficulty": "Intermediate-Advanced",
            "style": "Technical concepts + coding + projects",
            "math": "Intermediate",
            "coding": "Python",

            "topics": [

                "Machine Learning",
                "Datasets",
                "Data Preprocessing",
                "Regression",
                "Classification",
                "Clustering",
                "Neural Networks",
                "Deep Learning",
                "CNN",
                "Computer Vision",
                "NLP",
                "Transformers Basics",
                "Generative AI",
                "Prompt Engineering",
                "AI Agents",
                "RAG Introduction",
                "AI Safety",
                "AI Project"

            ]
        },

        "Age 16-18 — Advanced AI": {

            "difficulty": "Advanced",
            "style": "Technical + mathematical + engineering",
            "math": "Advanced",
            "coding": "Python",

            "topics": [

                "Machine Learning",
                "Probability for AI",
                "Statistics for AI",
                "Linear Algebra Basics",
                "Data Preprocessing",
                "Feature Engineering",
                "Regression",
                "Classification",
                "Clustering",
                "Neural Networks",
                "Deep Learning",
                "CNN",
                "RNN",
                "Transformers",
                "Computer Vision",
                "NLP",
                "LLMs",
                "Generative AI",
                "Prompt Engineering",
                "RAG",
                "AI Agents",
                "Multimodal AI",
                "Model Evaluation",
                "AI Ethics",
                "AI Research Project"

            ]
        },

        "College — Undergraduate": {

            "difficulty": "Advanced",
            "style": "Engineering + mathematics + implementation",
            "math": "Advanced",
            "coding": "Python / ML",

            "topics": [

                "AI Foundations",
                "Probability",
                "Statistics",
                "Linear Algebra",
                "Calculus for ML",
                "Optimization",
                "Machine Learning",
                "Supervised Learning",
                "Unsupervised Learning",
                "Reinforcement Learning",
                "Feature Engineering",
                "Model Selection",
                "Neural Networks",
                "Deep Learning",
                "CNN",
                "RNN",
                "Transformers",
                "Attention Mechanism",
                "NLP",
                "Computer Vision",
                "Generative AI",
                "LLMs",
                "Prompt Engineering",
                "Embeddings",
                "Vector Databases",
                "RAG",
                "AI Agents",
                "Multimodal AI",
                "Model Evaluation",
                "MLOps",
                "AI Security",
                "AI Ethics",
                "AI Project"

            ]
        },

        "University — Advanced / Research": {

            "difficulty": "Research / Expert",
            "style": "Research + engineering + mathematical depth",
            "math": "Advanced",
            "coding": "Advanced",

            "topics": [

                "Advanced Machine Learning",
                "Statistical Learning Theory",
                "Optimization",
                "Linear Algebra",
                "Probability",
                "Deep Learning",
                "CNN Architectures",
                "Sequence Models",
                "Attention",
                "Transformers",
                "Large Language Models",
                "Tokenization",
                "Embeddings",
                "Vector Search",
                "RAG",
                "AI Agents",
                "Agentic Systems",
                "Multimodal AI",
                "Computer Vision",
                "NLP",
                "Reinforcement Learning",
                "Fine-Tuning",
                "Parameter Efficient Fine-Tuning",
                "Open Source Models",
                "Model Evaluation",
                "AI Safety",
                "AI Alignment",
                "AI Security",
                "MLOps",
                "AI System Architecture",
                "Research Methodology",
                "AI Research Project"

            ]
        }

    }

    config = level_config[age_level]

    topics = config["topics"]

    # ========================================================
    # CURRENT LEVEL CHANGE RESET
    # ========================================================

    if st.session_state.ai_last_level != age_level:

        st.session_state.ai_last_level = age_level

        st.session_state.ai_teacher_messages = []

    # ========================================================
    # PROGRESS
    # ========================================================

    completed_count = len(
        st.session_state.ai_completed_topics
    )

    xp = st.session_state.ai_xp

    topic_count = len(topics)

    progress = min(
        completed_count / topic_count,
        1
    ) if topic_count else 0

    # ========================================================
    # TOP METRICS
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "⭐ XP",
            xp
        )

    with c2:
        st.metric(
            "📚 Topics",
            topic_count
        )

    with c3:
        st.metric(
            "✅ Completed",
            completed_count
        )

    with c4:
        st.metric(
            "🎓 Level",
            config["difficulty"]
        )

    st.progress(progress)

    # ========================================================
    # TABS
    # ========================================================

    (
        tab_path,
        tab_teacher,
        tab_practice,
        tab_quiz,
        tab_agent,
        tab_project,
        tab_ethics,
        tab_progress

    ) = st.tabs(

        [

            "🗺️ Learning Path",
            "👨‍🏫 AI Teacher",
            "🧪 Practice",
            "📝 Assessment",
            "🤖 Agent Builder",
            "🛠️ Project Lab",
            "🔐 AI Ethics",
            "📊 Progress"

        ]

    )

    # ========================================================
    # TAB 1
    # LEARNING PATH
    # ========================================================

    with tab_path:

        st.subheader(
            "🗺️ Personal AI Learning Path"
        )

        st.write(
            f"""
            **Level:** {age_level}

            **Teaching style:** {config["style"]}

            **Difficulty:** {config["difficulty"]}
            """
        )

        st.divider()

        st.markdown(
            """
            ### 🧠 Clyxess Learning Method

            **1. Understand**

            Concept ko simple language mein samjho.

            **2. See**

            Real-world example dekho.

            **3. Try**

            Khud answer ya activity karo.

            **4. Challenge**

            AI tumhe challenge dega.

            **5. Build**

            Concept ko project mein use karo.

            **6. Test**

            Quiz aur practical assessment.

            **7. Master**

            Weak topics dobara practice.

            **8. Create**

            Apna project banao.
            """
        )

        st.divider()

        for index, topic in enumerate(topics):

            topic_id = (
                f"{age_level}::{topic}"
            )

            completed = (
                topic_id
                in st.session_state.ai_completed_topics
            )

            mastery = st.session_state.ai_mastery.get(
                topic_id,
                0
            )

            col1, col2, col3 = st.columns(
                [0.6, 5, 1.5]
            )

            with col1:

                if completed:
                    st.write("✅")

                else:
                    st.write(
                        f"**{index + 1}**"
                    )

            with col2:

                st.write(
                    f"**{topic}**"
                )

                st.progress(
                    min(mastery / 100, 1)
                )

            with col3:

                if st.button(
                    "Learn",
                    key=f"topic_learn_{index}_{age_level}"
                ):

                    st.session_state.ai_selected_topic = topic

                    st.session_state.ai_teacher_messages = []

                    st.rerun()

    # ========================================================
    # TAB 2
    # AI TEACHER
    # ========================================================

    with tab_teacher:

        st.subheader(
            "👨‍🏫 Personal AI Teacher"
        )

        selected_topic = (
            st.session_state.ai_selected_topic
        )

        if selected_topic:

            st.success(
                f"🎯 Current Topic: {selected_topic}"
            )

        else:

            st.info(
                "Learning Path se topic select karo "
                "ya directly question pucho."
            )

        # ----------------------------------------------------
        # QUICK TOPICS
        # ----------------------------------------------------

        st.write(
            "### ⚡ Quick Start"
        )

        quick_topics = [

            "AI kya hai?",
            "Machine Learning",
            "Neural Network",
            "Generative AI",
            "Prompt Engineering",
            "AI Agents",
            "Computer Vision",
            "NLP",
            "RAG",
            "Multimodal AI"

        ]

        quick_cols = st.columns(5)

        selected_quick = None

        for i, topic in enumerate(
            quick_topics
        ):

            with quick_cols[i % 5]:

                if st.button(
                    topic,
                    key=f"quick_topic_{i}_{age_level}"
                ):

                    selected_quick = topic

        # ----------------------------------------------------
        # CHAT HISTORY
        # ----------------------------------------------------

        for msg in st.session_state.ai_teacher_messages:

            with st.chat_message(
                msg["role"]
            ):

                st.markdown(
                    msg["content"]
                )

        user_input = st.chat_input(
            "AI ke baare mein kuch bhi pucho..."
        )

        if selected_quick:

            user_input = selected_quick

        # ----------------------------------------------------
        # TEACHING ENGINE
        # ----------------------------------------------------

        if user_input:

            st.session_state.ai_teacher_messages.append(
                {
                    "role": "user",
                    "content": user_input
                }
            )

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    user_input
                )

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "🤖 Personal AI Teacher soch raha hai..."
                ):

                    teacher_prompt = f"""

You are Clyxess AI School's Personal AI Teacher.

============================================================
STUDENT
============================================================

Education level:
{age_level}

Difficulty:
{config["difficulty"]}

Teaching style:
{config["style"]}

Current topic:
{selected_topic or "General AI"}

============================================================
MISSION
============================================================

Teach the student according to their real developmental
and educational level.

The same AI system must successfully teach:

• Age 5
• Age 6
• Age 7
• Age 8
• Age 9
• Age 10
• Age 11
• Age 12
• Age 13
• Age 14
• Age 15
• Age 16
• Age 17
• Age 18
• College
• University
• Advanced researchers

Never give every learner the same explanation.

============================================================
AGE 5-6
============================================================

Use:

• very simple words
• stories
• toys
• animals
• colors
• family examples
• games
• imagination

Avoid:

• complicated mathematics
• technical jargon
• long explanations
• advanced code

Teach ideas such as:

AI can recognize patterns.
Machines can follow instructions.
Computers can learn from examples.

============================================================
AGE 7-8
============================================================

Use:

• simple explanations
• everyday technology
• mini activities
• pattern games
• visual thinking

Introduce:

• data
• patterns
• machine learning
• robots
• computer vision
• generative AI

============================================================
AGE 9-10
============================================================

Introduce:

• datasets
• classification
• basic algorithms
• computer vision
• NLP
• prompts
• neural networks

Use beginner coding only when useful.

============================================================
AGE 11-12
============================================================

Introduce:

• Python
• machine learning
• training data
• supervised learning
• regression
• classification
• neural networks
• generative AI
• AI agents

============================================================
AGE 13-15
============================================================

Use:

• Python
• algorithms
• datasets
• model training
• neural networks
• deep learning
• CNN
• NLP
• transformers
• AI agents
• RAG

============================================================
AGE 16-18
============================================================

Use:

• mathematical intuition
• probability
• statistics
• vectors
• optimization
• ML pipelines
• deep learning
• transformers
• LLMs
• RAG
• agents
• evaluation

============================================================
COLLEGE
============================================================

Teach:

• mathematics for AI
• ML algorithms
• deep learning
• optimization
• CNN
• RNN
• transformers
• embeddings
• vector databases
• RAG
• agents
• multimodal AI
• MLOps
• deployment
• evaluation

Use technical terminology and implementation thinking.

============================================================
UNIVERSITY / RESEARCH
============================================================

Teach deeply:

• statistical learning
• optimization
• representation learning
• attention
• transformers
• LLM architecture
• embeddings
• retrieval
• RAG
• agentic systems
• multimodal models
• fine-tuning concepts
• PEFT
• open-source models
• reinforcement learning
• model evaluation
• safety
• alignment
• AI security
• MLOps
• research methodology

When mathematics is useful, explain the intuition
and then the mathematics.

============================================================
TEACHING RULES
============================================================

Never simply dump information.

Use:

CONCEPT
↓
REAL WORLD EXAMPLE
↓
SIMPLE EXPLANATION
↓
STUDENT QUESTION
↓
PRACTICE
↓
FEEDBACK
↓
CHALLENGE
↓
MASTERY

If the student is solving a problem:

DO NOT immediately give the final answer.

Use:

Hint 1
↓
Guiding question
↓
Hint 2
↓
Small example
↓
Student attempt
↓
Feedback

Only reveal the full solution when appropriate.

============================================================
AI AGENTS
============================================================

Explain agent systems as:

GOAL
↓
PLAN
↓
MEMORY
↓
TOOLS
↓
ACTION
↓
OBSERVATION
↓
REFLECTION
↓
NEXT ACTION

For advanced students explain:

• tool calling
• orchestration
• planning
• memory
• retrieval
• evaluation
• guardrails
• human approval

============================================================
GENERATIVE AI
============================================================

Explain according to level:

• prompts
• tokens
• context
• generation
• embeddings
• transformers
• LLMs
• multimodal models
• limitations

============================================================
ETHICS
============================================================

Teach:

• privacy
• bias
• fairness
• misinformation
• hallucination
• copyright
• security
• responsible AI
• human oversight

============================================================
IMPORTANT
============================================================

Never pretend AI output is guaranteed correct.

Encourage verification.

Never make the student dependent on the AI.

The goal is:

UNDERSTAND
THINK
SOLVE
CREATE
BECOME INDEPENDENT

Use the student's language naturally.

If student uses Hindi/Hinglish:
reply in Hindi/Hinglish.

If student uses English:
reply in English.

Keep response length appropriate to age.

"""

                    messages = [

                        {
                            "role": "system",
                            "content": teacher_prompt
                        }

                    ]

                    messages.extend(
                        st.session_state.ai_teacher_messages[-10:]
                    )

                    try:

                        completion = client.chat.completions.create(

                            model="llama-3.3-70b-versatile",

                            messages=messages,

                            temperature=0.65,

                            max_tokens=2200

                        )

                        reply = (
                            completion
                            .choices[0]
                            .message
                            .content
                        )

                    except Exception:

                        reply = (
                            "⚠️ AI Teacher abhi available nahi hai. "
                            "Please thodi der baad try karo."
                        )

                    st.markdown(
                        reply
                    )

                    st.session_state.ai_teacher_messages.append(
                        {
                            "role": "assistant",
                            "content": reply
                        }
                    )

    # ========================================================
    # TAB 3
    # ADAPTIVE PRACTICE
    # ========================================================

    with tab_practice:

        st.subheader(
            "🧪 Adaptive AI Practice"
        )

        practice_topic = st.selectbox(

            "📚 Topic",

            topics,

            key="adaptive_practice_topic"

        )

        difficulty = st.select_slider(

            "🎯 Difficulty",

            [

                "Very Easy",
                "Easy",
                "Medium",
                "Hard",
                "Expert"

            ],

            value="Medium",

            key="adaptive_difficulty"

        )

        if st.button(
            "🎯 Generate Challenge",
            key="generate_adaptive_challenge"
        ):

            prompt = f"""

Create one adaptive learning challenge.

Student:
{age_level}

Topic:
{practice_topic}

Difficulty:
{difficulty}

Rules:

• Age appropriate
• Test understanding
• Real-world context
• Do not immediately reveal answer
• Give one small hint
• Encourage independent thinking

Format:

🎯 CHALLENGE

💡 HINT

🧠 WHAT TO THINK ABOUT

"""

            try:

                result = client.chat.completions.create(

                    model="llama-3.3-70b-versatile",

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.7,
                    max_tokens=1200

                )

                st.session_state.ai_practice_question = (
                    result.choices[0]
                    .message
                    .content
                )

                st.session_state.ai_practice_result = ""

            except:

                st.error(
                    "Challenge generate nahi ho paya."
                )

        if st.session_state.ai_practice_question:

            st.markdown(
                st.session_state.ai_practice_question
            )

            answer = st.text_area(
                "✍️ Apna solution likho",
                key="adaptive_answer"
            )

            if st.button(
                "🔍 Check My Answer",
                key="check_adaptive_answer"
            ):

                if not answer.strip():

                    st.warning(
                        "Pehle apna answer likho."
                    )

                else:

                    evaluation = f"""

You are an educational evaluator.

Student:
{age_level}

Topic:
{practice_topic}

Challenge:
{st.session_state.ai_practice_question}

Student answer:
{answer}

Evaluate:

1. Concept understanding
2. Reasoning
3. Correct parts
4. Mistakes
5. One useful hint
6. Correct explanation
7. Next difficulty recommendation

Do not humiliate the student.

Encourage independent thinking.

"""

                    with st.spinner(
                        "🧠 Answer analyse ho raha hai..."
                    ):

                        try:

                            result = client.chat.completions.create(

                                model="llama-3.3-70b-versatile",

                                messages=[
                                    {
                                        "role": "user",
                                        "content": evaluation
                                    }
                                ],

                                temperature=0.35,
                                max_tokens=1800

                            )

                            feedback = (
                                result.choices[0]
                                .message
                                .content
                            )

                            st.session_state.ai_practice_result = feedback

                            st.markdown(
                                feedback
                            )

                            st.session_state.ai_xp += 10

                        except:

                            st.error(
                                "Answer evaluation failed."
                            )

    # ========================================================
    # TAB 4
    # ASSESSMENT
    # ========================================================

    with tab_quiz:

        st.subheader(
            "📝 AI Assessment Engine"
        )

        quiz_topic = st.selectbox(

            "Quiz Topic",

            topics,

            key="advanced_quiz_topic"

        )

        quiz_size = st.slider(

            "Questions",

            5,
            15,
            5,

            key="advanced_quiz_size"

        )

        quiz_level = st.selectbox(

            "Difficulty",

            [
                "Easy",
                "Medium",
                "Hard",
                "Expert"
            ],

            key="advanced_quiz_level"

        )

        if st.button(
            "🚀 Generate Assessment",
            key="advanced_generate_quiz"
        ):

            quiz_prompt = f"""

Create {quiz_size} MCQ questions.

Student:
{age_level}

Topic:
{quiz_topic}

Difficulty:
{quiz_level}

Return ONLY valid JSON.

Format:

[
  {{
    "question": "Question",
    "options": [
      "Option 1",
      "Option 2",
      "Option 3",
      "Option 4"
    ],
    "answer": "Option 1",
    "explanation": "Short explanation"
  }}
]

Rules:

• Exactly 4 options
• answer must exactly match one option
• Test understanding
• Age appropriate
• No ambiguous questions
• No trick questions
• Use Hinglish unless English is more appropriate

"""

            with st.spinner(
                "🤖 AI assessment prepare kar raha hai..."
            ):

                try:

                    result = client.chat.completions.create(

                        model="llama-3.3-70b-versatile",

                        messages=[
                            {
                                "role": "user",
                                "content": quiz_prompt
                            }
                        ],

                        temperature=0.35,

                        max_tokens=5000

                    )

                    raw = (
                        result
                        .choices[0]
                        .message
                        .content
                        .strip()
                    )

                    match = re.search(
                        r"\[[\s\S]*\]",
                        raw
                    )

                    if not match:

                        raise ValueError(
                            "Invalid quiz JSON"
                        )

                    quiz = json.loads(
                        match.group(0)
                    )

                    valid_questions = []

                    for question in quiz:

                        if not isinstance(
                            question,
                            dict
                        ):
                            continue

                        options = question.get(
                            "options",
                            []
                        )

                        answer = question.get(
                            "answer",
                            ""
                        )

                        if (
                            isinstance(options, list)
                            and len(options) == 4
                            and answer in options
                        ):

                            valid_questions.append(
                                question
                            )

                    if not valid_questions:

                        raise ValueError(
                            "No valid questions"
                        )

                    st.session_state.ai_quiz_data = (
                        valid_questions
                    )

                    st.session_state.ai_quiz_index = 0
                    st.session_state.ai_quiz_score = 0
                    st.session_state.ai_quiz_running = True

                    st.rerun()

                except Exception:

                    st.error(
                        "Quiz generate nahi ho paya. Dobara try karo."
                    )

        # ----------------------------------------------------
        # QUIZ RUNNER
        # ----------------------------------------------------

        if st.session_state.ai_quiz_running:

            quiz = st.session_state.ai_quiz_data

            index = st.session_state.ai_quiz_index

            if index < len(quiz):

                question = quiz[index]

                st.progress(
                    index / len(quiz)
                )

                st.write(
                    f"### Q{index + 1}/{len(quiz)}"
                )

                st.markdown(
                    f"**{question['question']}**"
                )

                selected = st.radio(

                    "Choose answer:",

                    question["options"],

                    key=f"ai_assessment_{index}"

                )

                if st.button(
                    "✅ Submit Answer",
                    key=f"submit_ai_assessment_{index}"
                ):

                    if selected == question["answer"]:

                        st.success(
                            "🎉 Correct!"
                        )

                        st.session_state.ai_quiz_score += 1

                        st.session_state.ai_xp += 20

                    else:

                        st.error(
                            "❌ Incorrect"
                        )

                    st.info(
                        "💡 "
                        + question.get(
                            "explanation",
                            "Concept ko dobara review karo."
                        )
                    )

                    st.session_state.ai_quiz_index += 1

                    time.sleep(0.25)

                    st.rerun()

            else:

                total = len(quiz)

                score = (
                    st.session_state.ai_quiz_score
                )

                percentage = (
                    score / total * 100
                    if total
                    else 0
                )

                st.balloons()

                st.success(
                    f"🏆 Assessment Complete: {score}/{total}"
                )

                st.metric(
                    "Accuracy",
                    f"{percentage:.0f}%"
                )

                if percentage >= 85:

                    st.success(
                        "🔥 Strong mastery — next difficulty unlock kar sakte ho."
                    )

                elif percentage >= 60:

                    st.info(
                        "👍 Good progress — thodi practice aur karo."
                    )

                else:

                    st.warning(
                        "📚 Weak concepts ko Learning Path se dobara practice karo."
                    )

                if st.button(
                    "🔄 New Assessment",
                    key="new_ai_assessment"
                ):

                    st.session_state.ai_quiz_data = []
                    st.session_state.ai_quiz_index = 0
                    st.session_state.ai_quiz_score = 0
                    st.session_state.ai_quiz_running = False

                    st.rerun()

    # ========================================================
    # TAB 5
    # AI AGENT BUILDER
    # ========================================================

    with tab_agent:

        st.subheader(
            "🤖 AI Agent Builder"
        )

        st.write(
            "Student apna AI Agent design karega."
        )

        agent_type = st.selectbox(

            "Agent Type",

            [

                "AI Study Assistant",
                "Weather Agent",
                "Agriculture Agent",
                "Research Agent",
                "Coding Agent",
                "Language Agent",
                "Business Assistant",
                "Personal Productivity Agent",
                "Custom Agent"

            ],

            key="agent_type"

        )

        agent_goal = st.text_area(

            "🎯 Agent ka goal kya hai?",

            placeholder=(
                "Example: Farmers ko weather information "
                "samajhne mein help karna."
            ),

            key="agent_goal"

        )

        if st.button(
            "🚀 Design My AI Agent",
            key="design_agent"
        ):

            agent_prompt = f"""

You are an AI Agent Engineering Teacher.

Student:
{age_level}

Agent:
{agent_type}

Goal:
{agent_goal or "Create an educational example."}

Create an age-appropriate AI Agent design.

Explain:

1. Agent Name
2. Problem
3. User
4. Goal
5. Inputs
6. Knowledge
7. Memory
8. Tools
9. Planning
10. Actions
11. Observation
12. Feedback
13. Safety
14. Human Approval
15. Testing
16. Future Improvements

Architecture:

USER
↓
GOAL
↓
PLANNER
↓
MEMORY / KNOWLEDGE
↓
TOOLS
↓
ACTION
↓
OBSERVATION
↓
EVALUATION
↓
NEXT ACTION

For young children explain this with a simple story.

For teenagers explain the architecture.

For college/university include:

• APIs
• tool calling
• retrieval
• embeddings
• vector database
• orchestration
• evaluation
• guardrails
• deployment

Do not claim the agent has actually been deployed.

"""

            with st.spinner(
                "🤖 Agent architecture design ho raha hai..."
            ):

                try:

                    result = client.chat.completions.create(

                        model="llama-3.3-70b-versatile",

                        messages=[
                            {
                                "role": "user",
                                "content": agent_prompt
                            }
                        ],

                        temperature=0.55,
                        max_tokens=3000

                    )

                    output = (
                        result.choices[0]
                        .message
                        .content
                    )

                    st.session_state.ai_builder_result = output

                    st.markdown(
                        output
                    )

                    st.session_state.ai_xp += 30

                except:

                    st.error(
                        "Agent design generate nahi ho paya."
                    )

    # ========================================================
    # TAB 6
    # PROJECT LAB
    # ========================================================

    with tab_project:

        st.subheader(
            "🛠️ AI Project Lab"
        )

        project_area = st.selectbox(

            "🌍 Project Area",

            [

                "Education",
                "Agriculture",
                "Space",
                "Healthcare",
                "Environment",
                "Finance",
                "Robotics",
                "Languages",
                "Games",
                "Business",
                "Cyber Safety",
                "Social Impact"

            ],

            key="ai_project_area"

        )

        project_type = st.selectbox(

            "🚀 Project Level",

            [

                "Fun Project",
                "School Project",
                "Science Fair",
                "Real World Project",
                "Advanced Project",
                "College Project",
                "University Research Project"

            ],

            key="ai_project_type"

        )

        project_problem = st.text_area(

            "💡 Problem you want to solve",

            placeholder=(
                "Example: Students ko difficult concepts "
                "samjhane ke liye AI tutor banana."
            ),

            key="ai_project_problem"

        )

        if st.button(
            "🚀 Build My Project Plan",
            key="build_ai_project"
        ):

            project_prompt = f"""

You are a senior AI project mentor.

Student:
{age_level}

Project level:
{project_type}

Area:
{project_area}

Problem:
{project_problem or "Create a suitable project."}

Create a complete educational AI project.

Include:

# PROJECT NAME

# PROBLEM

# WHY IT MATTERS

# WHAT STUDENT WILL BUILD

# CONCEPTS

# DATA

# TOOLS

# ARCHITECTURE

# STEP 1

# STEP 2

# STEP 3

# STEP 4

# STEP 5

# TESTING

# EXPECTED RESULT

# COMMON ERRORS

# SAFETY

# SKILLS LEARNED

# ADVANCED VERSION

For Age 5-8:
Use games, visual activities and no-code ideas.

For Age 9-12:
Use beginner coding and simple AI concepts.

For Age 13-18:
Use Python, datasets and real AI concepts.

For College:
Use implementation, APIs and model evaluation.

For University:
Include research methodology, experiments,
baselines, metrics and deployment/research direction.

Never claim the project is already built.

"""

            with st.spinner(
                "🛠️ Project architecture ban rahi hai..."
            ):

                try:

                    result = client.chat.completions.create(

                        model="llama-3.3-70b-versatile",

                        messages=[
                            {
                                "role": "user",
                                "content": project_prompt
                            }
                        ],

                        temperature=0.7,
                        max_tokens=3500

                    )

                    project = (
                        result.choices[0]
                        .message
                        .content
                    )

                    st.session_state.ai_project_result = project

                    st.markdown(
                        project
                    )

                    st.session_state.ai_xp += 40

                except:

                    st.error(
                        "Project generate nahi ho paya."
                    )

        if st.session_state.ai_project_result:

            st.download_button(

                "📥 Save Project Plan",

                data=st.session_state.ai_project_result,

                file_name="clyxess_ai_project.txt",

                mime="text/plain",

                key="download_ai_project"

            )

    # ========================================================
    # TAB 7
    # AI ETHICS
    # ========================================================

    with tab_ethics:

        st.subheader(
            "🔐 Responsible AI & Ethics"
        )

        ethics_items = [

            (
                "🔒 Privacy",
                "Personal information ko protect karna."
            ),

            (
                "⚖️ Bias & Fairness",
                "AI systems mein unfair patterns ko samajhna."
            ),

            (
                "🧠 Hallucination",
                "AI kabhi incorrect information generate kar sakta hai."
            ),

            (
                "📰 Misinformation",
                "AI-generated information ko verify karna."
            ),

            (
                "©️ Copyright",
                "Content aur intellectual property ka responsible use."
            ),

            (
                "🛡️ Security",
                "AI systems ko misuse aur attacks se protect karna."
            ),

            (
                "👤 Human Oversight",
                "Important decisions mein human judgment."
            ),

            (
                "🌍 Social Impact",
                "AI ka society par positive aur negative impact."
            )

        ]

        for title, description in ethics_items:

            with st.expander(title):

                st.write(
                    description
                )

        st.divider()

        if st.button(
            "🎯 Generate Ethics Challenge",
            key="generate_ethics"
        ):

            ethics_prompt = f"""

Create one AI ethics scenario.

Student:
{age_level}

Make it age appropriate.

Give:

1. Situation
2. Problem
3. Two possible decisions
4. Ask student what they would do
5. Ask why
6. Explain the relevant ethical principles

Do not immediately give the best answer.

"""

            try:

                result = client.chat.completions.create(

                    model="llama-3.3-70b-versatile",

                    messages=[
                        {
                            "role": "user",
                            "content": ethics_prompt
                        }
                    ],

                    temperature=0.7,
                    max_tokens=1400

                )

                st.markdown(
                    result.choices[0]
                    .message
                    .content
                )

            except:

                st.error(
                    "Ethics challenge generate nahi ho paya."
                )

    # ========================================================
    # TAB 8
    # PROGRESS / MASTERY
    # ========================================================

    with tab_progress:

        st.subheader(
            "📊 Student Progress"
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "⭐ Total XP",
                st.session_state.ai_xp
            )

        with c2:

            st.metric(
                "📚 Completed",
                len(
                    st.session_state.ai_completed_topics
                )
            )

        with c3:

            st.metric(
                "🎓 Difficulty",
                config["difficulty"]
            )

        st.divider()

        st.subheader(
            "🧠 Topic Mastery"
        )

        for topic in topics:

            topic_id = (
                f"{age_level}::{topic}"
            )

            mastery = st.session_state.ai_mastery.get(
                topic_id,
                0
            )

            st.write(
                f"**{topic} — {mastery}%**"
            )

            st.progress(
                min(mastery / 100, 1)
            )

        st.divider()

        st.info(
            """
            🔮 Adaptive Mastery Engine:

            Future learning engine automatically student ke:

            • Quiz accuracy
            • Practice answers
            • Mistake patterns
            • Time taken
            • Topic completion
            • Project performance

            ko analyse karke difficulty adjust karega.

            Weak topic → prerequisite / easier practice

            Strong topic → harder challenge

            Mastered topic → project / advanced concept
            """
        )

    # ========================================================
    # FOOTER
    # ========================================================

    st.divider()

    st.markdown(
        """
        <div style="
            padding:20px;
            text-align:center;
            border-radius:18px;
            background:#071326;
            border:1px solid #243b60;
        ">

            <h3 style="color:white;">
                🤖 ClyxessChat AI School
            </h3>

            <p style="color:#9eb7d7;">
                Learn • Think • Practice • Build • Create
            </p>

            <p style="
                color:#7089aa;
                font-size:13px;
            ">
                From first AI concept to advanced AI research.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

def render_parent_dashboard():
    st.title("👨‍👩‍👦 Parent Dashboard")
    best=max(st.session_state.play_best_scores.values(),default=0)
    c1,c2,c3=st.columns(3); c1.metric("Completed Levels",len(st.session_state.play_completed_levels)); c2.metric("Best Score",f"{best}/10"); c3.metric("Current Level",st.session_state.play_age)
    report=learning_report()
    st.markdown('<div class="report-card">',unsafe_allow_html=True); st.text(report); st.markdown('</div>',unsafe_allow_html=True)
    st.download_button("📄 Save Report",data=report,file_name="clyxesschat_learning_report.txt",mime="text/plain")
    st.link_button("📤 Share Report", "https://wa.me/?text="+urllib.parse.quote(report))

# ============================================================
# UI START
# ============================================================
st.markdown('<div class="header"><h1>💬 ClyxessChat AI</h1></div>', unsafe_allow_html=True)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("GROQ_API_KEY is missing from Streamlit secrets.")
    st.stop()

with st.sidebar:
    st.title("💬 ClyxessChat AI")
    try:
        logged_user = supabase.auth.get_user().user if supabase else None
    except Exception:
        logged_user = None
    if logged_user:
        st.success(f"👤 {logged_user.email}")
        if st.button("🚪 Log Out", use_container_width=True):
            try: supabase.auth.sign_out()
            except Exception: pass
            st.rerun()
    else:
        st.caption("Not logged in — sign in to save chats and view parent progress.")

    mode = st.radio("Select Mode", [
        "Normal Chat",
        "Creative Lab (School Mode)",
        "🎮 Play & Learn",
        "🎨 Creative AI Image Generator",
        "📷 Vision Lab", 
        "🧠 AI Autonomous Behavior", 
        "🧩 Kids Logic Lab", 
        "🖥️ Real World Project",  
        "🎭 Peer Roleplay Modes",
        "📋 AI Autonomus Behavior",
        "📝 Interactive Homework & Test",
        "👨‍👩‍👦 Parent Dashboard", 
        "👨‍💻 Coding Lab",  
        "🧠 Learn AI",  
        "🚀 Physics Lab",  
        "🔢 Math Lab",  
        "💸 Learn Finance", 
        "📈 Learn Data Science",  
        "🔐 Login / Sign Up"
    ])
    st.markdown("---")
    if st.button("+ New Chat", use_container_width=True):
        st.session_state.messages=[]
        st.session_state.session_id=str(uuid.uuid4())
        st.session_state.school_messages=[]
        st.session_state.school_session_id=str(uuid.uuid4())
        st.rerun()
    st.caption("🇮🇳 India live time: "+get_india_datetime_context().replace("Current India date: ",""))

# ---- routes: one unique screen per feature ----
if mode == "🔐 Login / Sign Up":
    render_login_signup(); st.stop() 
if mode == "💸 Learn Finance":
    render_learn_finance(client); st.stop()   
if mode == "🔢 Math Lab":
    render_math_lab(client); st.stop()        
if mode == "🚀 Physics Lab":
    render_physics_lab(client); st.stop()   
if mode == "🧠 Learn AI":
    render_learn_ai(client); st.stop()
if mode == "👨‍💻 Coding Lab":
    render_coding_lab_mod(); st.stop() 
if mode == "👨‍👩‍👦 Parent Dashboard":
    render_parent_dashboard(); st.stop()
if mode == "🎨 Creative AI Image Generator":
    render_image_generator(); st.stop() 
if mode == "🧩 Kids Logic Lab":
    render_kids_logic_lab(); st.stop() 
if mode == "🧠 AI Autonon":
    render_ai_autonos_behavio(); st.stop()       
if mode == "📷 Vision Lab":
    render_vision_lab(); st.stop()
if mode == "🎭 Peer Roleplay Modes":
    render_roleplay(); st.stop()
if mode == "📋 AI Autonomous Behavior ":
    render_ai_autonomous_behavior(); st.stop()
if mode == "📝 Interactive Homework & Test":
    render_homework_test(); st.stop()
if mode == "🎮 Play & Learn":
    render_play_and_learn(client); st.stop()

# ============================================================
# NORMAL CHAT / CREATIVE LAB — SEPARATE CHAT HISTORIES
# ============================================================
def _explicit_image_request(text):
    low = text.lower().strip()
    phrases = [
        "generate image", "create image", "make an image", "draw an image",
        "generate a picture", "create a picture", "make a picture",
        "image banao", "image bana", "photo banao", "picture banao",
        "poster banao", "चित्र बनाओ", "तस्वीर बनाओ", "फोटो बनाओ"
    ]
    return any(x in low for x in phrases)

def _render_chat_history(messages):
    for message in messages:
        with st.chat_message(message["role"]):
            if "image_url" in message:
                st.markdown('<div class="media-card">', unsafe_allow_html=True)
                st.image(message["image_url"], caption=message.get("image_caption", ""), width=420)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown(message["content"])

def _chat_voice_input(key):
    if not mic_recorder:
        return ""
    audio = mic_recorder(
        start_prompt="🎙️",
        stop_prompt="⏹️",
        key=key
    )
    if audio:
        return transcribe_audio_with_groq(client, audio.get("bytes", b""))
    return ""

def render_normal_chat():
   
    _render_chat_history(st.session_state.messages)

    voice_prompt = _chat_voice_input("normal_chat_mic")
    prompt = st.chat_input("Search / ask ClyxessChat AI…", key="normal_chat_input")
    if not prompt and voice_prompt:
        prompt = voice_prompt

    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)

    if _explicit_image_request(prompt):
        with st.chat_message("assistant"):
            with st.spinner("🎨 Image bana raha hu..."):
                img_data, source = generate_image_url(prompt, False, "Normal", "1:1")
            st.markdown('<div class="media-card">', unsafe_allow_html=True)
            st.image(img_data, width=420, caption="Generated image")
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption(f"Source: {source}")
        st.session_state.messages.append({
            "role": "assistant", "image_url": img_data,
            "image_caption": prompt, "content": "Generated image"
        })
        save_current_chat_cloud()
        st.rerun()

    search_context, sources = search_tavily(prompt)
    system = NORMAL_SYSTEM_PROMPT + "\nLIVE INDIA CLOCK: " + get_india_datetime_context()
    if search_context:
        system += "\nLIVE WEB INFO:\n" + search_context

    with st.chat_message("assistant"):
        # SPINNER - User chat karte hi pehle ye ayega
        responding = st.empty()
        responding.markdown("""
            <div style='display:flex;align-items:center;gap:10px;color:#aaa'>
                <div style='border:2px solid #333;border-top:2px solid #ffcc00;border-radius:50%;width:16px;height:16px;animation:spin 0.8s linear infinite'></div>
                <b>Clyxess is responding<span class="dots"></span></b>
            </div>
            <style>
            @keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
           .dots::after{content:'';animation:dotAnim 1.2s infinite}
            @keyframes dotAnim{0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}100%{content:''}}
            </style>
        """, unsafe_allow_html=True)

        completion, used_model = get_groq_response(client, st.session_state.messages, system, "")
        if completion is None:
            responding.empty()
            st.error("AI response नहीं आ पाया. Please try again.")
            return
        response = completion.choices[0].message.content
        responding.empty()

        placeholder = st.empty()
        typed = ""
        for word in response.split(" "):
            typed += word + " "
            placeholder.markdown(typed + "▌")
            time.sleep(0.01)
        placeholder.markdown(response)
        if sources:
            st.caption("Sources:\n" + sources)
        st.caption("🔒 ClyxessChat AI | Secure • Fast • Private")
        st.session_state.messages.append({"role": "assistant", "content": response})
        save_current_chat_cloud()
        st.rerun()

def render_school_chat():
    st.title("🚀 Creative Lab — School Mode")
    st.caption("Age and language control the AI. School Mode has its own separate chat history.")

    c1, c2 = st.columns(2)
    with c1:
        age_options = ["1-2 Yrs", "3-4 Yrs", "5-6 Yrs", "6-8 Yrs", "8-10 Yrs", "10-11 Yrs", "11+ Yrs"]
        school_age = st.selectbox(
            "🎒 Age Group", age_options,
            index=age_options.index(st.session_state.get("school_age", "1-2 Yrs")),
            key="school_age_selector"
        )
    with c2:
        labels = list(PLAY_LANGUAGES.keys())
        current_label = next((n for n, c in PLAY_LANGUAGES.items() if c == st.session_state.get("school_language", "hi")), labels[0])
        school_label = st.selectbox(
            "🌐 Language", labels,
            index=labels.index(current_label),
            key="school_language_selector"
        )

    st.session_state.school_age = school_age
    st.session_state.school_language = PLAY_LANGUAGES[school_label]

    _render_chat_history(st.session_state.school_messages)

    voice_prompt = _chat_voice_input("school_chat_mic")
    prompt = st.chat_input("Ask School Mode…", key="school_chat_input")
    if not prompt and voice_prompt:
        prompt = voice_prompt

    if not prompt:
        return

    messages = st.session_state.school_messages
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)

    if _explicit_image_request(prompt):
        with st.chat_message("assistant"):
            with st.spinner("🎨 Age-appropriate image bana raha hu..."):
                img_data, source = generate_image_url(prompt, True, school_age, "1:1")
            st.markdown('<div class="media-card">', unsafe_allow_html=True)
            st.image(img_data, width=420, caption="Generated image")
            st.markdown('</div>', unsafe_allow_html=True)
            st.caption(f"Source: {source}")
        messages.append({
            "role": "assistant", "image_url": img_data,
            "image_caption": prompt, "content": "Generated image"
        })
        st.rerun()

    language_name = language_display_name(st.session_state.school_language)
    system = get_school_system_prompt(school_age)
    system += f"\nSELECTED LANGUAGE: {language_name} ({st.session_state.school_language}). Reply ONLY in this language."
    system += "\nUse the previous messages in this School Mode conversation as context. Never use Normal Chat history."
    search_context, sources = search_tavily(prompt)
    if search_context:
        system += "\nLIVE WEB INFO:\n" + search_context

    with st.chat_message("assistant"):
        completion, used_model = get_groq_response(client, messages, system, "")
        if completion is None:
            st.error("AI response नहीं आ पाया. Please try again.")
            return
        response = completion.choices[0].message.content
        placeholder = st.empty()
        typed = ""
        for word in response.split(" "):
            typed += word + " "
            placeholder.markdown(typed + "▌")
            time.sleep(0.02)
        placeholder.markdown(response)
        if sources:
            st.caption("Sources:\n" + sources)
        st.caption("🔒 ClyxessChat AI | Secure • Fast • Private")
        messages.append({"role": "assistant", "content": response})
        st.rerun()

if mode == "Normal Chat":
    render_normal_chat()
    st.stop()

if mode == "Creative Lab (School Mode)":
    render_school_chat()
    st.stop()
