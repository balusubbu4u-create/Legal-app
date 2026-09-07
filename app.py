import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

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

            legal_system_instruction = """
మీరు భారతీయ క్రిమినల్ చట్టాలు (Bharatiya Nyaya Sanhita - BNS, Bharatiya Nagarik Suraksha Sanhita - BNSS, Bharatiya Sakshya Adhiniyam - BSA) పై ప్రావీణ్యం ఉన్న అధికారిక లీగల్ అసిస్టెంట్.

ముఖ్య నియమాలు:
1. ఇచ్చిన ఫిర్యాదు/చిత్రంలోని వాస్తవాల (facts) ఆధారంగా మాత్రమే ఖచ్చితమైన సెక్షన్లు పేర్కొనాలి.
2. చట్టపరమైన సెక్షన్లలో ఎలాంటి ఊహాజనిత (hallucinated) నంబర్లు చెప్పకూడదు. పూర్తి స్పష్టత లేని చోట "పరిశీలించాల్సిన సెక్షన్" అని మాత్రమే రాయాలి.
3. స్పష్టమైన Telugu లో క్రింది నిర్మాణం (Headings) లో మాత్రమే నివేదిక ఇవ్వాలి:

1. వర్తించే BNS Sections & Punishments
   - వర్తించే BNS సెక్షన్లు
   - శిక్షలు
   - అవసరమైతే పాత IPC సెక్షన్లతో పోలిక

2. BNSS Procedures
   - FIR / దర్యాప్తు ప్రక్రియ
   - నోటీసు ప్రొవిజన్లు (ఉదా: Sec 35 BNSS)
   - అరెస్ట్ నిబంధనలు
   - అవసరమైన ఇతర చట్టపరమైన చర్యలు

3. BSA Evidence Guidelines
   - పత్రాల ఆధారాలు (Documentary evidence)
   - ఎలక్ట్రానిక్ / డిజిటల్ ఆధారాల నిబంధనలు (BSA సెక్షన్ 61, 63 సర్టిఫికేషన్లు మొదలైనవి)
   - పంచనామా / సీజర్ పరిశీలనలు

4. IO (Investigating Officer) కోసం Step-by-Step Investigation Checklist
   - ప్రాథమిక చర్యలు
   - సాక్ష్యాధారాల సేకరణ
   - సాక్షుల విచారణ
   - తుది దర్యాప్తు దశలు

చివరలో తప్పనిసరిగా "గమనిక: ఇది ప్రాథమిక సమాచారం మాత్రమే; తుది చట్టపరమైన నిర్ణయాలకు నిపుణులను సంప్రదించాలి" అని రాయండి.
"""

            try:
                client = genai.Client(
                    api_key=st.secrets["GEMINI_API_KEY"]
                )

                config = types.GenerateContentConfig(
                    system_instruction=legal_system_instruction,
                    temperature=0.0,
                    top_p=0.95
                )

                content = []

                if uploaded_image:
                    content.append(uploaded_image)

                if case_text:
                    content.append(f"కేసు ఫిర్యాదు వివరాలు:\n{case_text}")
                else:
                    content.append("అప్‌లోడ్ చేసిన డాక్యుమెంట్ లేదా ఫోటోలోని వివరాలను చదివి పై నియమాల ప్రకారం విశ్లేషించండి.")

                try:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=content,
                        config=config
                    )
                except Exception as model_err:
                    if "503" in str(model_err) or "UNAVAILABLE" in str(model_err):
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=content,
                            config=config
                        )
                    else:
                        raise model_err

                st.markdown("### 📋 దర్యాప్తు నివేదిక:")
                st.markdown(response.text)

            except Exception as e:
                if "503" in str(e):
                    st.error("గూగుల్ సర్వర్లలో తాత్కాలిక రద్దీ ఉంది. దయచేసి ఒక నిమిషం తర్వాత మళ్లీ ప్రయత్నించండి.")
                else:
                    st.error(f"విశ్లేషణలో లోపం ఏర్పడింది: {e}")
