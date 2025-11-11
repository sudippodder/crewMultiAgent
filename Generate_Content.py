import streamlit as st
from crew_pipeline import run_pipeline
from zerogpt_api import check_ai_content
from paragraph_editor import display_paragraphs_with_detection
from highlight_ai_segments import display_highlighted_text

def generate_content_page():
    st.title("✍️ Generate AI Blog Content")

    topic = st.text_input("Enter your topic:", placeholder="e.g. AI tools for marketing")

    with st.expander("Researcher Settings", expanded=True):
        researcher_goal = st.text_area("Goal", "Find and summarize useful content for the given topic.")
        researcher_backstory = st.text_area("Backstory", "You're great at finding relevant sources.")

    with st.expander("Writer Settings", expanded=True):
        writer_goal = st.text_area("Goal", "Write a detailed, SEO-friendly blog post using the research.")
        writer_backstory = st.text_area("Backstory", "You're skilled at clarity and engagement.")

    with st.expander("Editor Settings", expanded=True):
        editor_goal = st.text_area("Goal", "Polish and refine the blog content for tone, clarity, and grammar.")
        editor_backstory = st.text_area("Backstory", "You ensure it reads naturally and maintains tone.")

    if "generated_content" not in st.session_state:
        st.session_state.generated_content = None
    if "detection_result" not in st.session_state:
        st.session_state.detection_result = None

    if st.button("🚀 Generate Content"):
        if topic.strip():
            with st.spinner("🤖 Generating content..."):
                try:
                    result = run_pipeline(
                        topic,
                        researcher_goal, researcher_backstory,
                        writer_goal, writer_backstory,
                        editor_goal, editor_backstory
                    )
                    # file_path = "outputs/For_Audience_Engagement.txt"  # Replace with your file name or full path
                    # # Open the file in read mode ('r')
                    # with open(file_path, "r", encoding="utf-8") as file:
                    #     content = file.read()

                    # result = content
                    st.session_state.generated_content = result
                    #st.session_state.detection_result = check_ai_content(result)
                    #display_paragraphs_with_detection(result)
                    detection_result = check_ai_content(result)

                    if "error" in detection_result:
                        st.error(detection_result["error"])
                    else:
                        display_highlighted_text(detection_result)

                    st.success("✅ Generation complete!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a topic first.")

    # if st.session_state.generated_content:
    #     st.subheader("📝 Generated Content")
    #     st.markdown(st.session_state.generated_content)

generate_content_page()
