import streamlit as st

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

import azure.cognitiveservices.speech as speechsdk

import time

# =========================
# AZURE CONFIGURATION
# =========================

# OCR Service
VISION_KEY = "YOUR_VISION_KEY"
VISION_ENDPOINT = "YOUR_VISION_ENDPOINT"

# Speech Service
SPEECH_KEY = "YOUR_SPEECH_KEY"
SPEECH_REGION = "eastus"

# =========================
# STREAMLIT UI
# =========================

st.title("✨ Readify AI")
st.subheader("AI Powered OCR & Speech Recognition System")
st.sidebar.title("📌 Features")

st.sidebar.info(
    """
    ✔ Image To Text  
    ✔ OCR Technology  
    ✔ Text To Speech  
    ✔ Speech To Text  
    ✔ AI Based Application
    """
)

option = st.selectbox(
    "Choose Input Type",
    ["Image To Text", "Speech To Blog"]
)

# =========================
# OCR FUNCTION
# =========================

def extract_text_from_image(image_file):

    # Create OCR Client
    client = ComputerVisionClient(
        VISION_ENDPOINT,
        CognitiveServicesCredentials(VISION_KEY)
    )

    # Read Image
    read_response = client.read_in_stream(
        image_file,
        raw=True
    )

    # Get Operation ID
    operation_id = read_response.headers["Operation-Location"].split("/")[-1]

    # Wait for OCR Result
    while True:

        result = client.get_read_result(operation_id)

        if result.status not in ["notStarted", "running"]:
            break

        time.sleep(1)

    extracted_text = ""

    # Extract Text
    if result.status == "succeeded":

        for page in result.analyze_result.read_results:

            for line in page.lines:

                extracted_text += line.text + " "

    return extracted_text

# =========================
# TEXT TO SPEECH FUNCTION
# =========================

def text_to_speech(text):

    # Speech Configuration
    speech_config = speechsdk.SpeechConfig(
        subscription=SPEECH_KEY,
        region=SPEECH_REGION
    )

    # Voice Selection
    speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    # Output File
    output_file = "output_audio.wav"

    # Audio Config
    audio_config = speechsdk.audio.AudioConfig(
        filename=output_file
    )

    # Create Synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    # Convert Text to Speech
    synthesizer.speak_text_async(text).get()

    return output_file

# =========================
# IMAGE TO TEXT
# =========================

if option == "Image To Text":

    uploaded_image = st.file_uploader(
        "Upload Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_image is not None:

        st.image(uploaded_image, caption="Uploaded Image")

        if st.button("Extract Text"):

            # OCR
            extracted_text = extract_text_from_image(uploaded_image)

            # Display Extracted Text
            st.subheader("Extracted Text")
            st.write(extracted_text)

            # Generate Audio
            audio_file = text_to_speech(extracted_text)

            # Play Audio
            st.subheader("Audio Output")

            audio = open(audio_file, "rb")

            st.audio(audio.read())

# =========================
# SPEECH TO BLOG
# =========================

# =========================
# SPEECH TO TEXT
# =========================

elif option == "Speech To Blog":

    uploaded_audio = st.file_uploader(
        "Upload Audio",
        type=["wav"]
    )

    if uploaded_audio is not None:

        st.audio(uploaded_audio)
        

        # Save uploaded audio
        with open("uploaded_audio.wav", "wb") as f:
            f.write(uploaded_audio.read())

        if st.button("Convert Speech To Text"):

            # Speech Config
            speech_config = speechsdk.SpeechConfig(
                subscription=SPEECH_KEY,
                region=SPEECH_REGION
            )

            # Audio Config
            audio_config = speechsdk.audio.AudioConfig(
                filename="uploaded_audio.wav"
            )

            # Speech Recognizer
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )

            st.write("Converting speech to text...")

            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:

                st.subheader("Converted Text")
                st.write(result.text)

            else:

                st.error("Speech could not be recognized")
                #to run:  python -m streamlit run app.py