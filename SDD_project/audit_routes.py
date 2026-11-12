from fastapi import APIRouter

from database import get_connection

router = APIRouter()


@router.get("/audit")
def get_audit_logs():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY id DESC
        """
    )

    logs = cursor.fetchall()

    cursor.close()

    conn.close()

    return logs