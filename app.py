# ============================================
# 📚 AI Tutor for Slow Learners (TIER 1 - 5 Features)
# ============================================
# Features:
# 1. 🎤 Voice Input (Tamil/English Mic)
# 2. 🔊 Voice Output (Tamil Speak)
# 3. 📊 Progress Tracker
# 4. 🎮 Quiz Mode
# 5. 📚 Multiple Subject Selection

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import random
from datetime import datetime

# Voice packages
try:
    import speech_recognition as sr
    VOICE_INPUT_AVAILABLE = True
except:
    VOICE_INPUT_AVAILABLE = False

try:
    from gtts import gTTS
    import tempfile
    VOICE_OUTPUT_AVAILABLE = True
except:
    VOICE_OUTPUT_AVAILABLE = False

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Models
FREE_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-flash-latest',
]

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_ai_response(prompt):
    """Get AI response with multi-model fallback"""
    for model_name in FREE_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            continue
    return "❌ Sorry! All models failed. Please wait 60 seconds and try again."

def speak_text(text, lang='en'):
    """Convert text to speech and return audio file path"""
    if not VOICE_OUTPUT_AVAILABLE:
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except:
        return None

def listen_to_mic():
    """Listen to microphone and convert speech to text"""
    if not VOICE_INPUT_AVAILABLE:
        return "❌ Voice input not available. Install SpeechRecognition package."
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 Mikrofone-kitta pesunga... (Listening...)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language="en-IN")
            return text
    except sr.WaitTimeoutError:
        return "⏰ Timeout! Please try again."
    except sr.UnknownValueError:
        return "🤔 Sorry, I couldn't understand. Please try again."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================
# DATA PERSISTENCE
# ============================================

PROGRESS_FILE = "student_progress.json"

def load_progress():
    """Load student progress from JSON file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(name, subject, score=0):
    """Save student progress"""
    data = load_progress()
    if name not in data:
        data[name] = {
            "questions_asked": 0,
            "subjects_covered": [],
            "quiz_scores": [],
            "total_points": 0,
            "badges": [],
            "history": []
        }
    
    data[name]["questions_asked"] += 1
    if subject not in data[name]["subjects_covered"]:
        data[name]["subjects_covered"].append(subject)
    
    if score > 0:
        data[name]["quiz_scores"].append(score)
    
    data[name]["total_points"] += 10  # +10 points per interaction
    
    # Badge system
    if data[name]["questions_asked"] >= 5 and "🌟 Quick Learner" not in data[name]["badges"]:
        data[name]["badges"].append("🌟 Quick Learner")
    if data[name]["questions_asked"] >= 10 and "🎓 Scholar" not in data[name]["badges"]:
        data[name]["badges"].append("🎓 Scholar")
    if data[name]["total_points"] >= 100 and "💯 Centurion" not in data[name]["badges"]:
        data[name]["badges"].append("💯 Centurion")
    
    data[name]["history"].append({
        "subject": subject,
        "timestamp": str(datetime.now()),
        "score": score
    })
    
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    return data[name]

# ============================================
# QUIZ GENERATION
# ============================================

def generate_quiz(subject, grade, level):
    """Generate a quiz question using AI"""
    prompt = f"""Generate ONE multiple choice question (MCQ) for:
Subject: {subject}
Grade: {grade}
Level: {level}

Format STRICTLY like this:
QUESTION: [Your question here]
OPTION_A: [First option]
OPTION_B: [Second option]
OPTION_C: [Third option]
OPTION_D: [Fourth option]
CORRECT: [A, B, C, or D]
EXPLANATION: [Brief explanation why the correct answer is right]

Make it engaging and educational.

