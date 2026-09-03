import streamlit as st
from PIL import Image
from google import genai

# మీ API Key ని ఇక్కడ ఉంచండి
GEMINI_API_KEY = "AQ.Ab8RN6IELJB2yhussCFa7xQXyAQf1U6VGs3xDlCn22nX5Ve-GA"

client = genai.Client(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="BNS Legal Assistant", page_icon="⚖️", layout="centered")

st.title("⚖️ BNS, BNSS & BSA లీగల్ అసిస్టెంట్")
st.write("కేసు వివరాలు నమోదు చేయండి లేదా ఫిర్యాదు కాపీ ఫోటో అప్‌లోడ్ చేయండి.")

tab1, tab2 = st.tabs(["📝 టెక్స్ట్ వివరాలు", "📷 ఫోటో / డాక్యుమెంట్"])

case_text = ""
uploaded_image = None

with tab1:
    text_input = st.text_area("ఫిర్యాదు వివరాలు ఇక్కడ రాయండి:", height=150)
    if text_input:
        case_text = text_input

with tab2:
    uploaded_file = st.file_uploader("ఫిర్యాదు కాపీ లేదా FIR ఫోటో ఎంచుకోండి", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="అప్‌లోడ్ చేసిన చిత్రం", use_container_width=True)

if st.button("కేస్ విశ్లేషించండి (Analyze)", type="primary"):
    if not case_text and not uploaded_image:
        st.warning("దయచేసి వివరాలు రాయండి లేదా ఫోటో అప్‌లోడ్ చేయండి.")
    else:
        with st.spinner("BNS, BNSS, BSA చట్టాల ప్రకారం పరిశీలిస్తోంది..."):
            prompt = """
            You are an expert Indian criminal law assistant. Analyze the given crime complaint (whether provided as text or an image in Telugu/English).

            Provide a clear and detailed structured output in Telugu (with English legal terms in brackets):
            1. **వర్తించే BNS సెక్షన్లు & శిక్షలు (Applicable BNS Sections & Punishments)**: పూర్వపు IPC సెక్షన్లతో పోల్చి చెప్పండి.
            2. **BNSS ప్రకారం తీసుకోవాల్సిన చర్యలు (BNSS Procedures)**: నోటీసులు (Sec 35(3)), అరెస్ట్ నిబంధనలు, ఫోరెన్సిక్ టీమ్ విజిట్.
            3. **BSA ప్రకారం సాక్ష్యాధారాల సేకరణ (Evidence Guidelines under BSA)**: ఎలక్ట్రానిక్ ఆధారాలు (Sec 63 సర్టిఫికేట్), పంచనామా.
            4. **దర్యాప్తు అధికారికి దశలవారీ మార్గదర్శకాలు (Step-by-Step Investigation SOP for IO)**.
            """
            try:
                contents = [prompt]
                if uploaded_image:
                    contents.append(uploaded_image)
                if case_text:
                    contents.append(f"అదనపు వివరాలు: {case_text}")

                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents
                )
                st.markdown("### 📋 దర్యాప్తు నివేదిక:")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"విశ్లేషణలో లోపం ఏర్పడింది: {e}")
