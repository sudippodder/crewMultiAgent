import streamlit as st
from crew_pipeline import run_pipeline

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
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic first.")
