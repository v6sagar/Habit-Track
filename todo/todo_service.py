from database.db import get_connection

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


