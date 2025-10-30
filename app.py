import streamlit as st
from crew_pipeline import run_pipeline

st.set_page_config(page_title="Multi-Agent Blog Generator", layout="wide")

st.title("🧠 Multi-Agent AI Blog Generator")
st.write("Enter a topic below. The agents will research, write, edit, and prepare a complete blog post.")

# Input field
topic = st.text_input("Blog Topic:", placeholder="e.g. AI tools for marketing")

# Generate button
if st.button("Generate Blog"):
    if topic.strip():
        with st.spinner("🤖 Agents are working on your blog..."):
            try:
                result = run_pipeline(topic)
                st.success("✅ Blog generation complete!")
                st.markdown(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a topic first.")
