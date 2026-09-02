import streamlit as st
from PIL import Image
import pytesseract
from google import genai

# Gemini API Key ని ఇక్కడ ఉంచండి
GEMINI_API_KEY = "AQ.Ab8RN6IELJB2yhussCFa7xQXyAQf1U6VGs3xDlCn22nX5Ve-GA"

client = genai.Client(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="BNS Legal Assistant", page_icon="⚖️", layout="centered")

st.title("⚖️ BNS, BNSS & BSA లీగల్ అసిస్టెంట్")
st.write("కేసు వివరాలు నమోదు చేయండి లేదా ఫిర్యాదు కాపీ ఫోటో తీసి అప్‌లోడ్ చేయండి.")

tab1, tab2 = st.tabs(["📝 టెక్స్ట్ వివరాలు", "📷 ఫోటో / డాక్యుమెంట్"])

case_text = ""

with tab1:
    text_input = st.text_area("ఫిర్యాదు వివరాలు ఇక్కడ రాయండి:", height=150)
    if text_input:
        case_text = text_input

with tab2:
    uploaded_file = st.file_uploader("ఫిర్యాదు కాపీ ఫోటో ఎంచుకోండి", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="అప్‌లోడ్ చేసిన చిత్రం", use_container_width=True)
        try:
            extracted = pytesseract.image_to_string(img)
            st.info(f"గుర్తించిన టెక్స్ట్:\n{extracted}")
            case_text = extracted
        except Exception:
            st.warning("OCR రీడింగ్ కాలేదు, దయచేసి టెక్స్ట్ బాక్స్‌లో వివరాలు నమోదు చేయండి.")

if st.button("కేస్ విశ్లేషించండి (Analyze)", type="primary") and case_text:
    with st.spinner("BNS, BNSS, BSA ప్రకారం పరిశీలిస్తోంది..."):
        prompt = f"""
        You are an Indian criminal law expert assistant. Analyze the case details:
        {case_text}

        Provide a structured output in Telugu (with English legal terms):
        1. **BNS Sections & Punishments** (with old IPC equivalents)
        2. **BNSS Procedures** (Arrest rules, Section 35(3), Forensic visits, Search/Seizure)
        3. **BSA Evidence Guidelines** (Digital evidence certification Section 63, chain of custody)
        4. **Step-by-Step Investigation SOP for IO**
        """
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            st.markdown("### 📋 దర్యాప్తు నివేదిక:")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
