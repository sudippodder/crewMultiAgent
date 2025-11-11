import streamlit as st
import os
from crew_pipeline import run_pipeline
#from huggingface_detector import detect_ai_generated  # NEW import
import requests
import time
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()
ZEROGPT_API_KEY = os.getenv("ZEROGPT_API_KEY")
ZEROGPT_API_URL = "https://api.zerogpt.com/api/detect/detectText"

# @st.cache_data(ttl=3600)
# def cached_detect_ai(text):
#     try:
#         return detect_ai_generated(text)
#     except Exception as e:
#         return {"error": str(e)}
    
def display_editable_segments(label: str, original_paragraph: str, segments: list, detection_result: dict):
    """
    Reusable component that shows editable AI-suspected segments.
    On save: calls ZeroGPT API and returns the updated detection_result.
    
    Args:
        label (str): Section title for the UI (e.g., "Suspected AI Segments")
        original_paragraph (str): Full text analyzed
        segments (list): List of suspected AI segments
        detection_result (dict): Current ZeroGPT detection data

    Returns:
        dict: Updated detection_result after re-check (if any changes were saved)
    """
    st.subheader(f"🚨 {label}")

    if not segments:
        st.info("No suspected AI segments found.")
        return detection_result

    # Initialize session keys
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = {}
    if "edit_buffers" not in st.session_state:
        st.session_state.edit_buffers = {}

    for idx, segment in enumerate(segments):
        seg_key = f"{label}_segment_{idx}"
        buf_key = f"{seg_key}_buffer"
        edit_key = f"{seg_key}_edit"

        if buf_key not in st.session_state:
            st.session_state[buf_key] = segment
        if edit_key not in st.session_state:
            st.session_state[edit_key] = False

        st.markdown(f"**Segment {idx + 1}**")

        seg_col, btn_col = st.columns([0.85, 0.15])
        with seg_col:
            if st.session_state[edit_key]:
                edited = st.text_area(
                    label=f"Edit segment {idx + 1}",
                    value=st.session_state[buf_key],
                    key=f"{seg_key}_edit_area",
                    height=140,
                )
                st.session_state[buf_key] = edited
            else:
                st.markdown(
                    f"<div style='padding:10px;border-radius:6px;background:#fff6f6'>{segment}</div>",
                    unsafe_allow_html=True,
                )

        with btn_col:
            if not st.session_state[edit_key]:
                if st.button("Edit", key=f"{seg_key}_edit_btn"):
                    st.session_state[edit_key] = True
                    st.session_state[buf_key] = segment
                    st.experimental_rerun()
            else:
                if st.button("Save", key=f"{seg_key}_save_btn"):
                    edited_text = st.session_state[buf_key].strip()
                    if not edited_text:
                        st.warning("Edited segment cannot be empty.")
                    else:
                        full_text = original_paragraph
                        if segment in full_text:
                            new_full = full_text.replace(segment, edited_text, 1)
                        else:
                            new_full = full_text.replace(" ".join(segment.split()), " ".join(edited_text.split()), 1)

                        with st.spinner("Re-checking updated text with ZeroGPT..."):
                            recheck = check_ai_content(new_full)
                            if "error" in recheck:
                                st.error(f"Recheck failed: {recheck['error']}")
                            else:
                                st.session_state[edit_key] = False
                                st.success("Segment updated and rechecked successfully.")
                                return recheck  # Return updated detection result

                if st.button("Cancel", key=f"{seg_key}_cancel_btn"):
                    st.session_state[edit_key] = False
                    st.session_state[buf_key] = segment
                    st.experimental_rerun()

    return detection_result  # Default return if no edits were saved


# Session state
if "detection_result" not in st.session_state:
    st.session_state.detection_result = None

if "last_edit_time" not in st.session_state:
    st.session_state.last_edit_time = {}

if "edit_cache" not in st.session_state:
    st.session_state.edit_cache = {}

    
