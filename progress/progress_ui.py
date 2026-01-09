import streamlit as st
import plotly.express as px

from progress.analytics import (
    load_data,
    get_stage,
    active_days,
    completion_rate,
    daily_completion,
    habit_streaks,
    goal_scores,
    habit_scores,
    momentum,
    risk_signal,
    behavior_insights
)
from utils.session import require_login


def render():
    require_login()
    st.header("🎮 Your Progress")

    df = load_data(st.session_state.user_id)

    # --------------------------------------------------
    # DAY 0 EXPERIENCE
    # --------------------------------------------------
    if df.empty:
        st.subheader("🚀 Day 0")
        st.info("You’ve set your goals. One small action today starts everything.")
        st.metric("Consistency", "0%")
        return

    days = active_days(df)
    stage = get_stage(days)

    # --------------------------------------------------
    # TOP SUMMARY
    # --------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Days", days)
    c2.metric("Consistency", f"{completion_rate(df)}%")
    c3.metric("Stage", stage.capitalize())

    # --------------------------------------------------
    # STAGE-SPECIFIC VISUALS
    # --------------------------------------------------
    st.divider()

    # ---------- DONUT (ALL STAGES) ----------
    donut = px.pie(
        df,
        values="completed",
        names="goal",
        hole=0.6,
        title="Goal Contribution"
    )
    st.plotly_chart(donut, use_container_width=True)

    # ---------- HABIT BARS ----------
    hs = habit_scores(df)
    bar = px.bar(
        x=list(hs.keys()),
        y=list(hs.values()),
        labels={"x": "Habit", "y": "Completion %"},
        title="Habit Reliability"
    )
    st.plotly_chart(bar, use_container_width=True)

    # ---------- HEATMAP (CONSISTENCY+) ----------
    if stage in ["consistency", "momentum", "mastery"]:
        heat = daily_completion(df)
        heat["day"] = heat["date"].dt.day
        heat["month"] = heat["date"].dt.strftime("%b")

        pivot = heat.pivot_table(
            index="month",
            columns="day",
            values="completed",
            aggfunc="mean"
        )

        st.plotly_chart(
            px.imshow(
                pivot,
                color_continuous_scale="Greens",
                title="Consistency Map"
            ),
            use_container_width=True
        )

    # ---------- MOMENTUM ----------
    if stage in ["momentum", "mastery"]:
        m7 = momentum(df, 7)
        m21 = momentum(df, 21) or 0

        st.plotly_chart(
            px.bar(
                x=["Last 7 Days", "Last 21 Days"],
                y=[m7, m21],
                title="Momentum Comparison"
            ),
            use_container_width=True
        )

    # ---------- STREAKS ----------
    st.divider()
    st.subheader("🔥 Habit Streaks")

    for habit, (cur, best) in habit_streaks(df).items():
        st.write(f"**{habit}** → Current: {cur} | Best: {best}")

    # ---------- RISK ----------
    st.divider()
    st.subheader("⚠️ Risk Signal")
    st.info(risk_signal(df))

    # ---------- INSIGHTS ----------
    st.divider()
    st.subheader("🧠 Insights")

    insights = behavior_insights(df)
    if insights:
        for i in insights:
            st.write("•", i)
    else:
        st.caption("More insights will appear as patterns form.")
