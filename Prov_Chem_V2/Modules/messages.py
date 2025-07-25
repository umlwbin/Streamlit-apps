import streamlit as st

def warnings(msg):
    left, right = st.columns([0.8, 0.2])
    left.warning(f'{msg}', icon="⚠️")

def errors(msg):
    left, right = st.columns([0.8, 0.2])
    left.error(f'{msg}', icon="🚨")  

def successes(msg):
    #left, right = st.columns([0.8, 0.2])
    st.success(f'Success! {msg}', icon="✅",)

