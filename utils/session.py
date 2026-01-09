import streamlit as st

def require_login():
    if "user_id" not in st.session_state:
        st.stop()
