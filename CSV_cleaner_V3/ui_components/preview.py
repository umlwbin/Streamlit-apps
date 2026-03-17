import streamlit as st

def show_live_preview():
    st.markdown("#### 🔎 Live Preview of Processed Files")
    st.markdown("")

    if st.session_state.current_data:
        filenames = list(st.session_state.current_data.keys())
        selected_file = st.selectbox(
            "📂 Choose a file to preview",
            filenames,
            key="preview_file"
        )

        current_df = st.session_state.current_data[selected_file]
        original_df = st.session_state.original_data[selected_file]
        history = st.session_state.task_history.get(selected_file, [])

        st.markdown("")
        st.markdown(f" 📑 **File:** `{selected_file}`")
        st.markdown(f" ✅ **Tasks Applied:** {', '.join(history) if history else 'None'}")
        st.markdown("")

        compare = st.checkbox("Compare with Original", key="sidebar_compare")

        if compare:
            st.markdown("**Processed (Top 5 rows):**")
            st.dataframe(current_df.head(5), use_container_width=True)

            st.markdown("**Original (Top 5 rows):**")
            st.dataframe(original_df.head(5), use_container_width=True)
        else:
            st.markdown("**Processed Data (Top 5 rows):**")
            st.dataframe(current_df.head(5), use_container_width=True)
    else:
        st.info("Upload files to see a live preview.")