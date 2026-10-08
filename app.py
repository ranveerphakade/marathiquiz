"""
मराठी प्रश्नमंजुषा (Marathi Quiz Application)
इयत्ता ४ थी • शिष्यवृत्ती सराव (Class 4 • Scholarship Practice)

Redesigned Clean, Educational UI:
- Centered content layout (max-width: ~900px)
- No sidebar navigation (main application uses full clean canvas)
- Dark navy theme (#0B1020, #151E32) with crisp Marathi typography
- Large clickable option cards
- Floating Quiz Bot accessible at bottom-right corner across all pages
- Seamless context passing from current question & wrong answers to AI Bot
"""

import os
import streamlit as st
from utils.question_loader import load_questions
from utils.quiz_engine import select_questions, calculate_score, to_marathi_num
from utils.ai_bot import get_ai_explanation, get_gemini_api_key
from utils.pwa_helper import inject_pwa

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="मराठी प्रश्नमंजुषा - इयत्ता ४ थी",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 1.1 Progressive Web App (PWA) Injection ---
inject_pwa()


# --- 2. Design System & CSS Styling ---
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&family=Outfit:wght@400;600;700&display=swap');

/* Base Styles & Theme Variables */
:root {
    --bg-main: #0B1020;
    --bg-card: #151E32;
    --bg-card-hover: #1A2640;
    --bg-input: #1C2844;
    --border-subtle: #232D42;
    --border-focus: #3B82F6;
    --primary-blue: #2856A6;
    --accent-yellow: #F5B800;
    --color-success: #22A06B;
    --color-error: #E5484D;
    --text-primary: #FFFFFF;
    --text-secondary: #B8C2D9;
    --text-muted: #8E9BB0;
}

/* Force Dark Theme Background */
html, body, .stApp {
    background-color: #0B1020 !important;
    color: #FFFFFF !important;
    font-family: 'Baloo 2', 'Noto Sans Devanagari', 'Outfit', sans-serif !important;
}

/* Center Content Container with comfortable max-width */
.block-container {
    max-width: 880px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 5.5rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    margin: 0 auto !important;
}

/* Completely Hide Sidebar and Collapse Arrow */
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Global Typography */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    font-family: 'Baloo 2', 'Noto Sans Devanagari', sans-serif !important;
}

/* Header Card */
.header-card {
    background: linear-gradient(135deg, #1E40AF 0%, #2856A6 50%, #1D4ED8 100%);
    border-radius: 18px;
    padding: 1.3rem 1.6rem;
    text-align: center;
    margin-bottom: 1.3rem;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.12);
}

.header-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #FFFFFF !important;
    margin: 0;
    line-height: 1.25;
    letter-spacing: 0.5px;
}

.header-subtitle {
    font-size: 1.15rem;
    font-weight: 700;
    color: #F5B800 !important;
    margin-top: 0.35rem;
}

/* Clean Educational Cards */
.edu-card {
    background-color: #151E32;
    border: 1px solid #232D42;
    border-radius: 16px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

/* Info Stat Cards (3 Column Grid) */
.info-stat-card {
    background-color: #151E32;
    border: 1px solid #232D42;
    border-radius: 14px;
    padding: 1.1rem 0.8rem;
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease;
    height: 100%;
}

.info-stat-card:hover {
    transform: translateY(-2px);
    border-color: #3B82F6;
}

.info-stat-val {
    font-size: 1.85rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 0.2rem;
}

.info-stat-label {
    font-size: 0.95rem;
    font-weight: 600;
    color: #B8C2D9;
}

/* Question Badges */
.q-pill {
    display: inline-flex;
    align-items: center;
    background: rgba(37, 99, 235, 0.2);
    color: #60A5FA;
    border: 1px solid rgba(96, 165, 250, 0.3);
    font-weight: 700;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-size: 0.95rem;
}

.topic-pill {
    display: inline-flex;
    align-items: center;
    background: rgba(245, 184, 0, 0.15);
    color: #FCD34D;
    border: 1px solid rgba(245, 184, 0, 0.3);
    font-weight: 600;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.9rem;
    margin-left: 0.5rem;
}

.question-text {
    font-size: 1.35rem;
    font-weight: 700;
    line-height: 1.6;
    color: #FFFFFF;
    margin: 1rem 0 1.2rem 0;
}

/* Radio Button Option Cards (Large Clickable Options) */
div[data-testid="stRadio"] > div {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

div[data-testid="stRadio"] label {
    background-color: #172239 !important;
    border: 1.5px solid #23314E !important;
    border-radius: 14px !important;
    padding: 12px 18px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    color: #FFFFFF !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    display: flex !important;
    align-items: center !important;
}

div[data-testid="stRadio"] label:hover {
    background-color: #1E2D4C !important;
    border-color: #3B82F6 !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

div[data-testid="stRadio"] label:has(input:checked),
div[data-testid="stRadio"] label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.25) 0%, rgba(30, 64, 175, 0.3) 100%) !important;
    border-color: #60A5FA !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    box-shadow: 0 0 0 1px #60A5FA, 0 4px 14px rgba(37, 99, 235, 0.25) !important;
}

