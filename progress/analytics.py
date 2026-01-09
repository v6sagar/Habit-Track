import pandas as pd
import numpy as np
from database.db import get_connection

# =====================================================
# DATA LOAD (DUPLICATE SAFE)
# =====================================================
def load_data(user_id):
    conn = get_connection()
    df = pd.read_sql(
        """
        SELECT
            d.date,
            d.completed,
            g.name AS goal,
            s.name AS sub_goal
        FROM daily_logs d
        JOIN sub_goals s ON d.sub_goal_id = s.id
        JOIN goals g ON s.goal_id = g.id
        
        WHERE active=1 & g.user_id = ?
        """,
        conn,
        params=(user_id,)
    )

    df["date"] = pd.to_datetime(df["date"])
    return df


# =====================================================
# STAGE ENGINE (NO HARD LOCKS)
# =====================================================
def get_stage(days):
    if days < 3:
        return "identity"
    elif days < 7:
        return "pattern"
    elif days < 14:
        return "consistency"
    elif days < 30:
        return "momentum"
    else:
        return "mastery"


# =====================================================
# CORE METRICS
# =====================================================
def active_days(df):
    return df["date"].dt.date.nunique()


def completion_rate(df):
    if df.empty:
        return 0
    return round(df["completed"].mean() * 100, 1)


def daily_completion(df):
    return (
        df.groupby("date")["completed"]
        .mean()
        .reset_index()
        .sort_values("date")
    )


# =====================================================
# STREAKS
# =====================================================
def streaks(series):
    dates = series.sort_values().dt.date.tolist()
    if not dates:
        return 0, 0

    best = current = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current += 1
            best = max(best, current)
        else:
            current = 1

    # current streak
    temp = 1
    for i in range(len(dates) - 1, 0, -1):
        if (dates[i] - dates[i - 1]).days == 1:
            temp += 1
        else:
            break

    return temp, best


def habit_streaks(df):
    result = {}
    for h, hdf in df[df["completed"] == 1].groupby("sub_goal"):
        result[h] = streaks(hdf["date"])
    return result


# =====================================================
# GOAL & HABIT SCORES
# =====================================================
def goal_scores(df):
    return (
        df.groupby("goal")["completed"]
        .mean()
        .mul(100)
        .round(0)
        .astype(int)
        .to_dict()
    )


def habit_scores(df):
    return (
        df.groupby("sub_goal")["completed"]
        .mean()
        .mul(100)
        .round(0)
        .astype(int)
        .to_dict()
    )


# =====================================================
# MOMENTUM & RISK
# =====================================================
def momentum(df, window):
    daily = df.groupby("date")["completed"].mean()
    if len(daily) < window:
        return None
    return daily.tail(window).mean()


def risk_signal(df):
    daily = df.groupby("date")["completed"].mean().sort_index()

    if len(daily) < 10:
        return "Too early"

    short = daily.tail(7).mean()
    long = daily.tail(21).mean() if len(daily) >= 21 else daily.mean()

    if short < 0.4:
        return "High Risk"
    if short < long:
        return "Declining"
    return "Stable"


# =====================================================
# BEHAVIOR INSIGHTS (GAMIFIED)
# =====================================================
def behavior_insights(df):
    insights = []

    if df.empty:
        return insights

    weekday = df.copy()
    weekday["weekday"] = weekday["date"].dt.day_name()

    by_day = weekday.groupby("weekday")["completed"].mean()

    worst = by_day.idxmin()
    best = by_day.idxmax()

    if by_day[best] - by_day[worst] > 0.2:
        insights.append(
            f"You perform best on **{best}s** and struggle on **{worst}s**."
        )

    if completion_rate(df) > 80:
        insights.append("You’re building strong consistency. Keep the rhythm.")
    elif completion_rate(df) < 40:
        insights.append("Low completion detected — try shrinking your goals.")

    return insights
