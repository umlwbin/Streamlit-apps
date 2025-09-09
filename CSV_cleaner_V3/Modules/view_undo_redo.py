import streamlit as st

def reset_undo_redo_buttons():

    col1, col2, col3 = st.columns(3)

    with col1:
        # 🔄 Reset all
        if st.button("🔄  **Reset All Files**"):
            for filename in st.session_state.original_data:
                st.session_state.current_data[filename] = st.session_state.original_data[filename].copy()
                st.session_state.task_history[filename] = []
            st.toast("🔁 All files reset to original versions")

    with col2:
    # ↩️ Undo Button
        if st.button("↩️ **Undo Last Task**"):
            for filename in st.session_state.current_data:
                if st.session_state.history_stack[filename]:
                    # Move current to redo
                    st.session_state.redo_stack[filename].append(
                        st.session_state.current_data[filename].copy()
                    )
                    # Restore previous
                    st.session_state.current_data[filename] = st.session_state.history_stack[filename].pop()
                    if st.session_state.task_history[filename]:
                        st.session_state.task_history[filename].pop()
            st.toast("Undo successful.", icon='✅')

    with col3:
        if st.button("↪️ **Redo Last Undo**"):
            for filename in st.session_state.current_data:
                if st.session_state.redo_stack[filename]:
                    # Save current to history
                    st.session_state.history_stack[filename].append(
                        st.session_state.current_data[filename].copy()
                    )
                    # Restore redo
                    st.session_state.current_data[filename] = st.session_state.redo_stack[filename].pop()
            st.toast("Redo successful.",icon="✅")

    st.markdown("")


def show_snapshot():
    st.markdown('')
    st.success('All done! View updated file in the **Live Data Preview** tab!', icon="✅")
    #st.write(list(st.session_state.current_data.values())[0].head(5))


def view_task_applied():
    if len(st.session_state.current_data) > 0:
        # Show task history
        history = st.session_state.task_history.values()
        history=iter(history)
        history=next(history)
        st.sidebar.caption(f"🧾 Tasks applied to file(s): {', '.join(history) if history else 'None'}")



def update_Undo_Redo_stacks(filename, df):
    st.session_state.history_stack[filename].append(df.copy()) # Save current to history
    st.session_state.redo_stack[filename] = [] # Clear redo stack


def store_currentData_and_update_taskHistory(filename,cleaned_df,task):
    st.session_state.current_data[filename] = cleaned_df
    st.session_state.task_history[filename].append(task)   