import streamlit as st
from Modules.undo_redo import reset_all_files, undo_last_task, redo_last_task

def toolbar():

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

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🔄 Reset All Files", key="reset_toolbar"):
            reset_all_files()
            st.toast("All files reset.", icon="🔁")

    with col2:
        if st.button("↩️ Undo", key="undo_toolbar"):
            undo_last_task()
            st.toast("Undo successful.", icon="✅")

    with col3:
        if st.button("↪️ Redo", key="redo_toolbar"):
            redo_last_task()
            st.toast("Redo successful.", icon="✅")