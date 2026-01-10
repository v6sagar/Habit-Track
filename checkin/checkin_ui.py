import streamlit as st
from datetime import date as dt_date

from goals.goals_service import get_goals
from checkin.checkin_service import set_status, get_status
from utils.session import require_login


def render():
    require_login()
    st.header("✅ Daily Check-in")

    # ---------------------------------------------
    # LOCK TO TODAY ONLY
    # ---------------------------------------------
    selected_date = dt_date.today()

    st.subheader(f"📅 Today — {selected_date.strftime('%A, %d %b')}")
    st.caption("You can only update today's progress.")

    goals = get_goals(st.session_state.user_id)

    if not goals:
        st.info("Add goals first to start tracking your habits.")
        return

    # ---------------------------------------------
    # RENDER CHECKBOXES
    # ---------------------------------------------
    for goal, subs in goals:
        st.subheader(goal[1])

        for sub in subs:
            sub_id = sub[0]
            sub_name = sub[1]

            # ✅ ALWAYS use selected_date
            checked = bool(get_status(sub_id, selected_date))

            val = st.checkbox(
                sub_name,
                value=checked,
                key=f"check_{sub_id}_{selected_date}"
            )

            # -------------------------------------
            # WRITE ONLY ON CHANGE
            # -------------------------------------
            if val != checked:
                set_status(sub_id, selected_date, int(val))

                # 🚀 Force immediate refresh
                st.rerun()
