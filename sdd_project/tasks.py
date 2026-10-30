from fastapi import APIRouter

from database import get_connection

from schemas import (
    TaskCreate,
    AssignTaskRequest,
    UpdateStatusRequest,
    CommentCreate,
    TaskUpdate
)

router = APIRouter()


# -----------------------------------
# GET ALL TASKS
# -----------------------------------
@router.get("/tasks")
def get_tasks():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY id
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# -----------------------------------
# CREATE TASK
# -----------------------------------
@router.post("/tasks")
def create_task(task: TaskCreate):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks
        (
            project_id,
            task_name,
            description,
            assigned_to,
            priority,
            status,
            estimated_hours
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s)
        RETURNING *
        """,
        (
            task.project_id,
            task.task_name,
            task.description,
            task.assigned_to,
            task.priority,
            task.status,
            task.estimated_hours
        )
    )

    result = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return result


# -----------------------------------
# UPDATE TASK
# -----------------------------------
@router.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdate
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET
            task_name=%s,
            description=%s,
            priority=%s,
            status=%s,
            estimated_hours=%s
        WHERE id=%s
        RETURNING *
        """,
        (
            task.task_name,
            task.description,
            task.priority,
            task.status,
            task.estimated_hours,
            task_id
        )
    )

    result = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return result


# -----------------------------------
# DELETE TASK
# -----------------------------------
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id=%s
        RETURNING *
        """,
        (task_id,)
    )

    result = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return result


# -----------------------------------
# ADD COMMENT
# -----------------------------------
@router.post("/comments")
def add_comment(comment: CommentCreate):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO task_comments
        (
            task_id,
            user_id,
            comment_text
        )
        VALUES
        (%s,%s,%s)
        RETURNING *
        """,
        (
            comment.task_id,
            comment.user_id,
            comment.comment_text
        )
    )

    result = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return result


# -----------------------------------
# SEARCH TASKS
# -----------------------------------
@router.get("/tasks/search/{keyword}")
def search_tasks(keyword: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE
            task_name ILIKE %s
            OR description ILIKE %s
        """,
        (
            f"%{keyword}%",
            f"%{keyword}%"
        )
    )

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# -----------------------------------
# FILTER BY STATUS
# -----------------------------------
@router.get("/tasks/status/{status}")
def get_tasks_by_status(status: str):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE status=%s
        """,
        (status,)
    )

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# -----------------------------------
# PAGINATION
# -----------------------------------
@router.get("/tasks/page")
def task_page(
    page: int = 1,
    size: int = 10
):

    offset = (page - 1) * size

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM tasks
        ORDER BY id
        LIMIT %s
        OFFSET %s
        """,
        (
            size,
            offset
        )
    )

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# -----------------------------------
# TASK HISTORY
# -----------------------------------
@router.get("/tasks/{task_id}/history")
def get_task_history(task_id: int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM task_status_history
        WHERE task_id=%s
        ORDER BY changed_at DESC
        """,
        (task_id,)
    )

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result