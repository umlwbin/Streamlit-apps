import streamlit as st
from Modules.state.undo_redo import reset_all_files, undo_last_task, redo_last_task

def toolbar():
    # Keep your custom CSS styling intact
    st.markdown("""
        <style>
        .toolbar {
            display: flex;
            gap: 0.6rem;
            padding: 0.4rem 0 1rem 0;
            border-bottom: 1px solid rgba(0,0,0,0.1);
            margin-bottom: 0.8rem;
        }
        .toolbar button {
            padding: 0.45rem 0.8rem !important;
            border-radius: 6px !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        # Check if edits have been made before allowing a reset
        is_reset_disabled = not st.session_state.get("task_applied", False)
        if st.button("🔄 Reset All Files", key="reset_toolbar", disabled=is_reset_disabled):
            reset_all_files()  # This function internally triggers a clean rerun
            st.toast("All files reset to original.", icon="🔁")

    with col2:
        # Dynamically count remaining history steps
        history_len = len(st.session_state.get("history_stack", []))
        is_undo_disabled = history_len == 0
        undo_label = f"↩️ Undo ({history_len})" if history_len > 0 else "↩️ Undo"
        
        if st.button(undo_label, key="undo_toolbar", disabled=is_undo_disabled):
            undo_last_task()  # This function internally triggers a clean rerun
            st.toast("Undo successful.", icon="↩️")

    with col3:
        # Dynamically count remaining redo layers
        redo_len = len(st.session_state.get("redo_stack", []))
        is_redo_disabled = redo_len == 0
        redo_label = f"↪️ Redo ({redo_len})" if redo_len > 0 else "↪️ Redo"
        
        if st.button(redo_label, key="redo_toolbar", disabled=is_redo_disabled):
            redo_last_task()  # This function internally triggers a clean rerun
            st.toast("Redo successful.", icon="↪️")
