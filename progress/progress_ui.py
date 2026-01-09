import streamlit as st
import plotly.express as px
import pandas as pd

from progress.analytics import (
    load_data,
    get_stage,
    active_days,
    completion_rate,
    daily_completion,
    goal_scores,
    habit_scores,
    habit_streaks,
    momentum,
    risk_signal,
    consistency_trend,
    fragile_habit,
    perfect_days,
    weekday_pattern
)
from utils.session import require_login


# =====================================================
# FILTER HELPER
# =====================================================
def apply_filter(df, view, goal=None, sub_goal=None):
    if view == "Main Goal":
        return df[df["goal"] == goal]
    if view == "Sub-goal":
        return df[(df["goal"] == goal) & (df["sub_goal"] == sub_goal)]
    return df


def render():
    require_login()
    st.header("🎮 Progress & Insights")

    df = load_data(st.session_state.user_id)

    # -------------------------------------------------
    # DAY 0 EXPERIENCE
    # -------------------------------------------------
    if df.empty:
        st.subheader("🚀 Day 0")
        st.info("Your goals are set. One small action today starts everything.")
        return

    total_days = active_days(df)
    stage = get_stage(total_days)

    # -------------------------------------------------
    # FILTERS
    # -------------------------------------------------
    st.subheader("🎯 Focus")

    view = st.radio(
        "View",
        ["Overall", "Main Goal", "Sub-goal"],
        horizontal=True
    )

    goal = sub_goal = None
    if view in ["Main Goal", "Sub-goal"]:
        goal = st.selectbox("Goal", sorted(df["goal"].unique()))

    if view == "Sub-goal":
        sub_goal = st.selectbox(
            "Sub-goal",
            sorted(df[df["goal"] == goal]["sub_goal"].unique())
        )

    df_f = apply_filter(df, view, goal, sub_goal)

    # -------------------------------------------------
    # TOP SUMMARY
    # -------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Days", total_days)
    c2.metric("Consistency", f"{completion_rate(df_f)}%")
    c3.metric("Stage", stage.capitalize())

    st.divider()

    # -------------------------------------------------
    # DONUT — GOAL CONTRIBUTION
    # -------------------------------------------------
    st.subheader("🏹 Goal Contribution")
    st.plotly_chart(
        px.pie(
            df_f,
            values="completed",
            names="goal",
            hole=0.6
        ),
        use_container_width=True
    )

    # -------------------------------------------------
    # HABIT RELIABILITY
    # -------------------------------------------------
    st.subheader("📊 Habit Reliability")
    hs = habit_scores(df_f)
    if hs:
        st.plotly_chart(
            px.bar(
                x=list(hs.keys()),
                y=list(hs.values()),
                labels={"x": "Habit", "y": "Completion %"}
            ),
            use_container_width=True
        )

    # -------------------------------------------------
    # HEATMAP — CONSISTENCY (EVOLVES WITH STAGE)
    # -------------------------------------------------
    if stage in ["consistency", "momentum", "mastery"]:
        st.subheader("🗓 Consistency Map")
        heat = daily_completion(df_f)
        heat["day"] = heat["date"].dt.day
        heat["month"] = heat["date"].dt.strftime("%b")

        pivot = heat.pivot_table(
            index="month",
            columns="day",
            values="completed",
            aggfunc="mean"
        ).fillna(0)

        st.plotly_chart(
            px.imshow(
                pivot,
                color_continuous_scale="Greens"
            ),
            use_container_width=True
        )

    # -------------------------------------------------
    # MOMENTUM
    # -------------------------------------------------
    if stage in ["momentum", "mastery"]:
        st.subheader("📈 Momentum")
        m7 = momentum(df_f, 7)
        m21 = momentum(df_f, 21) or 0

        st.plotly_chart(
            px.bar(
                x=["Last 7 Days", "Last 21 Days"],
                y=[m7, m21]
            ),
            use_container_width=True
        )

    # -------------------------------------------------
    # STREAKS
    # -------------------------------------------------
    st.divider()
    st.subheader("🔥 Habit Streaks")
    for h, (cur, best) in habit_streaks(df_f).items():
        st.write(f"**{h}** → Current: {cur} | Best: {best}")

    # -------------------------------------------------
    # INSIGHTS
    # -------------------------------------------------
    st.divider()
    st.subheader("🧠 Behavioral Insights")

    trend = consistency_trend(df_f)
    if trend:
        st.info(f"Consistency trend: **{trend}**")

    fragile = fragile_habit(df_f)
    if fragile:
        st.warning(f"Weakest habit: **{fragile[0]}** ({fragile[1]}%)")

    p, total = perfect_days(df_f)
    st.metric("Perfect Days", f"{p} / {total}")

    weekday = weekday_pattern(df_f)
    if weekday:
        st.info(
            f"You perform best on **{weekday[0]}s** and struggle most on **{weekday[1]}s**."
        )

    st.subheader("⚠️ Risk Signal")
    st.info(risk_signal(df_f))
