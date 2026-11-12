from fastapi import APIRouter

from database import get_connection

router = APIRouter()


@router.get("/dashboard/summary")
def dashboard_summary():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) total_users
        FROM users
        WHERE is_active = TRUE
        """
    )

    users = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*) total_projects
        FROM projects
        """
    )

    projects = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*) total_tasks
        FROM tasks
        """
    )

    tasks = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*) completed
        FROM tasks
        WHERE status='Completed'
        """
    )

    completed = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*) progress
        FROM tasks
        WHERE status='In Progress'
        """
    )

    progress = cursor.fetchone()

    cursor.execute(
        """
        SELECT COUNT(*) blocked
        FROM tasks
        WHERE status='Blocked'
        """
    )

    blocked = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "total_users":
            users["total_users"],

        "total_projects":
            projects["total_projects"],

        "total_tasks":
            tasks["total_tasks"],

        "completed_tasks":
            completed["completed"],

        "in_progress_tasks":
            progress["progress"],

        "blocked_tasks":
            blocked["blocked"]
    }