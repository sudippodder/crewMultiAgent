import streamlit as st
import os
from crew_pipeline import run_pipeline
#from huggingface_detector import detect_ai_generated  # NEW import
import requests
import time
from dotenv import load_dotenv
from functools import lru_cache
from display_editable_segments import display_editable_segments
from zerogpt_api import check_ai_content
from Generate_Content import generate_content_page
#from Content_Detection import detection_page


load_dotenv()
ZEROGPT_API_KEY = os.getenv("ZEROGPT_API_KEY")
ZEROGPT_API_URL = "https://api.zerogpt.com/api/detect/detectText"

# @st.cache_data(ttl=3600)
# def cached_detect_ai(text):
#     try:
#         return detect_ai_generated(text)
#     except Exception as e:
#         return {"error": str(e)}


# Session state
if "detection_result" not in st.session_state:
    st.session_state.detection_result = None

if "last_edit_time" not in st.session_state:
    st.session_state.last_edit_time = {}

if "edit_cache" not in st.session_state:
    st.session_state.edit_cache = {}



#st.set_page_config(page_title="Multi-Agent Content Generator", layout="wide")

st.title("🧠 Multi-Agent AI Content Generator V-1.0.2")

st.markdown("""
Enter your topic and optionally customize each agent’s **goal** and **backstory**.
The AI agents will research, write, and edit your Content collaboratively.\n"""
"""
This multi-agent system can be used anywhere content needs to be created, refined, and published regularly. Some examples include: SEO-friendly blogs and articles, generating social media posts, newsletters, campaign content , product descriptions, guides, promotional blogs, newsletters, announcements, reports.
""")

# --- GENERATE BUTTON ---
generate_content_page()



#detection_page()
