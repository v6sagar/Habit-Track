import pandas as pd
import numpy as np
from database.db import get_connection

# =====================================================
# DATA LOADING (DUPLICATE-SAFE BY DESIGN)
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
        WHERE active=1 AND g.user_id = ?
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
    return round(df["completed"].mean() * 100, 1) if not df.empty else 0


def daily_completion(df):
    return (
        df.groupby("date")["completed"]
        .mean()
        .reset_index()
        .sort_values("date")
    )


# =====================================================
# SCORES
# =====================================================
def goal_scores(df):
    if df.empty:
        return {}

    temp = df.copy()
    temp["completed"] = pd.to_numeric(temp["completed"], errors="coerce").fillna(0)

    return (
        temp.groupby("goal")["completed"]
        .mean()
        .mul(100)
        .round()
        .astype(int)
        .to_dict()
    )



def habit_scores(df):
    if df.empty:
        return {}

    temp = df.copy()
    temp["completed"] = pd.to_numeric(temp["completed"], errors="coerce").fillna(0)

    return (
        temp.groupby("sub_goal")["completed"]
        .mean()
        .mul(100)
        .round()
        .astype(int)
        .to_dict()
    )



# =====================================================
# STREAKS
# =====================================================
def _streak_calc(dates):
    if not dates:
        return 0, 0

    best = curr = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            curr += 1
            best = max(best, curr)
        else:
            curr = 1

    curr = 1
    for i in range(len(dates) - 1, 0, -1):
        if (dates[i] - dates[i - 1]).days == 1:
            curr += 1
        else:
            break

    return curr, best


def habit_streaks(df):
    out = {}
    for h, hdf in df[df["completed"] == 1].groupby("sub_goal"):
        dates = sorted(hdf["date"].dt.date.unique())
        out[h] = _streak_calc(dates)
    return out


# =====================================================
# MOMENTUM & RISK
# =====================================================
def momentum(df, window):
    daily = df.groupby("date")["completed"].mean()
    return daily.tail(window).mean() if len(daily) >= window else None


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
# BEHAVIORAL INSIGHTS (HIGH SIGNAL)
# =====================================================
def consistency_trend(df):
    daily = df.groupby("date")["completed"].mean()
    if len(daily) < 7:
        return None

    x = np.arange(len(daily))
    slope = np.polyfit(x, daily.values, 1)[0]

    if slope > 0.01:
        return "Improving"
    if slope < -0.01:
        return "Declining"
    return "Stable"


def fragile_habit(df):
    rates = df.groupby("sub_goal")["completed"].mean()
    if rates.empty:
        return None
    return rates.idxmin(), int(rates.min() * 100)


def perfect_days(df):
    daily = df.groupby("date")["completed"].mean()
    return int((daily == 1).sum()), len(daily)


def weekday_pattern(df):
    temp = df.copy()
    temp["weekday"] = temp["date"].dt.day_name()
    by_day = temp.groupby("weekday")["completed"].mean()
    if len(by_day) < 5:
        return None
    return by_day.idxmax(), by_day.idxmin()


def has_completion_today(user_id, today):
    from database.db import get_connection

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 1
        FROM daily_logs d
        JOIN sub_goals s ON d.sub_goal_id = s.id
        JOIN goals g ON s.goal_id = g.id
        WHERE g.user_id = ?
          AND d.date = ?
          AND d.completed = 1
        LIMIT 1
        """,
        (user_id, today)
    )

    return cur.fetchone() is not None

def is_grace_day(user_id, today):
    from database.db import get_connection

    conn = get_connection()
    cur = conn.cursor()

    # Earliest day user ever completed anything
    cur.execute(
        """
        SELECT MIN(d.date)
        FROM daily_logs d
        JOIN sub_goals s ON d.sub_goal_id = s.id
        JOIN goals g ON s.goal_id = g.id
        WHERE g.user_id = ?
          AND d.completed = 1
        """,
        (user_id,)
    )

    row = cur.fetchone()
    if row is None or row[0] is None:
        return False

    return row[0] == today

def has_any_completion(user_id):
    """
    Returns True if the user has EVER completed at least one habit.
    Used ONLY for Day-0 detection.
    """
    from database.db import get_connection

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 1
        FROM daily_logs d
        JOIN sub_goals s ON d.sub_goal_id = s.id
        JOIN goals g ON s.goal_id = g.id
        WHERE g.user_id = ?
          AND d.completed = 1
        LIMIT 1
        """,
        (user_id,)
    )

    return cur.fetchone() is not None


