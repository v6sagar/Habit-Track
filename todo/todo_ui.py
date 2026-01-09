import streamlit as st
from datetime import date, timedelta

from todo.todo_service import (
    get_tasks,
    add_task,
    set_status,
    delete_task
)
from utils.session import require_login


def circular_progress(label, progress, size=70, thickness=8):
    progress = max(0, min(progress, 1))  # clamp

    percent = int(progress * 100)
    angle = percent * 3.6

    return f"""
    <div style="
        width:{size}px;
        height:{size}px;
        border-radius:50%;
        background:
            conic-gradient(
                #22c55e {angle}deg,
                #e5e7eb 0deg
            );
        display:flex;
        align-items:center;
        justify-content:center;
        margin:auto;
    ">
        <div style="
            width:{size - thickness}px;
            height:{size - thickness}px;
            background:#0f172a;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            color:white;
            font-weight:600;
            font-size:0.9rem;
        ">
            {label}
        </div>
    </div>
    """

def small_circular_progress(progress, size=80, thickness=10):
    progress = max(0, min(progress, 1))
    angle = int(progress * 360)

    return f"""
    <div style="
        width:{size}px;
        height:{size}px;
        border-radius:50%;
        background:
            conic-gradient(
                #22c55e {angle}deg,
                #e5e7eb 0deg
            );
        display:flex;
        align-items:center;
        justify-content:center;
    ">
        <div style="
            width:{size - thickness}px;
            height:{size - thickness}px;
            background:#0f172a;
            border-radius:50%;
        ">
        <div style="
            width:{size - thickness}px;
            height:{size - thickness}px;
            background:#0f172a;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            color:white;
            font-weight:600;
            font-size:0.9rem;
        ">
            WEEK
        </div>
    </div>
    """


def render():
    require_login()
    user_id = st.session_state.user_id
    today = date.today()

    # ----------------------------------------
    # PRE-CALCULATE WEEKLY TOTALS (IMPORTANT)
    # ----------------------------------------
    weekly_done = 0
    weekly_total = 0

    for i in range(7):
        d = today + timedelta(days=i)
        tasks = get_tasks(user_id, d.isoformat())
        weekly_done += sum(t[2] for t in tasks)
        weekly_total += len(tasks)

    weekly_progress = weekly_done / weekly_total if weekly_total else 0

    # ----------------------------------------
    # HEADER WITH WEEKLY RING
    # ----------------------------------------
    h1, h2 = st.columns([6, 1], vertical_alignment="center")

    with h1:
        st.header("📝 7-Day Planner")

    with h2:
        '''
        st.markdown(
            small_circular_progress(weekly_progress),
            unsafe_allow_html=True
        )
        '''

    cols = st.columns(7)
    weekly_done = 0
    weekly_total = 0



    # --------------------------------
    # Instant checkbox update handler
    # --------------------------------
    def toggle(task_id, key):
        set_status(task_id, int(st.session_state[key]))

    # =================================
    # 7-DAY GRID
    # =================================
    for i, col in enumerate(cols):
        current_day = today + timedelta(days=i)

        if i == 0:
            label = "Today"
        else:
            label = current_day.strftime("%a")

        # Visual emphasis
        bg = (
            "" if i == 0 else      # today
            "" if i > 0 else       # future
            ""                     # past (not used but future-proof)
        )

        with col:
            tasks = get_tasks(user_id, current_day.isoformat())
            done = sum(t[2] for t in tasks)
            total = len(tasks)

            weekly_done += done
            weekly_total += total

            progress = done / total if total else 0

            st.markdown(
                f"""
                <div style="
                    background:{bg};
                    padding:10px;
                    border-radius:10px;
                ">
                {circular_progress(label, progress)}
                """,
                unsafe_allow_html=True
            )

            # -----------------------------
            # Tasks
            # -----------------------------
            if not tasks:
                st.caption("No tasks yet")

            for t_id, task, completed in tasks:
                key = f"todo_{t_id}"
                label_text = f"~~{task}~~" if completed else task

                # Checkbox (full width, no columns)
                st.checkbox(
                    label_text,
                    value=bool(completed),
                    key=key,
                    on_change=toggle,
                    args=(t_id, key)
                )

                # Subtle inline delete, aligned right
                
                if st.button("❌", key=f"del_{t_id}", help="Remove"):
                    delete_task(t_id)
                    st.rerun()



            # -----------------------------
            # Add Task
            # -----------------------------
            

            def add_todo_callback(user_id, date, input_key):
                task = st.session_state[input_key].strip()
                if task:
                    add_task(user_id, task, date)
                    st.session_state[input_key] = ""   # ✅ guaranteed reset


            input_key = f"add_{current_day}"

            st.text_input(
                "Add task",
                key=input_key,
                placeholder="Quick task…"
            )

            st.button(
                "➕ Add",
                key=f"btn_{current_day}",
                on_click=add_todo_callback,
                args=(user_id, current_day.isoformat(), input_key)
)


    