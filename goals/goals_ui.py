import streamlit as st
from goals.goals_service import (
    add_goal,
    add_sub_goal,
    delete_goal,
    delete_sub_goal,
    get_goals
)
from utils.session import require_login

def render():
    require_login()
    st.header("Goals & Habits")

    user_id = st.session_state.user_id

    # ------------------------
    # Add Main Goal
    # ------------------------
    with st.expander("➕ Add Main Goal"):
      
        with st.form("add_goal_form", clear_on_submit=True):
            goal_name = st.text_input("New Goal")
            submitted = st.form_submit_button("Add Goal")

            if submitted and goal_name.strip():
                add_goal(user_id, goal_name)


    # ------------------------
    # Existing Goals
    # ------------------------
    goals = get_goals(user_id)

    if not goals:
        st.info("No goals added yet.")
        return

    for goal, subs in goals:
        col1, col2 = st.columns([8, 1])

        with col1:
            st.subheader(goal[1])

        with col2:
            if st.button("🗑️", key=f"del_goal_{goal[0]}"):
                delete_goal(goal[0])
                st.rerun()

        # ------------------------
        # Sub-goals
        # ------------------------
        for s in subs:
            sg_col1, sg_col2 = st.columns([8, 1])

            with sg_col1:
                st.write(f"• {s[1]}")

            with sg_col2:
                if st.button("❌", key=f"del_sub_{s[0]}"):
                    delete_sub_goal(s[0])
                    st.rerun()

        # ------------------------
        # Add Sub-goal
        # ------------------------

        with st.form(f"add_sub_{goal[0]}", clear_on_submit=True):
            sub = st.text_input("Add Sub-goal")
            submitted = st.form_submit_button("Add")

            if submitted and sub.strip():
                add_sub_goal(goal[0], sub)
                st.rerun()

        st.divider()
