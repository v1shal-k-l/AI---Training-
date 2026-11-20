from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)