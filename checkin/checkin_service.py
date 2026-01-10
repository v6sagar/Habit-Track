from database.db import get_connection

def set_status(sub_goal_id, date, completed):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO daily_logs (sub_goal_id, date, completed)
        VALUES (?, ?, ?)
        ON CONFLICT(sub_goal_id, date)
        DO UPDATE SET completed = excluded.completed
        """,
        (sub_goal_id, date, completed)
    )

    conn.commit()


def get_status(sub_goal_id, date):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT completed
        FROM daily_logs
        WHERE sub_goal_id = ? AND date = ?
        """,
        (sub_goal_id, date)
    )

    row = cur.fetchone()
    return row[0] if row else None

