import streamlit as st
from PIL import Image
from google import genai

st.set_page_config(
    page_title="BNS Legal Assistant",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ BNS, BNSS & BSA లీగల్ అసిస్టెంట్")
st.write("కేసు వివరాలు నమోదు చేయండి లేదా ఫిర్యాదు కాపీ ఫోటో అప్‌లోడ్ చేయండి.")

tab1, tab2 = st.tabs(["📝 టెక్స్ట్ వివరాలు", "📷 ఫోటో / డాక్యుమెంట్"])

case_text = ""
uploaded_image = None

with tab1:
    text_input = st.text_area(
        "ఫిర్యాదు వివరాలు ఇక్కడ రాయండి:",
        height=150
    )

    if text_input:
        case_text = text_input

with tab2:
    uploaded_file = st.file_uploader(
        "ఫిర్యాదు కాపీ లేదా FIR ఫోటో ఎంచుకోండి",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        uploaded_image = Image.open(uploaded_file)

        st.image(
            uploaded_image,
            caption="అప్‌లోడ్ చేసిన చిత్రం",
            use_container_width=True
        )

if st.button("కేస్ విశ్లేషించండి (Analyze)", type="primary"):

    if not case_text and not uploaded_image:
        st.warning("దయచేసి వివరాలు రాయండి లేదా ఫోటో అప్‌లోడ్ చేయండి.")

    else:
        with st.spinner("BNS, BNSS, BSA చట్టాల ప్రకారం పరిశీలిస్తోంది..."):

            prompt = """
మీరు భారతీయ క్రిమినల్ లా గురించి సమాచారాన్ని అందించే
లీగల్ అసిస్టెంట్.

ఇచ్చిన ఫిర్యాదు వివరాలను Teluguలో విశ్లేషించండి.
చట్టంలోని తాజా provisions ను ఖచ్చితంగా verify చేయాల్సిన
అవసరం ఉన్న చోట స్పష్టంగా సూచించండి.

కింది headingsలో structured output ఇవ్వండి:

1. వర్తించే BNS Sections & Punishments
   - వర్తించే BNS సెక్షన్లు
   - శిక్షలు
   - అవసరమైతే పాత IPC sectionతో పోలిక

2. BNSS Procedures
   - FIR / investigation procedure
   - Notice provisions
   - Arrest-related provisions
   - అవసరమైన procedural steps

3. BSA Evidence Guidelines
   - Documentary evidence
   - Electronic evidence
   - Digital evidence requirements
   - Panchanama / seizure-related considerations

4. IO కోసం Step-by-Step Investigation Checklist
   - మొదట చేయాల్సిన పని
   - Evidence collection
   - Witness examination
   - Documents
   - Final investigation steps

ముఖ్యమైన చట్టపరమైన నిర్ణయాలను ఖచ్చితమైన facts
ఆధారంగా మాత్రమే ఇవ్వండి. అవసరమైతే "ఇది సాధారణ
చట్టపరమైన సమాచారం మాత్రమే; కేసు facts ఆధారంగా
న్యాయ నిపుణుడిని సంప్రదించాలి" అని సూచించండి.
"""

            try:

                # API key Streamlit Secrets నుండి తీసుకుంటుంది
                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                content = [prompt]

                if uploaded_image:
                    content.append(uploaded_image)

                if case_text:
                    content.append(
                        f"అదనపు కేసు వివరాలు:\n{case_text}"
                    )

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=content
                )

                st.markdown("### 📋 దర్యాప్తు నివేదిక:")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"విశ్లేషణలో లోపం ఏర్పడింది: {e}")
