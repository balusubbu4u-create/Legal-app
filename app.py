import streamlit as st
from PIL import Image
from google import genai


# --------------------------------------------------
# Page settings
# --------------------------------------------------

st.set_page_config(
    page_title="Legal Case Analyzer",
    page_icon="⚖️",
    layout="wide"
)


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("⚖️ కేస్ విశ్లేషణ (Analyze)")
st.write("కేసుకు సంబంధించిన వివరాలను నమోదు చేసి విశ్లేషణ పొందండి.")


# --------------------------------------------------
# Gemini Client
# --------------------------------------------------

try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception as e:
    st.error("Gemini API Key లో సమస్య ఉంది.")
    st.error(str(e))
    st.stop()


# --------------------------------------------------
# Prompt
# --------------------------------------------------

prompt = """
మీరు ఒక Legal Case Analysis Assistant.

క్రింద ఇచ్చిన కేసు వివరాలను జాగ్రత్తగా విశ్లేషించండి.

దయచేసి ఈ క్రింది అంశాల ప్రకారం సమాధానం ఇవ్వండి:

1. కేసు సంక్షిప్త వివరణ
2. ముఖ్యమైన వాస్తవాలు
3. ప్రధాన ఆరోపణలు / సమస్యలు
4. అందుబాటులో ఉన్న ఆధారాలు
5. ఆధారాలలో ఉన్న బలాలు
6. ఆధారాలలో ఉన్న బలహీనతలు
7. సంఘటనల కాలక్రమం
8. ఇంకా అవసరమైన సమాచారం
9. తదుపరి దర్యాప్తులో పరిశీలించాల్సిన అంశాలు
10. తుది విశ్లేషణ

ఇది సాధారణ సమాచార/విశ్లేషణ కోసం మాత్రమే.
చట్టపరమైన తుది నిర్ణయంగా పరిగణించకూడదు.
"""


# --------------------------------------------------
# Case details
# --------------------------------------------------

case_text = st.text_area(
    "కేసు వివరాలు నమోదు చేయండి:",
    height=250,
    placeholder="ఇక్కడ కేసుకు సంబంధించిన పూర్తి వివరాలను నమోదు చేయండి..."
)


# --------------------------------------------------
# Image upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "కేసుకు సంబంధించిన చిత్రం / Screenshot upload చేయండి (Optional)",
    type=["jpg", "jpeg", "png"]
)

uploaded_image = None

if uploaded_file is not None:
    try:
        uploaded_image = Image.open(uploaded_file)

        st.image(
            uploaded_image,
            caption="Uploaded Image",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Image open చేయడంలో సమస్య: {e}")


# --------------------------------------------------
# Analyze button
# --------------------------------------------------

if st.button("🔍 Analyze Case", type="primary"):

    if not case_text.strip() and uploaded_image is None:
        st.warning("దయచేసి కేసు వివరాలు లేదా image కనీసం ఒకటి ఇవ్వండి.")
        st.stop()

    try:

        # ------------------------------------------
        # Content
        # ------------------------------------------

        content = [prompt]

        if case_text.strip():
            content.append(
                f"""
కేసు వివరాలు:

{case_text}
"""
            )

        if uploaded_image is not None:
            content.append(uploaded_image)


        # ------------------------------------------
        # Gemini request
        # ------------------------------------------

        with st.spinner("కేసును విశ్లేషిస్తోంది..."):

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=content
            )


        # ------------------------------------------
        # Result
        # ------------------------------------------

        st.markdown("### 📋 దర్యాప్తు నివేదిక:")

        if response.text:
            st.markdown(response.text)
        else:
            st.warning("Gemini నుంచి text response రాలేదు.")


    # ----------------------------------------------
    # Error handling
    # ----------------------------------------------

    except Exception as e:

        error_message = str(e)

        if "503" in error_message or "UNAVAILABLE" in error_message:

            st.error(
                "Gemini model ప్రస్తుతం అధిక వినియోగంలో ఉంది. "
                "కొద్దిసేపటి తర్వాత మళ్లీ ప్రయత్నించండి."
            )

        elif "API key" in error_message or "api_key" in error_message:

            st.error(
                "Gemini API Key లో సమస్య ఉంది. "
                "Streamlit Secrets లో GEMINI_API_KEY సరిగ్గా ఉందో చూడండి."
            )

        else:

            st.error(
                f"విశ్లేషణలో లోపం ఏర్పడింది:\n\n{error_message}"
)
