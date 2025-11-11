import re
import streamlit as st

def highlight_ai_segments(original_text, ai_segments, human_segments):
    """
    Highlight AI-generated and human-written parts of the text.
    """
    highlighted_text = original_text

    # Text inputs
    # original_text = st.text_area("Enter the full text:", height=200)
    # ai_segments = st.text_input("Enter the text to highlight:")

    # ot = st.markdown(f"<<<<< {original_text}")
    # ais = st.markdown(f" >>>>  {ai_segments}")
    for term in ai_segments:
        pattern = re.escape(term)
        highlighted_text = re.sub(
            pattern,
            f"<mark style='background-color: yellow; color: black;'>{term}</mark>",
            highlighted_text,
            flags=re.IGNORECASE
        )

    # if original_text:
    #     if ai_segments:
    #         # Escape regex special characters in ai_segments
    #         pattern = re.escape(ai_segments)
    #         # Replace all matches with highlighted HTML
    #         highlighted_text = re.sub(
    #             pattern,
    #             f"<mark style='background-color: yellow; color: black;'>{ai_segments}</mark>",
    #             original_text,
    #             flags=re.IGNORECASE
    #         )
    #     else:
    #         highlighted_text = original_text

        # Display highlighted text using Markdown with HTML enabled
        #st.markdown(highlighted_text, unsafe_allow_html=True)

    return highlighted_text

    # First highlight AI-generated segments
    # for segment in sorted(ai_segments, key=len, reverse=True):
    #     if segment.strip():
    #         pattern = re.escape(segment.strip())
    #         highlighted_text = re.sub(
    #             pattern,
    #             f"<span style='background-color:#ffcccc'>{segment}</span>",
    #             highlighted_text,
    #             flags=re.IGNORECASE
    #         )

    # # Then highlight human-like segments (so AI highlights aren't overwritten)
    # for segment in sorted(human_segments, key=len, reverse=True):
    #     if segment.strip():
    #         pattern = re.escape(segment.strip())
    #         highlighted_text = re.sub(
    #             pattern,
    #             f"<span style='background-color:#ccffcc'>{segment}</span>",
    #             highlighted_text,
    #             flags=re.IGNORECASE
    #         )

    # return highlighted_text


def display_highlighted_text(detection_result):
    """
    Display full text with AI/Human highlighting and stats.
    """
    data = detection_result.get("data", {})

    #st.json(data)
    ai_segments = data.get("h", [])
    # st.markdown(
    #     f"""
    #     ai_segments,
    #     >>>{ai_segments},>>>
    #     """
    # )
    human_segments = data.get("hi", [])
    original_text = data.get("originalParagraph", "")
    input_text = data.get("input_text", "")
    # st.markdown(
    #     f"""
    #     original_text, ai_segments, human_segments
    #     {original_text},>>> {ai_segments}, >>>> {human_segments}
    #     """
    # )

    # st.json(input_text)
    # st.json(ai_segments)
    #highlighted_text = highlight_ai_segments(input_text, ai_segments, human_segments)


    highlighted_text = input_text

    for i, term in enumerate(ai_segments):
        seg_key = f"ai_segment_{i}"
        pattern = re.escape(term)
        highlighted_text = re.sub(
            pattern,
            f"<mark style='background-color: yellow; color: black;'>{term}</mark>",
            highlighted_text,
            flags=re.IGNORECASE
        )
    st.markdown(highlighted_text, unsafe_allow_html=True)

    st.divider()
    #st.stop()
    # st.subheader("🧩 AI Detection Visualization")
    # st.markdown(
    #     """
    #     <div style="padding:10px; border-radius:10px; background-color:#f5f5f5;">
    #         <span style="background-color:#ffcccc;">&nbsp;AI-Generated Text&nbsp;</span>
    #         <span style="background-color:#ccffcc;">&nbsp;Human-Written Text&nbsp;</span>
    #     </div>
    #     """,
    #     unsafe_allow_html=True,
    # )

    # st.markdown(
    #     f"<div style='padding:20px;border-radius:10px;background:#ffffff;'>{highlighted_text}</div>",
    #     unsafe_allow_html=True,
    # )

    # Show stats
    fake_percentage = data.get("fakePercentage", 0)
    feedback = data.get("feedback", "No feedback provided.")
    ai_words = data.get("aiWords", 0)
    text_words = data.get("textWords", 0)
    is_human = data.get("isHuman", 0)


    label = "🧠 AI-Generated" if is_human == 0 else "🧍 Human-Written"
    color = "red" if is_human == 0 else "green"

    st.markdown(
        f"""
        <div style="padding:15px;border-radius:10px;background-color:{"#ffffff" if is_human == 0 else "#071D07"};">
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
