import streamlit as st
from database.db import get_connection

def render():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        cur = conn.cursor()
        user = cur.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            st.session_state.user_id = user[0]
            st.rerun()
        else:
            st.error("Invalid credentials")
