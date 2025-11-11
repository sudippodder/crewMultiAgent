import streamlit as st
import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()
ZEROGPT_API_KEY = os.getenv("ZEROGPT_API_KEY")

# === CONFIG ===
ZEROGPT_API_URL = "https://api.zerogpt.com/api/detect/detectText"


# === HELPER FUNCTION ===
def check_ai_content(text):
    headers = {"ApiKey": ZEROGPT_API_KEY, "Content-Type": "application/json"}
    data = {"input_text": text}
    try:
        response = requests.post(ZEROGPT_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"ZeroGPT API Error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": str(e)}


# === STREAMLIT APP ===
#st.set_page_config(page_title="AI Text Detection", layout="wide")
st.title("🧠 Real-Time AI Content Detection Dashboard")

# Session state
if "detection_result" not in st.session_state:
    st.session_state.detection_result = None

if "last_edit_time" not in st.session_state:
    st.session_state.last_edit_time = {}

if "edit_cache" not in st.session_state:
    st.session_state.edit_cache = {}

# Input area
text_input = st.text_area("Enter or Paste Your Blog/Text Here:", height=250)

if st.button("Check AI Content"):
    with st.spinner("Analyzing with ZeroGPT..."):
        result = check_ai_content(text_input)
        st.session_state.detection_result = result

# === DISPLAY RESULTS ===
if st.session_state.detection_result:
    result = st.session_state.detection_result
    if "error" in result:
        st.error(result["error"])
    else:
        data = result.get("data", {})
        fake_percentage = data.get("fakePercentage", 0)
        is_human = data.get("isHuman", 0)
        feedback = data.get("feedback", "No feedback provided.")
        h_segments = data.get("h", [])
        hi_segments = data.get("hi", [])

        label = "🧠 AI-Generated" if is_human == 0 else "🧍 Human-Written"
        color = "#ffcccc" if is_human == 0 else "#ccffcc"

        st.markdown(
            f"""
            <div style="padding:15px;border-radius:10px;background-color:{color};">
                <h4>Prediction: {label}</h4>
                <p><b>AI Probability:</b> {fake_percentage:.2f}%</p>
                <p><b>Feedback:</b> {feedback}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # --- Editable AI Segments ---
        if h_segments:
            st.subheader("🚨 Suspected AI-Generated Segments (Auto-Recheck)")

            for idx, segment in enumerate(h_segments):
                st.markdown(f"**Segment {idx+1}:**")
                key = f"edit_segment_{idx}"

                edited_text = st.text_area(
                    f"Edit Segment {idx+1}",
                    st.session_state.edit_cache.get(key, segment),
                    key=key,
                    height=100,
                )

                # Save to cache
                st.session_state.edit_cache[key] = edited_text

                # Detect typing delay
                current_time = time.time()
                last_time = st.session_state.last_edit_time.get(key, 0)

                # If user stopped typing for >1.5 seconds → auto recheck
                if abs(current_time - last_time) > 1.5:
                    st.session_state.last_edit_time[key] = current_time
                    with st.spinner(f"Rechecking Segment {idx+1}..."):
                        re_result = check_ai_content(edited_text)
                        if "error" in re_result:
                            st.error(re_result["error"])
                        else:
                            re_data = re_result.get("data", {})
                            re_fake_percentage = re_data.get("fakePercentage", 0)
                            re_is_human = re_data.get("isHuman", 0)
                            re_feedback = re_data.get("feedback", "")
                            color = "#ccffcc" if re_is_human == 1 else "#ffcccc"

                            st.markdown(
                                f"""
                                <div style="padding:10px;border-radius:8px;background-color:{color};">
                                    <p><b>New Feedback:</b> {re_feedback}</p>
                                    <p><b>AI Probability:</b> {re_fake_percentage:.2f}%</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

        # --- Human Segments ---
        if hi_segments:
            st.subheader("✅ Likely Human-Written Segments")
            for segment in hi_segments[:5]:
                st.markdown(
                    f"<div style='background:#eaffea;padding:10px;border-radius:8px;margin-bottom:8px;'>{segment}</div>",
                    unsafe_allow_html=True,
                )

        with st.expander("📄 Raw Detection Data"):
            st.json(result)