def check_ai_content(text):
    """Check whether the given text is AI-generated using ZeroGPT API."""
    headers = {
        "ApiKey": ZEROGPT_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"input_text": text}

    try:
        response = requests.post(ZEROGPT_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        #st.write("### 🔍 ZeroGPT Raw Response:", result)

        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "data": data,
                "confidence": data.get("confidence"),
                "message": data.get("message", "Detection completed.")
            }
        else:
            return {"error": f"Unexpected response structure: {result}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}
    
st.set_page_config(page_title="Multi-Agent Content Generator", layout="wide")

st.title("🧠 Multi-Agent AI Content Generator")

st.markdown("""
Enter your topic and optionally customize each agent’s **goal** and **backstory**.
The AI agents will research, write, and edit your Content collaboratively.\n"""
"""
This multi-agent system can be used anywhere content needs to be created, refined, and published regularly. Some examples include: SEO-friendly blogs and articles, generating social media posts, newsletters, campaign content , product descriptions, guides, promotional blogs, newsletters, announcements, reports.
""")

# --- INPUTS ---
st.subheader("📝 Topic")
topic = st.text_input("Enter the topic:", placeholder="e.g. AI tools for marketing")

st.subheader("🎯 Customize Agent Behavior")

with st.expander("🧑‍🔬 Researcher Settings", expanded=True):
    researcher_goal = st.text_area(
        "Researcher Goal",
        value="Find and summarize useful content for the given topic.",
        height=80
    )
    researcher_backstory = st.text_area(
        "Researcher Backstory",
        value="You're great at finding relevant sources online and summarizing key insights.",
        height=80
    )

with st.expander("✍️ Writer Settings", expanded=True):
    writer_goal = st.text_area(
        "Writer Goal",
        value="Write a detailed, SEO-friendly blog post using the research.",
        height=80
    )
    writer_backstory = st.text_area(
        "Writer Backstory",
        value="You're a professional writer skilled at clarity, engagement, and structure.",
        height=80
    )

with st.expander("🧑‍🏫 Editor Settings", expanded=True):
    editor_goal = st.text_area(
        "Editor Goal",
        value="Polish and refine the blog content for tone, clarity, and grammar.",
        height=80
    )
    editor_backstory = st.text_area(
        "Editor Backstory",
        value="You ensure every piece reads naturally, is error-free, and maintains a consistent tone.",
        height=80
    )

# --- GENERATE BUTTON ---
if st.button("🚀 Generate Content"):
    if topic.strip():
        with st.spinner("🤖 Agents are collaborating..."):
            try:
                result = run_pipeline(
                    topic,
                    researcher_goal,
                    researcher_backstory,
                    writer_goal,
                    writer_backstory,
                    editor_goal,
                    editor_backstory
                )
                st.success("✅ Generation complete!")
                st.markdown(result)
                with st.expander("🧠 Check if this content is AI-generated", expanded=False):
                    detection_result = check_ai_content(result)
                    #st.write(f"""### 🔍 json: {detection_result} """)
                    if "error" in detection_result:
                        st.error(detection_result["error"])
                    else:
                        st.markdown("### 🧾 ZeroGPT Detection Result")

                        data = detection_result.get("data", {})

                        fake_percentage = data.get("fakePercentage", 0)
                        ai_words = data.get("aiWords", 0)
                        text_words = data.get("textWords", 0)
                        is_human = data.get("isHuman", 0)
                        feedback = data.get("feedback", "No feedback provided.")
                        h_segments = data.get("h", [])
                        hi_segments = data.get("hi", [])
                        original_text = data.get("originalParagraph", "")

                        # Display summary
                        label = "🧠 AI-Generated" if is_human == 0 else "🧍 Human-Written"
                        color = "red" if is_human == 0 else "green"

                        st.markdown(
                            f"""
                            <div style="padding:15px;border-radius:10px;background-color:{"#000000" if is_human == 0 else '#ccffcc'};">
                                <h4 style="margin:0;">Prediction: <span style="color:{color};">{label}</span></h4>
                                <p style="margin:5px 0;"><b>Feedback:</b> {feedback}</p>
                                <p style="margin:5px 0;"><b>AI Probability:</b> {fake_percentage:.2f}%</p>
                                <p style="margin:5px 0;"><b>Total Words:</b> {text_words} |
                                <b>AI Words:</b> {ai_words} |
                                <b>Estimated Human Words:</b> {max(text_words - ai_words, 0)}</p>
                            </div>
                            
                            """,
                            unsafe_allow_html=True,
                        )
                        st.progress(min(max(fake_percentage / 100, 0), 1))

                        # --- AI Segments ---
                        
                        # --- Human Segments ---
                        if hi_segments:
                            st.subheader("✅ Likely Human-Written Segments")
                            for segment in hi_segments[:5]:
                                st.markdown(
                                    f"<div style='background:#eaffea;padding:10px;border-radius:8px;margin-bottom:8px;'>{segment}</div>",
                                    unsafe_allow_html=True,
                                )

                        updated_result = display_editable_segments(
                            label="Suspected AI-Generated Segments",
                            original_paragraph=original_text,
                            segments=h_segments,
                            detection_result=detection_result,
                        )

                        # If recheck happened, update global result
                        if updated_result != detection_result:
                            st.session_state["detection_result"] = updated_result
                            st.experimental_rerun()
                        # --- Human Segments ---
                        if hi_segments:
                            st.subheader("✅ Likely Human-Written Segments")
                            for segment in hi_segments[:5]:
                                st.markdown(f"<div style='background:#eaffea;padding:10px;border-radius:8px;margin-bottom:8px;'>{segment}</div>", unsafe_allow_html=True)
                        else:
                            st.warning("No clearly human-written segments found.")

                        # --- Original Text ---
                        st.subheader("📄 Original Text (Analyzed)")
                        st.text_area("Detected Text", original_text, height=300)

                        # --- Raw JSON ---
                        # with st.expander("🧩 View Full JSON Response"):
                        #     st.json(detection_result)

                    # with st.expander("🔍 View Detailed Detection Data"):
                    #     st.json(detection_result)



                st.markdown("---")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic first.")
