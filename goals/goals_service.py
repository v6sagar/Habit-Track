from database.db import get_connection

def add_goal(user_id, name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO goals (user_id, name) VALUES (?, ?)",
        (user_id, name)
    )
    conn.commit()

def add_sub_goal(goal_id, name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sub_goals (goal_id, name) VALUES (?, ?)",
        (goal_id, name)
    )
    conn.commit()

def delete_goal(goal_id):
    conn = get_connection()
    cur = conn.cursor()

    # delete sub-goals first
    cur.execute("DELETE FROM sub_goals WHERE goal_id=?", (goal_id,))
    cur.execute("DELETE FROM goals WHERE id=?", (goal_id,))

    conn.commit()

def delete_sub_goal(sub_goal_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE sub_goals SET active=0 WHERE id=?",
        (sub_goal_id,)
    )
    conn.commit()

def get_goals(user_id):
    conn = get_connection()
    cur = conn.cursor()

    goals = cur.execute(
        "SELECT id, name FROM goals WHERE user_id=?",
        (user_id,)
    ).fetchall()

    result = []
    for g in goals:
        subs = cur.execute(
            """
            SELECT id, name FROM sub_goals
            WHERE goal_id=? AND active=1
            """,
            (g[0],)
        ).fetchall()
        result.append((g, subs))

    return result

