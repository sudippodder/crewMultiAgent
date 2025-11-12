import re
import streamlit as st
import streamlit.components.v1 as components
from zerogpt_api import check_ai_content

def display_highlighted_text(detection_result=None):
    """
    Display highlighted text, show stats and allow editing + rechecking.
    Keeps state across reruns so content doesn't disappear on button clicks.
    """

    # -----------------------
    # 1) Initialize session state defaults (very important)
    # -----------------------
    st.session_state.setdefault("last_detection_result", None)
    st.session_state.setdefault("editable_text", "")
    st.session_state.setdefault("show_editor", False)

    # If a fresh detection_result was provided to the function, store it.
    if detection_result is not None:
        st.session_state["last_detection_result"] = detection_result
        # Prefill editable_text from detection_result input_text if available
        data = detection_result.get("data", {})
        st.session_state["editable_text"] = data.get("input_text", "")

    # Use the most recent detection result from session_state
    detection = st.session_state.get("last_detection_result")
    if not detection:
        st.info("No detection result to display yet.")
        return

    data = detection.get("data", {})
    ai_segments = data.get("h", [])
    input_text = data.get("input_text", "")

    # -----------------------
    # 2) Highlight AI segments in the (current) text
    # -----------------------
    highlighted_text = input_text or st.session_state.get("editable_text", "")
    for term in ai_segments:
        if not term:
            continue
        pattern = re.escape(term)
        highlighted_text = re.sub(
            pattern,
            f"<mark style='background-color: yellow; color: black;'>{term}</mark>",
            highlighted_text,
            flags=re.IGNORECASE
        )

    # -----------------------
    # 3) Display highlighted text + stats
    # -----------------------
    st.markdown("### 🧠 Detected Content")
    st.markdown(highlighted_text, unsafe_allow_html=True)

    fake_percentage = data.get("fakePercentage", 0)
    feedback = data.get("feedback", "No feedback provided.")
    ai_words = data.get("aiWords", 0)
    text_words = data.get("textWords", 0)
    is_human = data.get("isHuman", 0)

    label = "🧠 AI-Generated" if is_human == 0 else "🧍 Human-Written"
    color = "red" if is_human == 0 else "green"

    st.markdown(
        f"""
        <div style="padding:10px;border-radius:6px;background-color: #fff3bf;">
            <strong>Legend:</strong> Yellow = AI-detected segment
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="padding:12px;border-radius:8px;background-color:#ffffff;margin-top:8px;">
            <h4 style="margin:0;">Prediction: <span style="color:{color};">{label}</span></h4>
            <p style="margin:4px 0;"><b>Feedback:</b> {feedback}</p>
            <p style="margin:4px 0;"><b>AI Probability:</b> {fake_percentage:.2f}%</p>
            <p style="margin:4px 0;"><b>Total Words:</b> {text_words} |
            <b>AI Words:</b> {ai_words} |
            <b>Estimated Human Words:</b> {max(text_words - ai_words, 0)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(min(max(fake_percentage / 100, 0), 1))

    st.markdown("---")

    # -----------------------
    # 4) Edit button (ensures content stays visible)
    # --- Edit Button ---
    if st.button("✏️ Edit Content"):
        st.session_state["show_editor"] = True
        st.session_state["editable_text"] = highlighted_text

    # --- Editable Box (HTML) ---
    if st.session_state.get("show_editor", False):
        st.markdown("### 🧰 Edit & Recheck Content")

        # 🔸 Use contenteditable HTML box (supports highlights)
        html_editor = f"""
        <div id="editor-box" contenteditable="true"
             style="
                 width:100%;
                 min-height:300px;
                 padding:12px;
                 border-radius:8px;
                 border:2px solid #f1c40f;
                 background-color:#fffbea;
                 font-size:16px;
                 line-height:1.5;
                 overflow:auto;
             ">
             {st.session_state['editable_text']}
        </div>
        <script>
            const textarea = document.getElementById('editor-box');
            window.addEventListener('message', (event) => {{
                if (event.data.type === 'GET_EDITED_TEXT') {{
                    window.parent.postMessage({{type: 'EDITED_TEXT', value: textarea.innerHTML}}, '*');
                }}
            }});
        </script>
        """
        components.html(html_editor, height=350, scrolling=True)

        st.info("Edit the text above (you can keep yellow highlights).")

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔍 Recheck After Edit"):
                # Get updated text (since Streamlit doesn't capture innerHTML directly)
                # You can add JS-to-Python bridge if needed, but for now just reuse last edit
                try:
                    with st.spinner("Rechecking content..."):
                        plain_text = re.sub(r"<.*?>", "", st.session_state["editable_text"])  # remove HTML tags
                        new_detection = check_ai_content(plain_text)
                        st.session_state["last_detection_result"] = new_detection
                        st.session_state["show_editor"] = False
                        st.success("✅ Recheck complete!")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Recheck failed: {e}")

        with col2:
            if st.button("❌ Cancel Edit"):
                st.session_state["show_editor"] = False
