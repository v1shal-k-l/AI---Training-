import psycopg2

from psycopg2.extras import RealDictCursor


def get_connection():

    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="task_allotment_db",
        user="postgres",
        password="Admin@123",
        cursor_factory=RealDictCursor
    )