import streamlit as st
from google import genai
import tempfile
import time
import os

st.set_page_config(page_title="Gemini AI All-in-One", page_icon="🤖")
st.title("🤖 Gemini AI తెలుగు అసిస్టెంట్")

# మీ API కీ
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
client = genai.Client(api_key=API_KEY)

# 1. డాక్యుమెంట్ అప్‌లోడర్ (ఐచ్ఛికం - Optional)
uploaded_file = st.file_uploader("డాక్యుమెంట్ ఉంటే ఇక్కడ అప్‌లోడ్ చేయండి (PDF, TXT, ఇమేజ్ మొదలైనవి):", type=["pdf", "txt", "png", "jpg", "jpeg"])

# 2. టెక్స్ట్ ప్రశ్న (తప్పనిసరి)
user_prompt = st.text_area("మీ ప్రశ్న ఇక్కడ టైప్ చేయండి:", placeholder="ఉదా: సాధారణ ప్రశ్న అడగండి లేదా పైన అప్‌లోడ్ చేసిన ఫైల్ గురించి అడగండి...")

# 503 ఎర్రర్ వస్తే రీట్రై చేసే ఫంక్షన్
def generate_with_retry(contents_list, max_retries=3, delay=5):
    for attempt in range(1, max_retries + 1):
        try:
            return client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents_list
            )
        except Exception as err:
            if "503" in str(err) and attempt < max_retries:
                st.warning(f"సర్వర్ బిజీగా ఉంది. {delay} సెకన్లలో మళ్లీ ప్రయత్నిస్తున్నాం... (ప్రయత్నం {attempt}/{max_retries})")
                time.sleep(delay)
                delay *= 2
            else:
                raise err

# సమాధానం బటన్
if st.button("సమాధానం పంపు"):
    if not user_prompt.strip() and not uploaded_file:
        st.warning("దయచేసి ఏదైనా ప్రశ్న రాయండి లేదా ఫైల్ అప్‌లోడ్ చేయండి!")
    else:
        with st.spinner("సమాధానం రూపొందిస్తోంది..."):
            try:
                contents = []

                # ఫైల్ ఉంటే ప్రాసెస్ చేయడం
                if uploaded_file is not None:
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    # Files API ద్వారా అప్‌లోడ్
                    uploaded_doc = client.files.upload(file=tmp_path)
                    contents.append(uploaded_doc)
                    os.remove(tmp_path)

                # యూజర్ రాసిన ప్రశ్నను జత చేయడం
                prompt_text = user_prompt.strip() if user_prompt.strip() else "ఈ ఫైల్‌లోని ముఖ్యమైన వివరాలను వివరించండి."
                contents.append(prompt_text)

                # కాల్ చేయడం
                response = generate_with_retry(contents)

                st.success("పూర్తయింది!")
                st.write("### సమాధానం:")
                st.write(response.text)

            except Exception as e:
                st.error(f"ఎర్రర్ ఏర్పడింది: {e}")
