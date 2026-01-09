import streamlit as st
from database.schema import create_tables
from auth.login import render as login
from goals.goals_ui import render as goals
from checkin.checkin_ui import render as checkin
from progress.progress_ui import render as progress
from todo.todo_ui import render as todo

create_tables()

st.set_page_config(layout="wide")

if "user_id" not in st.session_state:
    login()
else:
    page = st.sidebar.radio(
    "Menu",
    ["Goals", "Daily Check-in", "Progress", "To-Do"]
)
    if page == "Goals":
        goals()
    elif page == "Daily Check-in":
        checkin()
    elif page == "To-Do":
        todo()
    else:
        progress()

