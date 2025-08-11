import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import requests
from io import BytesIO
from urllib.parse import quote
import base64
import time

# --- CONFIGURATION ---
genai.configure(api_key="your gemini api 🗝")
model = genai.GenerativeModel("gemini-1.5-flash")

st.set_page_config(
    page_title="✨ Kids Story Generator",
    page_icon="📚",
    layout="centered"
)

# --- CLEAN CSS STYLING ---
st.markdown("""
<style>
    /* Main colors */
    :root {
        --primary: #4a6fa5;
        --secondary: #6b8cae;
        --light: #f8f9fa;
        --dark: #343a40;
        --accent: #ff914d;
    }
    
    /* Base styles */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f5f7fa;
        color: var(--dark);
    }
    
    /* Header */
    .header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .header h1 {
        color: var(--primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        color: var(--secondary);
        font-size: 1.1rem;
    }
    
    /* Input card */
    .input-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Form elements */
    .stTextInput>div>div>input, 
    .stSelectbox>div>div>select,
    .stTextArea>div>div>textarea {
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }
    
    .stRadio>div {
        gap: 0.5rem;
    }
    
    .stRadio>div>label {
        margin-right: 0.5rem;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #3a5a8a !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    /* Results */
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-top: 1.5rem;
    }
    
    .story-text {
        line-height: 1.7;
        padding: 1rem 0;
        white-space: pre-line;
    }
    
    .illustration {
        border-radius: 8px;
        width: 100%;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: var(--secondary);
        font-size: 0.9rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header h1 {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="header">
    <h1>✨ Kids Story Generator</h1>
    <p>Create beautiful stories and poems for children with AI</p>
</div>
""", unsafe_allow_html=True)

# --- INPUT FORM ---
with st.container():
    st.markdown("### 📝 Create Your Story")
    with st.form("story_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            content_type = st.radio(
                "Type",
                ["Story", "Poem"],
                index=0,
                horizontal=True
            )
            
            theme = st.text_input(
                "Theme",
                "magical forest",
                help="E.g., space, jungle, underwater"
            )
            
        with col2:
            main_character = st.text_input(
                "Main character",
                "Luna",
                help="Name of the main character"
            )
            
            character_age = st.slider(
                "Character age",
                3, 12, 7
            )
        
        generate = st.form_submit_button("Generate Story")

# --- GENERATION ---
if generate:
    with st.spinner("Creating your story..."):
        progress_bar = st.progress(0)
        
        # Generate content
        prompt = (
            f"Write a {content_type.lower()} for children aged {character_age}-10 about {main_character} "
            f"in a {theme} setting. Make it engaging, imaginative, and educational with a positive message. "
            f"Use simple language and keep it under 300 words."
        )
        
        progress_bar.progress(30)
        response = model.generate_content(prompt)
        final_text = response.text.strip()
        
        progress_bar.progress(60)
        
        # Generate image
        image_prompt = (
            f"A children's book illustration of {main_character}, "
            f"a {character_age}-year-old, in a {theme} setting. "
            f"Whimsical, colorful, storybook style"
        )
        encoded_prompt = quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512"
        
        progress_bar.progress(80)
        
        image_data = None
        try:
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                image_data = image_response.content
        except Exception as e:
            st.error("Couldn't generate illustration")
        
        # Text to Speech
        tts = gTTS(final_text)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        progress_bar.progress(100)
        time.sleep(0.3)
        progress_bar.empty()

    # --- RESULTS ---
    st.markdown("---")
    st.markdown("### 📖 Your Creation")
    
    with st.container():
        st.markdown(f'<div class="story-text">{final_text}</div>', unsafe_allow_html=True)
        
        if image_data:
            st.image(image_data, use_column_width=True, caption="Generated Illustration")
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Story",
                    data=final_text,
                    file_name=f"{main_character}_{theme}_story.txt",
                    mime="text/plain"
                )
            with col2:
                st.download_button(
                    label="Download Image",
                    data=image_data,
                    file_name=f"{main_character}_{theme}_illustration.png",
                    mime="image/png"
                )
        
        st.markdown("### 🔊 Listen to Your Story")
        st.audio(audio_fp, format="audio/mp3")

# --- FOOTER ---
st.markdown("---")

st.markdown('<div class="footer">Made with ❤️ for young readers</div>', unsafe_allow_html=True)
