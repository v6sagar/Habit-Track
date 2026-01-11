from database.db import get_connection
from datetime import date, timedelta
from database.db import get_connection





from datetime import date
from database.db import get_connection


def roll_over_unfinished_tasks(user_id):
    """
    Move all unfinished tasks with due_date < today to today.
    Safe to run multiple times per day.
    """

    conn = get_connection()
    cur = conn.cursor()

    today = date.today().isoformat()

    # Find unfinished tasks from ANY past date
    cur.execute(
        """
        SELECT id
        FROM todos
        WHERE user_id = ?
          AND completed = 0
          AND due_date < ?
        """,
        (user_id, today)
    )

    task_ids = [row[0] for row in cur.fetchall()]

    if not task_ids:
        return

    # Move them to today
    cur.executemany(
        """
        UPDATE todos
        SET due_date = ?
        WHERE id = ?
        """,
        [(today, tid) for tid in task_ids]
    )

    conn.commit()

# -----------------------------
# Fetch tasks
# -----------------------------
def get_tasks(user_id, date):
    conn = get_connection()
    cur = conn.cursor()
    return cur.execute("""
        SELECT id, task, completed
        FROM todos
        WHERE user_id=? AND due_date=?
        ORDER BY id
    """, (user_id, date)).fetchall()


# -----------------------------
# Add task
# -----------------------------
def add_task(user_id, task, date):
    conn = get_connection()
    conn.execute("""
        INSERT INTO todos (user_id, task, due_date)
        VALUES (?, ?, ?)
    """, (user_id, task, date))
    conn.commit()


# -----------------------------
# Toggle completion
# -----------------------------
def set_status(task_id, completed):
    conn = get_connection()
    conn.execute("""
        UPDATE todos SET completed=?
        WHERE id=?
    """, (completed, task_id))
    conn.commit()


# -----------------------------
# Delete task
# -----------------------------
def delete_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM todos WHERE id=?", (task_id,))
    conn.commit()


