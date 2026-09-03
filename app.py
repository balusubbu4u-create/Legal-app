import streamlit as st
from google import genai
import tempfile
import time
import os

st.set_page_config(page_title="Gemini Document Analyzer", page_icon="📄")
st.title("📄 Gemini డాక్యుమెంట్ విశ్లేషణ")

API_KEY = "YOUR_GEMINI_API_KEY_HERE"
client = genai.Client(api_key=API_KEY)

# ఫైల్ అప్‌లోడర్
uploaded_file = st.file_uploader("PDF లేదా టెక్స్ట్ ఫైల్ అప్‌లోడ్ చేయండి:", type=["pdf", "txt"])
user_query = st.text_input("ఈ డాక్యుమెంట్ గురించి మీ ప్రశ్న:", value="ఈ డాక్యుమెంట్‌ను క్లుప్తంగా వివరించండి.")

if uploaded_file and st.button("విశ్లేషించు"):
    with st.spinner("ఫైల్ ప్రాసెస్ అవుతోంది..."):
        try:
            # 1. అప్‌లోడ్ చేసిన ఫైల్‌ను టెంపరరీగా సేవ్ చేయడం
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # 2. గూగుల్ ఫైల్స్ API కి అప్‌లోడ్ చేయడం
            doc_file = client.files.upload(file=tmp_path)
            
            # టెంప్ ఫైల్ తొలగించడం
            os.remove(tmp_path)

            # 3. 503 ఎర్రర్ వస్తే ఆటోమేటిక్‌గా 3 సార్లు ప్రయత్నించే లాజిక్
            max_retries = 3
            delay = 5
            response = None

            for attempt in range(1, max_retries + 1):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[doc_file, user_query]
                    )
                    break  # సక్సెస్ అయితే లూప్ ముగుస్తుంది
                except Exception as api_err:
                    if "503" in str(api_err) and attempt < max_retries:
                        st.info(f"సర్వర్‌లో రద్దీగా ఉంది, {delay} సెకన్లలో మళ్లీ ప్రయత్నిస్తున్నాం... (ప్రయత్నం {attempt}/{max_retries})")
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise api_err

            if response:
                st.success("విశ్లేషణ పూర్తయింది!")
                st.write("### ఫలితం:")
                st.write(response.text)

        except Exception as e:
            st.error(f"విశ్లేషణలో లోపం ఏర్పడింది: {e}")
