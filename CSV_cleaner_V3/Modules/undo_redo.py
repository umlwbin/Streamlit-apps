import streamlit as st

def reset_all_files():
    for filename in st.session_state.original_data:
        st.session_state.current_data[filename] = st.session_state.original_data[filename].copy()
        st.session_state.task_history[filename] = []
        st.session_state.history_stack[filename] = []
        st.session_state.redo_stack[filename] = []
    st.session_state.task_applied = False


def undo_last_task():
    for filename in st.session_state.current_data:
        if st.session_state.history_stack[filename]:
            st.session_state.redo_stack[filename].append(
                st.session_state.current_data[filename].copy()
            )
            st.session_state.current_data[filename] = st.session_state.history_stack[filename].pop()
            if st.session_state.task_history[filename]:
                st.session_state.task_history[filename].pop()


def redo_last_task():
    for filename in st.session_state.current_data:
        if st.session_state.redo_stack[filename]:
            st.session_state.history_stack[filename].append(
                st.session_state.current_data[filename].copy()
            )
            st.session_state.current_data[filename] = st.session_state.redo_stack[filename].pop()