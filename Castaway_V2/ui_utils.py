import streamlit as st

def big_caption(text, size="1.1rem", color="#6c757d"):
    st.markdown(
        f"<p style='font-size:{size}; color:{color}; margin-top:0.2rem;'>{text}</p>",
        unsafe_allow_html=True
    )