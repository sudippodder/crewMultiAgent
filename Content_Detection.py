import streamlit as st
from zerogpt_api import check_ai_content
from display_editable_segments import display_editable_segments

def detection_page():
    st.title("🔍 AI Content Detector (ZeroGPT)")

    #user_text = st.text_area("Paste your text for analysis:", height=250)

    if "detection_result" not in st.session_state:
        st.session_state.detection_result = None

    # if st.button("Analyze Text"):
    #     if user_text.strip():
    #         with st.spinner("Checking with ZeroGPT..."):
    #             st.session_state.detection_result = check_ai_content(user_text)
    #     else:
    #         st.warning("Please paste some text first.")

    if st.session_state.detection_result:
        result = st.session_state.detection_result
        if "error" in result:
            st.error(result["error"])
        else:
            data = result.get("data", {})
            fake_percentage = data.get("fakePercentage", 0)
            ai_words = data.get("aiWords", 0)
            is_human = data.get("isHuman", 0)
            text_words = data.get("textWords", 0)
            feedback = data.get("feedback", "No feedback.")
            h_segments = data.get("h", [])
            hi_segments = data.get("hi", [])
            original_text = data.get("originalParagraph", "")

            label = "AI-Generated" if is_human == 0 else "Human-Written"
            label = "🧠 AI-Generated" if is_human == 0 else "🧍 Human-Written"
            color = "red" if is_human == 0 else "green"

            st.markdown(
                f"""
                <div style="padding:15px;border-radius:10px;background-color:{"#fff" if is_human == 0 else "#071D07"};">
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

            st.markdown(f"### Prediction: **{label}** ({fake_percentage:.2f}% AI probability)")
            st.info(feedback)
            st.progress(fake_percentage / 100)

            updated_result, needs_refresh = display_editable_segments(
                label="Suspected AI-Generated Segments",
                original_paragraph=original_text,
                segments=h_segments,
                detection_result=result,
            )

            # ✅ if user edited and rechecked text, update session state
            if needs_refresh:
                st.session_state.detection_result = updated_result
                st.rerun()

detection_page()
