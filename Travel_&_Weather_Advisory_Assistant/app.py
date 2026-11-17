import os
import json
import redis
import psycopg2
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    HTTPException
)

from pydantic import BaseModel

from langchain_openai import ChatOpenAI

from weather import get_weather

from guardrails import (
    run_trip_guardrails,
    run_chat_guardrails,
    validate_weather_response
)


load_dotenv()

app = FastAPI(
    title="Travel Weather Advisor"
)

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True
)


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3
)

def get_connection():

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


class TripRequest(BaseModel):

    employee_id: str
    destination: str
    start_date: str
    end_date: str
    purpose: str


class ChatRequest(BaseModel):

    session_id: str
    question: str
    trip_id: int | None = None



@app.post("/trips")
def create_trip(request: TripRequest):

    valid, message = (
        run_trip_guardrails(
            request.destination,
            request.purpose,
            request.start_date,
            request.end_date
        )
    )

    if not valid:

        raise HTTPException(
            status_code=400,
            detail=message
        )

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO trips
        (
            employee_id,
            destination,
            start_date,
            end_date,
            purpose
        )
        VALUES
        (%s,%s,%s,%s,%s)
        RETURNING trip_id
        """,
        (
            request.employee_id,
            request.destination,
            request.start_date,
            request.end_date,
            request.purpose
        )
    )

    trip_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return {
        "success": True,
        "trip_id": trip_id
    }


@app.get("/trips/{trip_id}")
def retrieve_trip(trip_id: int):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM trips
        WHERE trip_id=%s
        """,
        (trip_id,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:

        raise HTTPException(
            status_code=404,
            detail="Trip not found."
        )

    return {
        "trip_id": row[0],
        "employee_id": row[1],
        "destination": row[2],
        "start_date": str(row[3]),
        "end_date": str(row[4]),
        "purpose": row[5],
        "status": row[6]
    }

@app.post(
    "/chat",
    response_class=PlainTextResponse
)
def ask_assistant(request: ChatRequest):

    valid, message = (
        run_chat_guardrails(
            request.question
        )
    )

    if not valid:

        raise HTTPException(
            status_code=400,
            detail=message
        )

    session_key = (
        f"travel:{request.session_id}"
    )

    trip = None

    if request.trip_id:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT *
            FROM trips
            WHERE trip_id=%s
            """,
            (request.trip_id,)
        )

        trip = cur.fetchone()

        cur.close()
        conn.close()

        if not trip:

            raise HTTPException(
                status_code=404,
                detail="Trip not found."
            )

        redis_client.set(
            session_key,
            json.dumps(
                {
                    "trip_id": trip[0],
                    "destination": trip[2]
                }
            ),
            ex=3600
        )

    else:

        previous = redis_client.get(
            session_key
        )

        if not previous:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Please provide "
                    "trip_id for first query."
                )
            )

        previous = json.loads(
            previous
        )

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT *
            FROM trips
            WHERE trip_id=%s
            """,
            (previous["trip_id"],)
        )

        trip = cur.fetchone()

        cur.close()
        conn.close()

    destination = trip[2]

    weather = get_weather(
        destination
    )

    valid, message = (
        validate_weather_response(
            weather
        )
    )

    if not valid:

       return message

    prompt = f"""
    You are a friendly AI-powered Travel & Weather Advisory Assistant.

    Respond directly to the employee in a professional conversational style.

    Rules:
    - Do not return JSON.
    - Do not use markdown.
    - Do not use numbered lists.
    - Sound like a chatbot.
    - Mention the destination naturally.
    - Include weather summary.
    - Include practical travel advice.
    - Include 3 to 4 packing suggestions.
    - Keep the response under 150 words.

    Trip Details:
    Destination: {destination}

    Purpose:
    {trip[5]}

    Weather Information:
    Maximum Temperature: {weather['max_temp']}°C
    Minimum Temperature: {weather['min_temp']}°C
    Rain Probability: {weather['rain_probability']}%

    Employee Question:
    {request.question}
    """

    response = llm.invoke(
        prompt
    )

    return response.content

@app.get("/")
def home():

    return {
        "status": "running"
    }