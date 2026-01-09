import streamlit as st
from goals.goals_service import get_goals
from checkin.checkin_service import set_status, get_status
from utils.session import require_login
from utils.dates import today

def render():
    require_login()
    st.header("Daily Check-in")

    date = st.date_input("Select date").isoformat()
    goals = get_goals(st.session_state.user_id)

    for goal, subs in goals:
        st.subheader(goal[1])

        for s in subs:
            checked = get_status(s[0], date)
            val = st.checkbox(s[1], value=bool(checked), key=f"{s[0]}{date}")
            set_status(s[0], date, int(val))
