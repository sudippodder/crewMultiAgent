import streamlit as st
from zerogpt_api import check_ai_content
import time

def display_editable_segments(label: str, original_paragraph: str, segments: list, detection_result: dict):
    """
    Editable AI-generated segment component.
    Returns (updated_result, needs_refresh) to control reruns outside this function.
    """
    st.subheader(f"🚨 {label}")
    st.subheader(f"🚨 {segments}")
    if not segments:
        st.info("No suspected AI-generated segments found.")
        return detection_result, False

    if "edit_state" not in st.session_state:
        st.session_state.edit_state = {}
    if "edit_buffers" not in st.session_state:
        st.session_state.edit_buffers = {}

    needs_refresh = False
    updated_result = detection_result

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
                    f"Edit Segment {idx+1}",
                    value=st.session_state.edit_buffers[seg_key],
                    key=f"{seg_key}_area",
                    height=120,
                )
                st.session_state.edit_buffers[seg_key] = new_text
            else:
                st.markdown(
                    f"<div style='padding:10px;border-radius:6px;background:#fff6f6;color: black;' data-key='{seg_key}'>{segment}</div>",
                    unsafe_allow_html=True,
                )

        with col2:
            if not st.session_state.edit_state[seg_key]:
                st.button("Edit", key=f"{seg_key}_edit", on_click=lambda k=seg_key: toggle_edit(k, True))
            else:
                save_col, cancel_col = st.columns(2)
                with save_col:
                    if st.button("Save", key=f"{seg_key}_save"):
                        edited_text = st.session_state.edit_buffers[seg_key].strip()
                        st.markdown(f" after edit  > {edited_text}")
                        if edited_text:
                            full_text = original_paragraph.replace(segment, edited_text, 1)
                            st.markdown(f" full_text edit  > {full_text}")
                            with st.spinner("Rechecking updated text..."):
                                recheck = check_ai_content(full_text)
                            if "error" in recheck:
                                st.error(f"Recheck failed: {recheck['error']}")
                            else:
                                st.success("✅ Segment updated successfully.")
                                st.session_state.edit_state[seg_key] = False
                                st.session_state["detection_result"] = recheck
                                needs_refresh = True
                                st.markdown(f" recheck edit  > {recheck}")
                                updated_result = recheck
                                #time.sleep(0.3)
                                st.rerun()
                        else:
                            st.warning("Edited text cannot be empty.")
                with cancel_col:
                    st.button("Cancel", key=f"{seg_key}_cancel", on_click=lambda k=seg_key: toggle_edit(k, False))

        st.divider()

    return updated_result, needs_refresh


def toggle_edit(seg_key: str, state: bool):
    st.session_state.edit_state[seg_key] = state
    st.rerun()
