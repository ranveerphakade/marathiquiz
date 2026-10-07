"""
AI Quiz Bot for Marathi Quiz Application
Powered by Gemini API to provide simple, child-friendly Marathi explanations for 4th Standard questions.
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


def get_gemini_api_key() -> Optional[str]:
    """
    Retrieves the Gemini API Key from environment or Streamlit secrets.
    Dynamically re-reads .env on every check so changes take effect immediately without restarting.
    """
    # 1. Search candidate .env paths and reload with override=True
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate_env_paths = [
        os.path.join(base_dir, ".env"),
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "marathi_quiz", ".env")
    ]
    
    for env_path in candidate_env_paths:
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path, override=True)
            break

    # 2. Check os.environ
    key = os.environ.get("GEMINI_API_KEY")
    if key and key.strip() and key.strip() != "your_api_key_here":
        return key.strip()

    # 3. Direct fallback: parse candidate .env files directly
    for env_path in candidate_env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GEMINI_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val and val != "your_api_key_here":
                                os.environ["GEMINI_API_KEY"] = val
                                return val
            except Exception:
                pass

    # 4. Check Streamlit secrets if available inside Streamlit runtime
    try:
        import sys
        if "streamlit" in sys.modules:
            import streamlit as st
            try:
                if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                    s_key = st.secrets["GEMINI_API_KEY"]
                    if s_key and str(s_key).strip() and str(s_key).strip() != "your_api_key_here":
                        return str(s_key).strip()
            except Exception:
                pass
    except Exception:
        pass

    return None


def format_context_prompt(question_ctx: Dict[str, Any]) -> str:
    """Formats the current question context into a clear Marathi description for the AI."""
    if not question_ctx:
        return "कोणताही विशिष्ट प्रश्न निवडलेला नाही. (General Marathi Scholarship Mode)"

    q_data = question_ctx.get("question_data", {})
    if not q_data:
        return "कोणताही विशिष्ट प्रश्न निवडलेला नाही."

    q_text = q_data.get("question", "")
    options = q_data.get("options", [])
    topic = q_data.get("topic", "")
    correct_ans = q_data.get("answer", "")
    explanation = q_data.get("explanation", "")
    user_ans = question_ctx.get("user_answer", "उत्तर दिलेले नाही")

    options_str = "\n".join([f"  - {opt}" for opt in options])

    context = f"""
[सध्याचा प्रश्न संदर्भ / Current Question Context]:
- विषय: मराठी (इयत्ता ४ थी - शिष्यवृत्ती सराव)
- घटक (Topic): {topic if topic else 'मराठी व्याकरण/भाषा'}
- प्रश्न (Question): {q_text}
- पर्याय (Options):
{options_str}
- विद्यार्थ्याने दिलेले उत्तर (Student's Answer): {user_ans}
- योग्य उत्तर (Correct Answer): {correct_ans}
- मूळ स्पष्टीकरण (JSON Explanation): {explanation if explanation else 'उपलब्ध नाही'}
"""
    return context.strip()


SYSTEM_INSTRUCTION = """
तुम्ही '🤖 Quiz Bot' (इयत्ता ४ थी च्या विद्यार्थ्यांचा मराठी अभ्यास मित्र) आहात.
तुमचे एकमेव कार्य विद्यार्थ्याला मराठी प्रश्नमंजुषेतील प्रश्न, उत्तरे, स्पष्टीकरणे व संकल्पना सोप्या भाषेत समजावून सांगणे हे आहे.

कठोर नियम आणि मार्गदर्शक तत्त्वे:
1. भाषा:
   - उत्तरे प्रामुख्याने सोप्या, शुद्ध, बालसुलभ व प्रेमळ मराठी भाषेतच द्या.
   - इयत्ता ४ थी च्या ९-१० वर्षांच्या लहान मुलांसाठी समजतील अशी छोटी व सुटसुटीत वाक्ये वापरा.
   - कोणत्याही अवघड किंवा क्लिष्ट व्याकरणाच्या संज्ञा टाळा.
   - नेहमी मैत्रीपूर्ण, प्रोत्साहक व प्रेमळ असा (उदा. 'शाब्बास!', 'खूप छान प्रयत्न!', 'काळजी करू नकोस').
   - विद्यार्थ्याच्या चुकीच्या उत्तराची कधीही खिल्ली उडवू नका.

2. HINT (सुगावा) मोड:
   - जेव्हा विद्यार्थी विचारतो: "मला hint द्या" किंवा "सुगावा द्या":
     थेट उत्तर न सांगता विचार करायला लावणारा छोटा सुगावा / इशारा द्या.
     थेट उत्तर सांगू नका! (उदा. 'सुंदर' च्या उलट काय असते, असा विचार कर).

3. EXPLANATION (स्पष्टीकरण) मोड:
   - जेव्हा विद्यार्थी विचारतो: "हा प्रश्न समजावून सांग" किंवा "उत्तर का बरोबर आहे?" किंवा "माझे उत्तर का चुकले?":
     अ) योग्य उत्तर कोणते आहे ते सांगा.
     ब) ते उत्तर का योग्य आहे त्याचे सोपे कारण सांगा.
     क) विद्यार्थ्याने चुकीचे उत्तर दिले असल्यास, ते का चूक ठरते ते सांगा.
     ड) गरज असल्यास रोजच्या वापरातील १ छोटे सोपे उदाहरण द्या.
     इ) उत्तर छोटे व मुद्देसूद ठेवा (जास्तीत जास्त ३-५ ओळी).

