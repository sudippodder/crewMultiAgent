import streamlit as st
from zerogpt_api import check_ai_content

def display_editable_segments(label: str, original_paragraph: str, segments: list, detection_result: dict):
    """
    Reusable editable segments component.
    Keeps all content visible and only toggles edit mode for one segment.
    """
    st.subheader(f"🚨 {label}")

    if not segments:
        st.info("No suspected AI-generated segments found.")
        return detection_result

    # Initialize edit states
    if "edit_state" not in st.session_state:
        st.session_state.edit_state = {}
    if "edit_buffers" not in st.session_state:
        st.session_state.edit_buffers = {}

    for idx, segment in enumerate(segments):
        seg_key = f"{label}_segment_{idx}"
        if seg_key not in st.session_state.edit_state:
            st.session_state.edit_state[seg_key] = False
        if seg_key not in st.session_state.edit_buffers:
            st.session_state.edit_buffers[seg_key] = segment

        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            if st.session_state.edit_state[seg_key]:
                new_text = st.text_area(
                    f"Edit segment {idx+1}",
                    value=st.session_state.edit_buffers[seg_key],
                    key=f"{seg_key}_area",
                    height=140,
                )
                st.session_state.edit_buffers[seg_key] = new_text
            else:
                st.markdown(
                    f"<div style='padding:10px;border-radius:6px;background:#fff6f6; color:black;'>{segment}</div>",
                    unsafe_allow_html=True,
                )

        with col2:
            if not st.session_state.edit_state[seg_key]:
                if st.button("Edit", key=f"{seg_key}_edit"):
                    st.session_state.edit_state[seg_key] = True
                    st.session_state.edit_buffers[seg_key] = segment
                    # No rerun — UI will update instantly
            else:
                save_col, cancel_col = st.columns(2)
                with save_col:
                    if st.button("Save", key=f"{seg_key}_save"):
                        edited_text = st.session_state.edit_buffers[seg_key].strip()
                        if edited_text:
                            full_text = original_paragraph.replace(segment, edited_text, 1)
                            with st.spinner("Rechecking updated text..."):
                                recheck = check_ai_content(full_text)
                                if "error" in recheck:
                                    st.error(f"Recheck failed: {recheck['error']}")
                                else:
                                    st.success("Segment updated successfully.")
                                    st.session_state.edit_state[seg_key] = False
                                    return recheck
                        else:
                            st.warning("Edited text cannot be empty.")

                with cancel_col:
                    if st.button("Cancel", key=f"{seg_key}_cancel"):
                        st.session_state.edit_state[seg_key] = False
                        st.session_state.edit_buffers[seg_key] = segment

        st.divider()

    return detection_result

