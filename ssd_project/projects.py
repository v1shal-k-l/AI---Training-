from fastapi import APIRouter
from fastapi import Depends

from database import get_connection

from security import require_manager_or_admin

from audit import write_audit_log

from schemas import (
    ProjectCreate,
    ProjectUpdate
)

router = APIRouter()


@router.get("/projects")
def get_projects():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM projects
        ORDER BY id
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


@router.post("/projects")
def create_project(
    project: ProjectCreate,
    current_user=Depends(
        require_manager_or_admin
    )
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO projects
        (
            project_name,
            description,
            status,
            manager_id
        )
        VALUES
        (%s,%s,%s,%s)
        RETURNING *
        """,
        (
            project.project_name,
            project.description,
            project.status,
            project.manager_id
        )
    )

    result = cursor.fetchone()

    conn.commit()

    write_audit_log(
        current_user["user_id"],
        "Project Created",
        "Project",
        result["id"]
    )

    cursor.close()
    conn.close()

    return result


@router.put("/projects/{project_id}")
def update_project(
    project_id: int,
    project: ProjectUpdate,
    current_user=Depends(
        require_manager_or_admin
    )
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE projects
        SET
            project_name=%s,
            description=%s,
            status=%s
        WHERE id=%s
        RETURNING *
        """,
        (
            project.project_name,
            project.description,
            project.status,
            project_id
        )
    )

    result = cursor.fetchone()

    conn.commit()

    write_audit_log(
        current_user["user_id"],
        "Project Updated",
        "Project",
        project_id
    )

    cursor.close()
    conn.close()

    return result


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user=Depends(
        require_manager_or_admin
    )
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM projects
        WHERE id=%s
        RETURNING *
        """,
        (project_id,)
    )

    result = cursor.fetchone()

    conn.commit()

    write_audit_log(
        current_user["user_id"],
        "Project Deleted",
        "Project",
        project_id
    )

    cursor.close()
    conn.close()

    return result