4. सत्यता (Source of Truth):
   - प्रश्नाच्या JSON मधील मूळ प्रश्नाचे उत्तर व स्पष्टीकरण हीच अंतिम सत्यता आहे.
   - उत्तर बदलू नका किंवा स्वतः वेगळे उत्तर शोधू नका.
   - अवांतर विषयांवर (उदा. गणित, विज्ञान किंवा सामान्य ChatGPT सारख्या गप्पा) बोलू नका.
"""


def get_ai_explanation(
    question_ctx: Dict[str, Any],
    user_message: str,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Calls Gemini API with the question context and student message.
    
    Returns:
        dict: {"success": bool, "reply": str, "error_type": str or None}
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return {
            "success": False,
            "reply": "⚠️ **Gemini API Key सापडली नाही.**\n\nAI Quiz Bot वापरण्यासाठी कृपया प्रकल्प डिरेक्टरीतील `.env` फाईलमध्ये तुमची `GEMINI_API_KEY` प्रविष्ट करा.\n*(टीप: API Key नसली तरीही तुमची मुख्य प्रश्नमंजुषा, निकाल व सराव पूर्णपणे चालू राहील.)*",
            "error_type": "MISSING_KEY"
        }

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        # Context build
        ctx_text = format_context_prompt(question_ctx)

        # Model selection with fallback
        model_names = [
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-3.5-flash",
            "gemini-3.8-flash",
            "gemini-flash-latest",
            "gemini-pro"
        ]
        model = None

        for m_name in model_names:
            try:
                model = genai.GenerativeModel(
                    model_name=m_name,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                break
            except Exception:
                continue

        if model is None:
            model = genai.GenerativeModel(model_name="gemini-3.5-flash-lite")

        # Build prompt messages
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\n{ctx_text}\n\n[विद्यार्थ्याचा प्रश्न / Student's Query]:\n{user_message}"

        # If chat history exists, format it cleanly
        history_context = ""
        if chat_history and len(chat_history) > 0:
            history_lines = []
            for msg in chat_history[-6:]:  # Keep recent turns
                role = "विद्यार्थी" if msg.get("role") == "user" else "Quiz Bot"
                history_lines.append(f"{role}: {msg.get('content')}")
            history_context = "\n[मागील संभाषण / Previous Chat]:\n" + "\n".join(history_lines) + "\n"

        final_content = f"{full_prompt}\n{history_context}\nउत्तर (लहान मुलांसाठी सोप्या मराठीत):"

        response = model.generate_content(final_content)
        
        if response and response.text:
            return {
                "success": True,
                "reply": response.text.strip(),
                "error_type": None
            }
        else:
            return {
                "success": False,
                "reply": "क्षमस्व, उत्तर तयार करता आले नाही. कृपया पुन्हा प्रयत्न करा.",
                "error_type": "EMPTY_RESPONSE"
            }

    except Exception as e:
        err_msg = str(e)
        if "API_KEY_INVALID" in err_msg or "invalid api key" in err_msg.lower():
            friendly_err = "⚠️ तुमची Gemini API Key अवैध (Invalid) आहे. कृपया योग्य API Key तपासा."
        elif "quota" in err_msg.lower() or "429" in err_msg:
            friendly_err = "⏳ API मर्यादा (Quota) संपली आहे. थोड्या वेळाने पुन्हा प्रयत्न करा."
        else:
            friendly_err = f"⚠️ बॉटकडून उत्तर मिळवण्यात अडचण आली: {err_msg}"

        return {
            "success": False,
            "reply": friendly_err,
            "error_type": "API_ERROR"
        }
