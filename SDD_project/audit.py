from database import get_connection


def write_audit_log(
    user_id,
    action,
    entity,
    entity_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO audit_logs
        (
            user_id,
            action,
            entity,
            entity_id
        )
        VALUES
        (%s,%s,%s,%s)
        """,
        (
            user_id,
            action,
            entity,
            entity_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()