import streamlit as st
from crew_pipeline import run_pipeline
from zerogpt_api import check_ai_content
from paragraph_editor import display_paragraphs_with_detection
from highlight_ai_segments import display_highlighted_text

#from tools.serper_tool import SerperTool

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

      # --- Initialize session state ---
    # st.session_state.setdefault("generated_content", None)
    # st.session_state.setdefault("detection_result", None)
    st.session_state.setdefault("show_editor", False)
    st.session_state.setdefault("editable_text", "")

    if st.button("🚀 Generate Content"):


        missing_fields = []
        if not topic.strip():
            missing_fields.append("Topic")
        if not researcher_goal.strip():
            missing_fields.append("Researcher Goal")
        if not researcher_backstory.strip():
            missing_fields.append("Researcher Backstory")
        if not writer_goal.strip():
            missing_fields.append("Writer Goal")
        if not writer_backstory.strip():
            missing_fields.append("Writer Backstory")
        if not editor_goal.strip():
            missing_fields.append("Editor Goal")
        if not editor_backstory.strip():
            missing_fields.append("Editor Backstory")

        if missing_fields:
            st.warning(f"Please fill out all required fields: {', '.join(missing_fields)}")
            st.stop()



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

                    #st.json(serper_tool)
                    #return serper_tool

                    #result = "Sample generated content based on the topic."
                    st.session_state.generated_content = result
                    st.session_state.editable_text = result
                    #st.session_state.detection_result = check_ai_content(result)
                    #display_paragraphs_with_detection(result)
                    detection_result = check_ai_content(result)
                    st.session_state.detection_result = detection_result

                    # if "error" in detection_result:
                    #     st.error(detection_result["error"])
                    # else:
                    #     display_highlighted_text(detection_result)

                    st.success("✅ Generation complete! See below for AI detection results.")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Please enter a topic first.")

    # if st.session_state.generated_content:
    #     st.subheader("📝 Generated Content")
    #     st.markdown(st.session_state.generated_content)

    if st.session_state.get("detection_result"):
        #st.markdown("---")
        #st.subheader("🧩 AI Detection Results")
        display_highlighted_text(st.session_state.detection_result)