div[data-testid="stRadio"] label span {
    color: #FFFFFF !important;
}

/* Streamlit Buttons Styling */
div.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 0.55rem 1.2rem !important;
    border: 1px solid #283756 !important;
    background-color: #18233C !important;
    color: #FFFFFF !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:hover {
    border-color: #3B82F6 !important;
    background-color: #1F2E4F !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    border: 1px solid #3B82F6 !important;
    color: #FFFFFF !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
}

div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.45) !important;
}

/* Review Cards for Wrong Answers */
.wrong-review-card {
    background-color: #151E32;
    border: 1px solid #232D42;
    border-left: 5px solid #E5484D;
    border-radius: 14px;
    padding: 1.3rem 1.4rem;
    margin-bottom: 1.2rem;
}

.ans-line {
    font-size: 1.05rem;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
}

.ans-wrong-badge {
    color: #F87171;
    font-weight: 700;
}

.ans-correct-badge {
    color: #4ADE80;
    font-weight: 700;
}

.explanation-container {
    background: rgba(34, 160, 107, 0.12);
    border: 1px solid rgba(34, 160, 107, 0.25);
    border-radius: 10px;
    padding: 0.75rem 0.95rem;
    margin-top: 0.8rem;
    font-size: 0.98rem;
    color: #A7F3D0;
    line-height: 1.5;
}

/* Progress bar styling */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3B82F6, #60A5FA) !important;
    border-radius: 10px;
}
.stProgress > div > div {
    background-color: #1E293B !important;
    border-radius: 10px;
}

/* Selectbox styling */
div[data-baseweb="select"] {
    background-color: #172239 !important;
    border-color: #23314E !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
}

/* Chat Message Styling */
[data-testid="stChatMessage"] {
    background-color: #131B2E !important;
    border: 1px solid #1E2B45 !important;
    border-radius: 12px !important;
    margin-bottom: 0.8rem !important;
}

/* Fixed Floating Bot Trigger Button */
.bot-float-container,
div[data-testid="stVerticalBlock"]:has(button[key="floating_bot_pill_btn"]) {
    position: fixed !important;
    bottom: 24px !important;
    right: 24px !important;
    z-index: 999999 !important;
    width: auto !important;
}

div.stButton > button[key="floating_bot_pill_btn"],
.bot-float-container button {
    background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.3) !important;
    box-shadow: 0 8px 24px rgba(37, 99, 235, 0.45) !important;
    border-radius: 30px !important;
    padding: 0.65rem 1.35rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
    letter-spacing: 0.3px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
}

div.stButton > button[key="floating_bot_pill_btn"]:hover,
.bot-float-container button:hover {
    transform: translateY(-3px) scale(1.03) !important;
    box-shadow: 0 12px 30px rgba(37, 99, 235, 0.65) !important;
}