CRITICAL LANGUAGE RULE:
- Write the question PRIMARILY in English (80% English minimum)
- After EVERY Tamil word, immediately provide English translation in brackets like this: Tamil_word (English_translation)
- Example: "If you have 2 balloons (2 பலூன்கள்) and your friend gives you 3 more..."
- This helps students learn Tamil terms while understanding in English
- Keep technical terms in English with Tamil in brackets"""

    
    response = get_ai_response(prompt)
    
    # Parse the response
    quiz = {
        "question": "",
        "options": {"A": "", "B": "", "C": "", "D": ""},
        "correct": "",
        "explanation": ""
    }
    
    try:
        lines = response.split('\n')
        for line in lines:
            if line.startswith("QUESTION:"):
                quiz["question"] = line.replace("QUESTION:", "").strip()
            elif line.startswith("OPTION_A:"):
                quiz["options"]["A"] = line.replace("OPTION_A:", "").strip()
            elif line.startswith("OPTION_B:"):
                quiz["options"]["B"] = line.replace("OPTION_B:", "").strip()
            elif line.startswith("OPTION_C:"):
                quiz["options"]["C"] = line.replace("OPTION_C:", "").strip()
            elif line.startswith("OPTION_D:"):
                quiz["options"]["D"] = line.replace("OPTION_D:", "").strip()
            elif line.startswith("CORRECT:"):
                quiz["correct"] = line.replace("CORRECT:", "").strip()
            elif line.startswith("EXPLANATION:"):
                quiz["explanation"] = line.replace("EXPLANATION:", "").strip()
    except:
        pass
    
    return quiz

# ============================================
# PAGE SETUP
# ============================================

st.set_page_config(
    page_title="AI Tutor for Slow Learners",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        color: #4CAF50;
        text-align: center;
        font-weight: bold;
    }
    .subtitle {
        font-size: 18px;
        color: #666;
        text-align: center;
    }
    .badge {
        display: inline-block;
        padding: 5px 12px;
        background: #FFD700;
        color: #000;
        border-radius: 15px;
        margin: 3px;
        font-size: 14px;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-title">📚 AI Tutor for Slow Learners</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Tamil + English Mix | Gemini AI | Voice Enabled | Quiz Mode | Progress Tracker</p>', 
            unsafe_allow_html=True)
st.write("---")

# ============================================
# SIDEBAR
# ============================================

with st.sidebar:
    st.header("👤 Student Info")
    student_name = st.text_input("Un peru sollu:", "Friend")
    grade = st.selectbox("Class:", [str(i) for i in range(1, 13)])
    
    st.write("---")
    st.header("📊 Your Progress")
    
    progress = load_progress()
    if student_name in progress:
        p = progress[student_name]
        st.metric("❓ Questions Asked", p['questions_asked'])
        st.metric("🏆 Total Points", p['total_points'])
        st.metric("📚 Subjects", len(p['subjects_covered']))
        
        if p['badges']:
            st.write("**🏅 Your Badges:**")
            badges_html = " ".join([f'<span class="badge">{b}</span>' for b in p['badges']])
            st.markdown(badges_html, unsafe_allow_html=True)
    else:
        st.info("👋 Start learning to see progress!")
    
    st.write("---")
    st.success("✅ AI: Gemini 2.5 Flash (FREE)")

# ============================================
# MODE SELECTION
# ============================================

st.write("### 🎯 Mode-aa Select Panrathu:")

mode = st.radio(
    "Yenna mode venum?",
    ["💬 Doubt Kelkka", "🎮 Quiz Mode"],
    horizontal=True
)

st.write("---")

# ============================================
# MODE 1: DOUBT ASKING
# ============================================

if mode == "💬 Doubt Kelkka":
    
    # Subject & Level
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.selectbox(
            "📖 Subject-aa Select Panrathu:",
            ["Maths", "Science", "English", "Tamil", "Social Science", "Computer Science"]
        )
    
    with col2:
        level = st.selectbox(
            "🎯 Un Level:",
            ["🐢 Beginner (Slow Learner)", "🐇 Average", "🦅 Advanced"]
        )
    
    st.write("---")
    st.subheader(f"💬 Hey {student_name}! Un doubt-aa kelunga:")
    
    # Sample questions
    st.write("💡 **Sample questions:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🌍 What is gravity?"):
            st.session_state.doubt_text = "What is gravity?"
    with col2:
        if st.button("🌱 Photosynthesis enna?"):
            st.session_state.doubt_text = "Photosynthesis enna? Simple-aa sollunga"
    with col3:
        if st.button("🔢 Pythagoras theorem"):
            st.session_state.doubt_text = "Pythagoras theorem sollunga example-la"
    
    # Voice Input
    st.write("**✍️ Type or 🎤 Speak your question:**")
    col1, col2 = st.columns([5, 1])
    
    with col1:
        default_text = st.session_state.get('doubt_text', '')
        doubt = st.text_area(
            "Type your question:",
            value=default_text,
            placeholder="Example: Sir, what is gravity?",
            height=100,
            label_visibility="collapsed"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🎤\nMic", use_container_width=True):
            if VOICE_INPUT_AVAILABLE:
                voice_text = listen_to_mic()
                if not voice_text.startswith("❌") and not voice_text.startswith("⏰") and not voice_text.startswith("🤔"):
                    st.session_state.doubt_text = voice_text
                    st.success(f"✅ Heard: {voice_text}")
                    st.rerun()
                else:
                    st.warning(voice_text)
            else:
                st.error("Install SpeechRecognition package!")
    
    # Get Answer
    if st.button("🚀 Get Answer", use_container_width=True, type="primary"):
        if doubt.strip() == "":
            st.warning("⚠️ Doubt-aa type pannunga or mic use pannunga!")
        else:
            with st.spinner(f"🤖 AI think panruthu {student_name}-ku..."):
                # Dynamic prompt based on level
                if "Beginner" in level:
                    instruction = """
                    - VERY simple language use pannu
                    - Tamil + English mix (Tanglish)
                    - Daily life examples (apple, phone, bike)
                    - Maximum 4-5 lines
                    - Use lots of emojis
                    - Like teaching a 5-year-old child
                    """
                elif "Average" in level:
                    instruction = """
                    - Clear explanation with examples
                    - Mix of Tamil and English
                    - Medium length (8-10 lines)
                    - 2-3 examples
                    """
                else:
                    instruction = """
                    - Detailed technical explanation
                    - Advanced terms with definitions
                    - Multiple examples
                    - In-depth coverage
                    """
                
                prompt = f"""You are a friendly AI Tutor for {student_name}, class {grade}.
