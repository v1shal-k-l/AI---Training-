from db import get_connection

def get_trip(trip_id):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            trip_id,
            destination,
            start_date,
            end_date,
            purpose
        FROM trips
        WHERE trip_id=%s
        """,
        (trip_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row