/* Mobile responsive adjustments */
@media (max-width: 640px) {
    .header-title {
        font-size: 1.6rem !important;
    }
    .header-subtitle {
        font-size: 0.95rem !important;
    }
    .question-text {
        font-size: 1.18rem !important;
    }
    .block-container {
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# --- 3. Session State Initialization ---
def init_session_state():
    """Initializes session state safely without resetting progress."""
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "home"  # 'home', 'quiz', 'result', 'wrong_answers'

    if "all_questions" not in st.session_state:
        questions, metadata = load_questions()
        st.session_state.all_questions = questions
        st.session_state.metadata = metadata

    if "active_questions" not in st.session_state:
        st.session_state.active_questions = []

    if "current_index" not in st.session_state:
        st.session_state.current_index = 0

    if "answers" not in st.session_state:
        st.session_state.answers = {}  # {question_id: selected_option}

    if "score_data" not in st.session_state:
        st.session_state.score_data = {}

    if "quiz_mode" not in st.session_state:
        st.session_state.quiz_mode = "practice"

    if "practice_count" not in st.session_state:
        st.session_state.practice_count = 10

    # Bot State
    if "bot_context_q" not in st.session_state:
        st.session_state.bot_context_q = None

    if "bot_chat_history" not in st.session_state:
        st.session_state.bot_chat_history = [
            {
                "role": "assistant",
                "content": (
                    "नमस्कार! 👋\n"
                    "मी तुमचा **मराठी Quiz Bot** आहे.\n\n"
                    "तुम्हाला एखादा प्रश्न समजून घ्यायचा असेल, "
                    "उत्तर का बरोबर आहे हे जाणून घ्यायचे असेल किंवा "
                    "hint हवा असेल तर मला विचारा."
                )
            }
        ]
    else:
        # If API key is now active, automatically purge old "API Key missing" errors from previous session
        if get_gemini_api_key():
            st.session_state.bot_chat_history = [
                msg for msg in st.session_state.bot_chat_history
                if "Gemini API Key सापडली नाही" not in msg.get("content", "")
            ]
            if not st.session_state.bot_chat_history:
                st.session_state.bot_chat_history = [
                    {
                        "role": "assistant",
                        "content": "नमस्कार! 👋\nमी तुमचा **मराठी Quiz Bot** आहे. मला कोणताही प्रश्न किंवा hint विचारा."
                    }
                ]


init_session_state()


def navigate_to(page: str):
    """Smooth navigation router."""
    st.session_state.nav_page = page
    st.rerun()


# --- 4. Reusable Header Card ---
def render_header(compact: bool = False):
    """Renders the top centered blue header card."""
    if compact:
        st.markdown("""
        <div class="header-card" style="padding: 0.9rem 1.2rem; margin-bottom: 1rem;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF; line-height: 1.2;">
                📚 मराठी प्रश्नमंजुषा
            </div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #F5B800; margin-top: 0.2rem;">
                इयत्ता ४ थी • शिष्यवृत्ती सराव
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="header-card">
            <h1 class="header-title">📚 मराठी प्रश्नमंजुषा</h1>
            <div class="header-subtitle">इयत्ता ४ थी • शिष्यवृत्ती सराव</div>
        </div>
        """, unsafe_allow_html=True)


# --- 5. Floating Quiz Bot Component ---
def get_current_active_context():
    """Determines the active question context based on current page state."""
    # 1. If explicit context set (e.g. from wrong answers click)
    if st.session_state.bot_context_q:
        return st.session_state.bot_context_q

    # 2. If in active quiz, pass current question
    if st.session_state.nav_page == "quiz" and st.session_state.active_questions:
        curr_idx = st.session_state.current_index
        if 0 <= curr_idx < len(st.session_state.active_questions):
            q_data = st.session_state.active_questions[curr_idx]
            q_id = q_data["id"]
            user_ans = st.session_state.answers.get(q_id, "अजून निवडले नाही")
            return {
                "question_data": q_data,
                "user_answer": user_ans,
                "correct_answer": q_data.get("answer", "")
            }

    # 3. If in wrong answers page
    if st.session_state.nav_page == "wrong_answers" and st.session_state.score_data:
        wrong_list = st.session_state.score_data.get("wrong_questions", [])
        if wrong_list:
            return wrong_list[0]

    return None


@st.dialog("🤖 Quiz Bot — मराठी अभ्यास मित्र", width="large")
def show_bot_dialog():
    """Renders the AI Quiz Bot modal dialog overlay without leaving or resetting the quiz."""
    ctx = get_current_active_context()

    # Automatically purge old "API Key missing" errors from previous session if key is now present
    if get_gemini_api_key():
        st.session_state.bot_chat_history = [
            msg for msg in st.session_state.bot_chat_history
            if "Gemini API Key सापडली नाही" not in msg.get("content", "")
        ]
        if not st.session_state.bot_chat_history:
            st.session_state.bot_chat_history = [
                {
                    "role": "assistant",
                    "content": "नमस्कार! 👋\nमी तुमचा **मराठी Quiz Bot** आहे. मला कोणताही प्रश्न किंवा hint विचारा."
                }
            ]

    # If context is available, display a clear context banner
    if ctx and ctx.get("question_data"):
        qd = ctx["question_data"]
        topic = qd.get("topic", "")
        u_ans = ctx.get("user_answer", "निवडले नाही")
        c_ans = qd.get("answer", "")
        
        st.markdown(f"""
        <div style="background: #18233C; border: 1px solid #283756; border-left: 4px solid #3B82F6; border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 0.8rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
                <span style="font-size: 0.85rem; font-weight: 700; color: #60A5FA;">📌 सध्याचा प्रश्न संदर्भ {f'({topic})' if topic else ''}</span>
            </div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.4rem;">
                {qd.get('question', '')}
            </div>
            <div style="display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.9rem;">
                <span style="color: #B8C2D9;">तुमचे उत्तर: <strong style="color: {'#4ADE80' if u_ans == c_ans and u_ans != 'निवडले नाही' else '#F87171'};">{u_ans}</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Quick Suggestion Action Chips
    st.markdown("<div style='font-size: 0.88rem; font-weight: 600; color: #B8C2D9; margin-bottom: 0.4rem;'>👇 जलद प्रश्न विचारा:</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    quick_prompt = None

    with c1:
        if st.button("💡 समजावून सांग", key="dlg_chip_exp", use_container_width=True):
            quick_prompt = "हा प्रश्न मला सोप्या भाषेत समजावून सांग."
    with c2:
        if st.button("🔍 मला hint द्या", key="dlg_chip_hint", use_container_width=True):
            quick_prompt = "मला hint द्या (थेट उत्तर न सांगता एक छोटा सुगावा द्या)."
    with c3:
        if st.button("❌ उत्तर का चुकले?", key="dlg_chip_wrong", use_container_width=True):
            quick_prompt = "माझे उत्तर चुकीचे का आहे? मला समजावून सांग."
    with c4:
        if st.button("✅ योग्य उत्तर का?", key="dlg_chip_why_corr", use_container_width=True):
            quick_prompt = "योग्य उत्तर का बरोबर आहे ते समजावून सांग."

    # Chat Messages History Box
    chat_box = st.container(height=320)
    with chat_box:
        for msg in st.session_state.bot_chat_history:
            avatar = "🧑‍🎓" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # Chat Input
    user_query = st.chat_input("तुमचा प्रश्न येथे विचारा... (उदा. मला hint द्या)", key="dlg_chat_input")
    selected_query = quick_prompt or user_query

    if selected_query:
        # Append User Message to history
        st.session_state.bot_chat_history.append({"role": "user", "content": selected_query})
        
        # Generate Response dynamically in dialog
        with chat_box:
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(selected_query)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Quiz Bot विचार करत आहे..."):
                    res = get_ai_explanation(
                        ctx or {},
                        selected_query,
                        st.session_state.bot_chat_history[:-1]
                    )
                    reply_text = res.get("reply", "क्षमस्व, उत्तर देता आले नाही.")
                    st.markdown(reply_text)
                    st.session_state.bot_chat_history.append({"role": "assistant", "content": reply_text})

    # Dialog Footer Controls
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        if st.button("🗑️ चॅट साफ करा", key="dlg_clear_chat", use_container_width=True):
            st.session_state.bot_chat_history = [
                {
                    "role": "assistant",
                    "content": "नमस्कार! 👋\nमी तुमचा **🤖 Quiz Bot** आहे. प्रश्न किंवा hint विचारण्यासाठी तयार आहे!"
                }
            ]
            st.rerun()


def render_floating_bot_button():
    """Renders the fixed floating Quiz Bot button at bottom-right corner."""
    # Bottom floating trigger button using a fixed bottom bar or columns
    st.markdown("""
    <style>
    /* Fixed Floating Bot Trigger */
    .bot-float-container {
        position: fixed;
        bottom: 22px;
        right: 22px;
        z-index: 999999;
    }
    .bot-float-container button {
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.25) !important;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.45) !important;
        border-radius: 30px !important;
        padding: 0.65rem 1.4rem !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        letter-spacing: 0.3px;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .bot-float-container button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 28px rgba(37, 99, 235, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Use Streamlit bottom container
    with st.container():
        st.markdown('<div class="bot-float-container">', unsafe_allow_html=True)
        if st.button("🤖 Quiz Bot", key="floating_bot_pill_btn", type="primary"):
            show_bot_dialog()
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 6. 🏠 HOME PAGE (render_home)
# ==========================================
def render_home():
    render_header()

    all_qs = st.session_state.all_questions
    metadata = st.session_state.metadata
    total_count = len(all_qs)

    if not all_qs:
        error_msg = metadata.get("error", "प्रश्नांची फाईल सापडली नाही.")
        st.error(f"⚠️ **त्रुटी:** {error_msg}")
        st.info("कृपया `data/questions.json` फाईल तपासा.")
        return

    # Introduction Card
    st.markdown("""
    <div class="edu-card" style="text-align: center;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #F5B800; margin-bottom: 0.35rem;">
            ✨ शिष्यवृत्ती परीक्षेसाठी सराव करा!
        </div>
        <div style="font-size: 1.05rem; color: #E2E8F0; line-height: 1.5;">
            इयत्ता चौथीच्या विद्यार्थ्यांसाठी खास तयार केलेले मराठी व्याकरण व भाषेचे बहुपर्यायी प्रश्न.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3 Information Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="info-stat-card">
            <div class="info-stat-val" style="color: #60A5FA;">मराठी</div>
            <div class="info-stat-label">विषय</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="info-stat-card">
            <div class="info-stat-val" style="color: #F5B800;">४ थी</div>
            <div class="info-stat-label">इयत्ता</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="info-stat-card">
            <div class="info-stat-val" style="color: #34D399;">{to_marathi_num(total_count)}</div>
            <div class="info-stat-label">उपलब्ध प्रश्न</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Quiz Mode Section
    st.markdown("""
    <div style="margin-top: 0.5rem; margin-bottom: 0.4rem;">
        <span style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">🎯 परीक्षा प्रकार निवडा</span>
    </div>
    """, unsafe_allow_html=True)

    mode_selection = st.radio(
        "परीक्षा प्रकार निवडा:",
        options=["सराव परीक्षा", "पूर्ण परीक्षा"],
        index=0 if st.session_state.quiz_mode == "practice" else 1,
        label_visibility="collapsed",
        key="home_mode_radio"
    )

    selected_count = total_count
    if mode_selection == "सराव परीक्षा":
        st.session_state.quiz_mode = "practice"
        count_options = [5, 10, 20, total_count]
        valid_options = [c for c in count_options if c <= total_count]
        if total_count not in valid_options:
            valid_options.append(total_count)

        def format_count_option(val):
            if val == total_count:
                return f"सर्व उपलब्ध प्रश्न ({to_marathi_num(val)})"
            return f"{to_marathi_num(val)} प्रश्न"

        curr_cnt = st.session_state.practice_count
        default_idx = valid_options.index(curr_cnt) if curr_cnt in valid_options else 1

        selected_count = st.selectbox(
            "प्रश्न संख्या निवडा:",
            options=valid_options,
            format_func=format_count_option,
            index=default_idx,
            label_visibility="collapsed"
        )
        st.session_state.practice_count = selected_count
    else:
        st.session_state.quiz_mode = "full"
        st.session_state.practice_count = total_count
        selected_count = total_count
        st.markdown(f"""
        <div style="background: rgba(37, 99, 235, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 10px; padding: 0.7rem 1rem; color: #93C5FD; font-size: 0.95rem; margin-top: 0.3rem;">
            💡 पूर्ण परीक्षेत सर्व <strong>{to_marathi_num(total_count)}</strong> प्रश्न समाविष्ट केले जातील.
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Start Quiz Button (Single Prominent Action)
    if st.button("🚀 परीक्षा सुरू करा", type="primary", use_container_width=True, key="start_quiz_main_btn"):
        st.session_state.active_questions = select_questions(
            all_qs,
            st.session_state.quiz_mode,
            st.session_state.practice_count
        )
        st.session_state.current_index = 0
        st.session_state.answers = {}
        st.session_state.score_data = {}
        st.session_state.bot_context_q = None
        navigate_to("quiz")


# ==========================================
# 7. 📝 QUIZ INTERFACE (render_quiz)
# ==========================================
def render_quiz():
    render_header(compact=True)

    questions = st.session_state.active_questions
    if not questions:
        # Prompt to start a quiz if visited directly
        st.markdown("""
        <div class="edu-card" style="text-align: center;">
            <div style="font-size: 1.25rem; font-weight: 700; color: #F5B800; margin-bottom: 0.5rem;">
                📝 कोणतीही परीक्षा चालू नाही
            </div>
            <p style="color: #B8C2D9;">कृपया मुख्य पृष्ठावरून परीक्षा सुरू करा.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🏠 मुख्य पृष्ठावर जा", type="primary", use_container_width=True):
            navigate_to("home")
        return

    curr_idx = st.session_state.current_index
    total_q = len(questions)

    # Bounds check
    if curr_idx < 0:
        curr_idx = 0
        st.session_state.current_index = 0
    elif curr_idx >= total_q:
        curr_idx = total_q - 1
        st.session_state.current_index = curr_idx

    current_q = questions[curr_idx]
    q_id = current_q["id"]

    curr_m_num = to_marathi_num(curr_idx + 1)
    total_m_num = to_marathi_num(total_q)

    # Progress Header
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        st.markdown(f"""
        <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">
            प्रश्न {curr_m_num} / {total_m_num}
        </div>
        """, unsafe_allow_html=True)
    with col_p2:
        answered_cnt = len([a for a in st.session_state.answers.values() if a])
        st.markdown(f"""
        <div style="text-align: right; font-size: 0.95rem; font-weight: 600; color: #60A5FA;">
            सोडवले: {to_marathi_num(answered_cnt)} / {total_m_num}
        </div>
        """, unsafe_allow_html=True)

    progress_val = (curr_idx + 1) / total_q
    st.progress(progress_val)
    st.write("")

    # Question Card
    topic = current_q.get("topic", "")
    topic_html = f"<span class='topic-pill'>📌 {topic}</span>" if topic else ""

    st.markdown(f"""
    <div class="edu-card">
        <div style="margin-bottom: 0.6rem;">
            <span class="q-pill">प्रश्न क्र. {curr_m_num}</span>
            {topic_html}
        </div>
        <div class="question-text">
            {current_q['question']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Options as Large Clickable Cards
    options = current_q.get("options", [])
    current_selected = st.session_state.answers.get(q_id, None)

    default_idx = None
    if current_selected in options:
        default_idx = options.index(current_selected)

    # Formatted options with A, B, C, D badges
    option_letters = ["A", "B", "C", "D", "E", "F"]
    formatted_options = []
    option_map = {}
    for i, opt in enumerate(options):
        letter = option_letters[i] if i < len(option_letters) else f"{i+1}"
        formatted_label = f"{letter}   {opt}"
        formatted_options.append(formatted_label)
        option_map[formatted_label] = opt

    formatted_default_idx = default_idx

    selected_formatted = st.radio(
        "पर्याय निवडा:",
        options=formatted_options,
        index=formatted_default_idx,
        key=f"quiz_opt_radio_{q_id}_{curr_idx}",
        label_visibility="collapsed"
    )

    if selected_formatted:
        raw_val = option_map.get(selected_formatted)
        st.session_state.answers[q_id] = raw_val

    st.write("")
    st.write("")

    # Navigation Controls
    col_prev, col_mid, col_next = st.columns([1.2, 1, 1.2])

    with col_prev:
        if curr_idx > 0:
            if st.button("← मागील", use_container_width=True, key="quiz_prev_btn"):
                st.session_state.current_index -= 1
                st.rerun()
        else:
            st.button("← मागील", disabled=True, use_container_width=True, key="quiz_prev_btn_dis")

    with col_mid:
        if st.button("🏁 निकाल पहा", use_container_width=True, key="quiz_mid_submit_btn"):
            st.session_state.score_data = calculate_score(questions, st.session_state.answers)
            navigate_to("result")

    with col_next:
        if curr_idx < total_q - 1:
            if st.button("पुढे →", type="primary", use_container_width=True, key="quiz_next_btn"):
                st.session_state.current_index += 1
                st.rerun()
        else:
            if st.button("✅ पूर्ण करा", type="primary", use_container_width=True, key="quiz_finish_btn"):
                st.session_state.score_data = calculate_score(questions, st.session_state.answers)
                navigate_to("result")


# ==========================================
# 8. 🏆 RESULT PAGE (render_result)
# ==========================================
def render_result():
    render_header(compact=True)

    score_data = st.session_state.score_data
    if not score_data:
        if st.session_state.active_questions:
            st.session_state.score_data = calculate_score(
                st.session_state.active_questions,
                st.session_state.answers
            )
            score_data = st.session_state.score_data
        else:
            st.info("💡 कृपया आधी परीक्षा द्या.")
            if st.button("🚀 परीक्षा सुरू करा", type="primary"):
                navigate_to("home")
            return

    total = score_data.get("total", 0)
    correct = score_data.get("correct", 0)
    incorrect = score_data.get("incorrect", 0)
    unanswered = score_data.get("unanswered", 0)
    percentage = score_data.get("percentage", 0.0)
    feedback = score_data.get("feedback", "तुमची कामगिरी खूप छान आहे!")

    # Large Centered Result Card
    st.markdown(f"""
    <div class="edu-card" style="text-align: center; border: 1.5px solid #2856A6; padding: 1.8rem 1.5rem;">
        <div style="font-size: 1.8rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.4rem;">
            🏆 प्रश्नमंजुषा पूर्ण!
        </div>
        <div style="font-size: 2.8rem; font-weight: 800; color: #60A5FA; margin: 0.3rem 0;">
            {to_marathi_num(correct)} / {to_marathi_num(total)}
        </div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #34D399; margin-bottom: 0.8rem;">
            {percentage}%
        </div>
        <div style="display: inline-block; background: rgba(37, 99, 235, 0.15); border: 1px solid rgba(96, 165, 250, 0.3); border-radius: 12px; padding: 0.6rem 1.2rem; font-size: 1.15rem; font-weight: 700; color: #F5B800;">
            {feedback}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3 Small Result Breakdown Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="info-stat-card" style="border-top: 3px solid #22A06B;">
            <div class="info-stat-val" style="color: #34D399;">✓ {to_marathi_num(correct)}</div>
            <div class="info-stat-label">बरोबर</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="info-stat-card" style="border-top: 3px solid #E5484D;">
            <div class="info-stat-val" style="color: #F87171;">✗ {to_marathi_num(incorrect)}</div>
            <div class="info-stat-label">चूक</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="info-stat-card" style="border-top: 3px solid #F5B800;">
            <div class="info-stat-val" style="color: #FCD34D;">○ {to_marathi_num(unanswered)}</div>
            <div class="info-stat-label">न सोडवलेले</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # Action Buttons
    wrong_count = len(score_data.get("wrong_questions", []))
    
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        if st.button("🔄 पुन्हा परीक्षा द्या", use_container_width=True, key="res_retry_btn"):
            st.session_state.answers = {}
            st.session_state.current_index = 0
            st.session_state.score_data = {}
            if st.session_state.quiz_mode == "practice":
                st.session_state.active_questions = select_questions(
                    st.session_state.all_questions,
                    "practice",
                    st.session_state.practice_count
                )
            navigate_to("quiz")

    with col_act2:
        if wrong_count > 0:
            if st.button(f"❌ चुकीचे प्रश्न पहा ({to_marathi_num(wrong_count)})", type="primary", use_container_width=True, key="res_wrong_btn"):
                navigate_to("wrong_answers")
        else:
            if st.button("🏠 मुख्य पृष्ठावर जा", type="primary", use_container_width=True, key="res_home_btn"):
                navigate_to("home")

    if wrong_count > 0:
        st.write("")
        if st.button("🏠 मुख्य पृष्ठावर जा", use_container_width=True, key="res_home_secondary_btn"):
            navigate_to("home")


# ==========================================
# 9. ❌ WRONG ANSWERS PAGE (render_wrong_answers)
# ==========================================
def render_wrong_answers():
    render_header(compact=True)

    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.2rem;">
            ❌ चुकीचे प्रश्न
        </div>
        <div style="color: #B8C2D9; font-size: 1rem;">
            खालील प्रश्नांची योग्य उत्तरे व स्पष्टीकरणे अभ्यासा.
        </div>
    </div>
    """, unsafe_allow_html=True)

    score_data = st.session_state.score_data
    if not score_data:
        if st.session_state.active_questions:
            st.session_state.score_data = calculate_score(
                st.session_state.active_questions,
                st.session_state.answers
            )
            score_data = st.session_state.score_data
        else:
            st.info("💡 कृपया आधी परीक्षा द्या.")
            if st.button("🚀 परीक्षा सुरू करा", type="primary"):
                navigate_to("home")
            return

    wrong_questions = score_data.get("wrong_questions", [])

    if not wrong_questions:
        st.markdown("""
        <div class="edu-card" style="text-align: center; border: 1px solid #22A06B;">
            <div style="font-size: 1.4rem; font-weight: 700; color: #34D399; margin-bottom: 0.4rem;">
                🎉 अभिनंदन!
            </div>
            <div style="color: #FFFFFF; font-size: 1.1rem;">
                तुमचे सर्व प्रश्न बरोबर आले आहेत! एकही उत्तर चुकलेले नाही.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("🏆 निकालाकडे परत जा", type="primary", use_container_width=True):
            navigate_to("result")
        return

    for idx, item in enumerate(wrong_questions):
        q = item["question_data"]
        user_ans = item["user_answer"]
        correct_ans = item["correct_answer"]
        topic = q.get("topic", "")
        explanation = q.get("explanation", "").strip()
        q_num = to_marathi_num(idx + 1)

        st.markdown(f"""
        <div class="wrong-review-card">
            <div style="margin-bottom: 0.5rem;">
                <span class="q-pill" style="background: rgba(229, 72, 77, 0.2); color: #F87171; border-color: rgba(229, 72, 77, 0.3);">प्रश्न {q_num}</span>
                {f"<span class='topic-pill'>📌 {topic}</span>" if topic else ""}
            </div>
            <div style="font-size: 1.2rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.8rem;">
                {q['question']}
            </div>
            <div class="ans-line">
                <span style="color: #B8C2D9;">तुमचे उत्तर:</span>
                <span class="ans-wrong-badge">{user_ans}</span>
            </div>
            <div class="ans-line">
                <span style="color: #B8C2D9;">योग्य उत्तर:</span>
                <span class="ans-correct-badge">{correct_ans}</span>
            </div>
            {f'<div class="explanation-container"><strong>💡 स्पष्टीकरण:</strong> {explanation}</div>' if explanation else ''}
        </div>
        """, unsafe_allow_html=True)

        # Bot trigger for this specific wrong question
        if st.button(
            f"🤖 Quiz Bot कडून समजून घ्या",
            key=f"btn_explain_wrong_q_{q['id']}_{idx}",
            use_container_width=True
        ):
            st.session_state.bot_context_q = item
            show_bot_dialog()

        st.write("")

    st.write("")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        if st.button("🔄 पुन्हा परीक्षा द्या", use_container_width=True, key="wrong_retry_btn"):
            st.session_state.answers = {}
            st.session_state.current_index = 0
            st.session_state.score_data = {}
            if st.session_state.quiz_mode == "practice":
                st.session_state.active_questions = select_questions(
                    st.session_state.all_questions,
                    "practice",
                    st.session_state.practice_count
                )
            navigate_to("quiz")

    with col_w2:
        if st.button("🏆 निकालाकडे परत जा", type="primary", use_container_width=True, key="wrong_back_result_btn"):
            navigate_to("result")


# ==========================================
# 10. MAIN APP ROUTER & RUNNER
# ==========================================
def main():
    current_page = st.session_state.get("nav_page", "home")

    if current_page == "home":
        render_home()
    elif current_page == "quiz":
        render_quiz()
    elif current_page == "result":
        render_result()
    elif current_page == "wrong_answers":
        render_wrong_answers()
    else:
        render_home()

    # Always render the floating Quiz Bot button
    render_floating_bot_button()


if __name__ == "__main__":
    main()
