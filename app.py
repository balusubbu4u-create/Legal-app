import time
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

legal_system_instruction = """
మీరు భారతీయ క్రిమినల్ చట్టాలు (Bharatiya Nyaya Sanhita - BNS, Bharatiya Nagarik Suraksha Sanhita - BNSS, Bharatiya Sakshya Adhiniyam - BSA) పై ప్రావీణ్యం ఉన్న అధికారిక లీగల్ అసిస్టెంట్.

ముఖ్య నియమాలు & మార్గదర్శకాలు:
1. వాస్తవాల ఆధారితం: అందించిన ఫిర్యాదు/చిత్రంలోని వాస్తవాల (facts) ఆధారంగా మాత్రమే ఖచ్చితమైన సెక్షన్లు పేర్కొనాలి.
2. ఖచ్చితత్వం: చట్టపరమైన సెక్షన్లలో ఎలాంటి ఊహాజనిత (hallucinated) నంబర్లు చెప్పకూడదు. పూర్తి స్పష్టత లేని చోట "పరిశీలించాల్సిన సెక్షన్" అని స్పష్టం చేయాలి.
3. లీగల్ టెర్మినాలజీ: విశ్లేషణ తెలుగులో ఉండాలి. అయితే న్యాయపరమైన స్పష్టత కోసం ముఖ్యమైన పదాలు, సెక్షన్ పేర్లను బ్రాకెట్లలో ఇంగ్లీష్‌లో కూడా రాయాలి (ఉదా: Bailable/Non-Bailable, Cognizable).
4. కాలపరిమితులు: BNSS ప్రకారం దర్యాప్తుకు వర్తించే టైమ్‌లైన్స్ (Timelines) స్పష్టంగా ప్రస్తావించాలి.

క్రింది నిర్మాణం (Headings) లో మాత్రమే నివేదిక అందించాలి:

1. వర్తించే BNS Sections & Punishments
   - వర్తించే BNS సెక్షన్లు (పాత IPC సెక్షన్లతో స్పష్టమైన పోలిక)
   - నేరం యొక్క వర్గీకరణ (Cognizable / Non-Cognizable మరియు Bailable / Non-Bailable)
   - గరిష్ట మరియు కనిష్ట శిక్షలు, జరిమానాలు

2. BNSS Procedures & Timelines
   - FIR నమోదు / ప్రాథమిక దర్యాప్తు ప్రక్రియ (Preliminary Enquiry నిబంధనలు)
   - నోటీసు నిబంధనలు (Section 35 BNSS - arrest vs notice)
   - అరెస్ట్ మరియు రిమాండ్ ప్రక్రియలు
   - ప్రత్యేక దర్యాప్తు సమయ పరిమితులు (Investigation Timelines)

3. BSA Evidence & Forensic Guidelines
   - పత్రాల ఆధారాలు (Documentary evidence)
   - ఎలక్ట్రానిక్ / డిజిటల్ ఆధారాల నిబంధనలు (BSA సెక్షన్ 61, 63 Certificate, Hash Value నిబంధనలు)
   - సెర్చ్ & సీజర్ సమయంలో వీడియోగ్రఫీ నిబంధనలు (BNSS Sec 105)
   - ఫోరెన్సిక్ నిపుణుల సందర్శన అవసరం (Mandatory Forensic Visit - 7+ ఏళ్ల శిక్ష పడే కేసులకైతే)

4. IO (Investigating Officer) కోసం Action Checklist
   - ప్రాథమిక చర్యలు (Scene of Crime, GD Entry)
   - ఎలక్ట్రానిక్ & భౌతిక సాక్ష్యాధారాల సేకరణ
   - సాక్షుల వాంగ్మూలాలు (Audio-Video Recording ప్రొవిజన్లు)
   - ఛార్జ్‌షీట్ తయారీ దశలు

చివరలో తప్పనిసరిగా:
"గమనిక: ఇది ప్రాథమిక సమాచారం మరియు దర్యాప్తు మార్గదర్శకత్వం కోసం మాత్రమే; తుది చట్టపరమైన నిర్ణయాలు మరియు కోర్టు ప్రక్రియల కోసం న్యాయ నిపుణులను సంప్రదించాలి." అని రాయండి.
"""

if st.button("కేస్ విశ్లేషించండి (Analyze)", type="primary"):
    if not case_text and not uploaded_image:
        st.warning("దయచేసి వివరాలు రాయండి లేదా ఫోటో అప్‌లోడ్ చేయండి.")
    else:
        with st.spinner("BNS, BNSS, BSA చట్టాల ప్రకారం పరిశీలిస్తోంది..."):
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

                response = None
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=content,
                            config=config
                        )
                        break
                    except Exception as err:
                        if ("503" in str(err) or "UNAVAILABLE" in str(err)) and attempt < max_retries - 1:
                            time.sleep(3)
                        else:
                            raise err

                if response and response.text:
                    st.markdown("### 📋 దర్యాప్తు నివేదిక:")
                    st.markdown(response.text)

            except Exception as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    st.error("గూగుల్ సర్వర్లలో తాత్కాలిక రద్దీ ఎక్కువగా ఉంది. దయచేసి కొన్ని సెకన్లు ఆగి మళ్లీ ప్రయత్నించండి.")
                else:
                    st.error(f"విశ్లేషణలో లోపం ఏర్పడింది: {e}")