Subject: {subject}
Level: {level}

Rules: {instruction}
- Be kind and encouraging
- Use emojis
- End with "Did you understand? Any doubts? 🤔"

Student's doubt: {doubt}

Your response:"""
                
                answer = get_ai_response(prompt)
                
                # Display answer
                st.write("---")
                st.success(f"📖 Answer for {student_name}:")
                st.markdown(answer)
                
                # Voice output
                if VOICE_OUTPUT_AVAILABLE and st.button("🔊 Listen to Answer"):
                    audio_file = speak_text(answer, lang='en')
                    if audio_file:
                        with open(audio_file, 'rb') as f:
                            st.audio(f.read(), format='audio/mp3')
                
                # Save progress
                updated_progress = save_progress(student_name, subject)
                st.info(f"🎉 +10 points earned! Total: {updated_progress['total_points']}")

# ============================================
# MODE 2: QUIZ MODE
# ============================================

elif mode == "🎮 Quiz Mode":
    
    st.subheader("🎮 Quiz Time! Let's Test Your Knowledge!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quiz_subject = st.selectbox(
            "📖 Quiz Subject:",
            ["Maths", "Science", "English", "Tamil", "Social Science", "Computer Science"],
            key="quiz_subject"
        )
    
    with col2:
        quiz_level = st.selectbox(
            "🎯 Quiz Level:",
            ["🐢 Easy", "🐇 Medium", "🦅 Hard"],
            key="quiz_level"
        )
    
    st.write("---")
    
    if st.button("🎲 Generate New Question", type="primary"):
        with st.spinner("🤖 AI quiz question create panruthu..."):
            quiz = generate_quiz(quiz_subject, grade, quiz_level)
            st.session_state.current_quiz = quiz
            st.session_state.quiz_answered = False
            st.rerun()
    
    # Display quiz
    if 'current_quiz' in st.session_state and st.session_state.current_quiz:
        quiz = st.session_state.current_quiz
        
        st.write(f"### ❓ Question:")
        st.info(quiz['question'])
        
        # Options
        if not st.session_state.get('quiz_answered', False):
            answer = st.radio(
                "Un answer-aa select pannunga:",
                [f"A) {quiz['options']['A']}", 
                 f"B) {quiz['options']['B']}", 
                 f"C) {quiz['options']['C']}", 
                 f"D) {quiz['options']['D']}"],
                key="quiz_answer"
            )
            
            if st.button("✅ Submit Answer"):
                selected = answer[0]  # Get A, B, C, or D
                st.session_state.quiz_answered = True
                
                if selected == quiz['correct']:
                    st.success(f"🎉 CORRECT! Answer: {quiz['correct']}")
                    st.balloons()
                    save_progress(student_name, quiz_subject, score=10)
                    st.info("🏆 +10 points earned!")
                else:
                    st.error(f"❌ Wrong! Correct answer: {quiz['correct']}")
                    st.warning(f"💡 {quiz['explanation']}")
                    save_progress(student_name, quiz_subject, score=0)
        else:
            # Show answer explanation
            st.write(f"**✅ Correct Answer:** {quiz['correct']}) {quiz['options'][quiz['correct']]}")
            st.write(f"**💡 Explanation:** {quiz['explanation']}")

# ============================================
# FOOTER
# ============================================

st.write("---")
st.caption("Made with ❤️ for Slow Learners | Powered by Google Gemini | 5 Features: Voice + Quiz + Progress + Multi-Subject + Badges")
