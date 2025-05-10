
import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import tempfile
from PIL import Image

load_dotenv()

# Configure Gemini - use the new model names
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize the Gemini model - using the newer 1.5 models
vision_model = genai.GenerativeModel('gemini-1.5-flash')  # or 'gemini-1.5-pro'
text_model = genai.GenerativeModel('gemini-1.5-flash')  # for text explanations

# Sample prompt for medical analysis
sample_prompt = """
You are a medical practitioner and an expert in analyzing medical-related images working for a very reputed hospital.
You will be provided with images, and you need to identify anomalies, diseases, or health issues.
Your response should include:
1. Detailed findings from the image
2. Possible conditions or diagnoses
3. Recommended next steps
4. A disclaimer: "Consult with a Doctor before making any decisions."

If certain aspects are unclear from the image, state: "Unable to determine based on the provided image."

Analyze the image and respond in a structured manner.
"""

# Initialize session state variables
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'result' not in st.session_state:
    st.session_state.result = None

def call_gemini_model_for_analysis(image_path, prompt=sample_prompt):
    img = Image.open(image_path)
    
    # For the newer models, we need to prepare the content differently
    response = vision_model.generate_content(
        contents=[prompt, img],
        generation_config={
            "temperature": 0.1,  # More deterministic responses
            "max_output_tokens": 2048
        }
    )
    return response.text

def chat_eli(query):
    eli5_prompt = "Explain this to a five-year-old: \n" + query
    response = text_model.generate_content(eli5_prompt)
    return response.text

# Streamlit UI
st.title("Medical Help using Multimodal LLM (Gemini)")

with st.expander("About this App"):
    st.write("Upload a medical image (X-ray, MRI, skin condition, etc.) to get an AI-powered analysis from Google Gemini.")

uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

# Temporary file handling
if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state['filename'] = tmp_file.name

    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)

# Process button
if st.button('Analyze Image'):
    if 'filename' in st.session_state and os.path.exists(st.session_state['filename']):
        with st.spinner("Analyzing the image..."):
            st.session_state['result'] = call_gemini_model_for_analysis(st.session_state['filename'])
            st.markdown(st.session_state['result'], unsafe_allow_html=True)
            os.unlink(st.session_state['filename'])  # Delete the temp file after processing

# ELI5 Explanation
if 'result' in st.session_state and st.session_state['result']:
    st.info("Want a simpler explanation? Use ELI5 (Explain Like I'm 5)!")
    if st.radio("ELI5 - Explain Like I'm 5", ('No', 'Yes')) == 'Yes':
        simplified_explanation = chat_eli5(st.session_state['result'])
        st.markdown(simplified_explanation, unsafe_allow_html=True)

# Disclaimer
st.warning("⚠️ **Disclaimer**: This AI tool provides preliminary insights and is not a substitute for professional medical advice. Always consult a qualified doctor for diagnosis and treatment.")
