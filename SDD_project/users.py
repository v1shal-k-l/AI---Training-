from fastapi import APIRouter
from fastapi import HTTPException

from database import get_connection

from security import create_access_token

from schemas import LoginRequest
from schemas import UserCreate

router = APIRouter()


# ------------------------------------------
# LOGIN
# ------------------------------------------
@router.post("/login")
def login(request: LoginRequest):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email=%s
        AND is_active=TRUE
        """,
        (request.email,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    # Plain text password check (temporary)
    if request.password.strip() != user["password_hash"]:

        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    access_token = create_access_token(
        {
            "user_id": user["id"],
            "role": user["role"]
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user["full_name"],
        "role": user["role"]
    }


# ------------------------------------------
# GET USERS
# ------------------------------------------
@router.get("/users")
def get_users():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE is_active = TRUE
        ORDER BY id
        """
    )

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return users


# ------------------------------------------
# CREATE USER
# ------------------------------------------
@router.post("/users")
def create_user(user: UserCreate):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (
            employee_id,
            full_name,
            email,
            password_hash,
            role,
            team_id,
            is_active
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,TRUE)
        RETURNING *
        """,
        (
            user.employee_id,
            user.full_name,
            user.email,
            user.password.strip(),
            user.role,
            user.team_id
        )
    )

    result = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return result


# ------------------------------------------
# DEACTIVATE USER (SOFT DELETE)
# ------------------------------------------
@router.delete("/users/{user_id}")
def deactivate_user(user_id: int):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET is_active = FALSE
        WHERE id=%s
        RETURNING *
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return result