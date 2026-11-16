# AI-Powered Travel & Weather Advisory Assistant

## Overview

The AI-Powered Travel & Weather Advisory Assistant helps employees prepare for upcoming business trips by combining trip management, weather forecasting, conversational AI, and session memory.

The application allows employees to:

- Register business trips.
- Retrieve previously saved trip information.
- Ask weather-related travel questions.
- Receive personalized travel recommendations.
- Continue follow-up conversations without repeatedly providing trip details.

The solution integrates PostgreSQL for trip storage, Redis for conversation memory, Open-Meteo for weather forecasts, and OpenRouter through LangChain for generating travel advice.

---

## Architecture

```text
Employee
   │
   ▼
FastAPI (app.py)
   │
   ├── PostgreSQL (Trip Storage)
   │
   ├── Redis (Session Memory)
   │
   ├── Open-Meteo API
   │
   └── OpenRouter + LangChain
           │
           ▼
      Travel Advisory
```

---

## Features

### Trip Management

- Create new business trips.
- Store trip details in PostgreSQL.
- Retrieve saved trip information.

### Weather Advisory

- Resolve destination coordinates using Open-Meteo Geocoding API.
- Retrieve live weather forecasts from Open-Meteo Forecast API.
- Provide weather-aware travel recommendations.

### Conversational Assistant

- Generate travel advice using LangChain and OpenRouter.
- Produce human-like responses in chatbot form.
- Include weather summaries and travel suggestions.

### Session Memory

- Store conversation context using Redis.
- Support follow-up questions without repeating the destination.
- Maintain isolated session histories.

### Guardrails

- Travel date validation.
- Destination validation.
- Prompt injection detection.
- Question length validation.
- Weather service validation.
- Graceful handling of invalid inputs.

---

## Technology Stack

| Component | Technology |
|------------|------------|
| API Framework | FastAPI |
| Database | PostgreSQL |
| Database Driver | psycopg2 |
| Session Memory | Redis |
| AI Framework | LangChain |
| LLM Provider | OpenRouter |
| Weather Service | Open-Meteo |
| Language | Python |

---

## Project Structure

```text
travel_weather_advisor/

│
├── app.py
├── weather.py
├── advisor.py
├── guardrails.py
│
├── schema.sql
├── requirements.txt
├── .env
├── .env.example
│
└── README.md
```

---

## Database Setup

Create the database:

```sql
CREATE DATABASE travel_db;
```

Execute the schema:

```sql
CREATE TABLE trips (
    trip_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(50) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    purpose TEXT,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Environment Configuration

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_api_key

OPENROUTER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free

DB_HOST=localhost
DB_PORT=5432
DB_NAME=travel_db
DB_USER=postgres
DB_PASSWORD=Admin@123

REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Start Redis

Using Docker:

```bash
docker run -d --name redis-server -p 6379:6379 redis
```

If the container already exists:

```bash
docker start redis-server
```

---

## Run the Application

```bash
uvicorn app:app --reload
```

---

## Swagger Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

---

# API Endpoints

## Create Trip

### Endpoint

```http
POST /trips
```

### Request

```json
{
  "employee_id": "EMP104",
  "destination": "Jaipur",
  "start_date": "2026-11-20",
  "end_date": "2026-11-23",
  "purpose": "Client Meeting"
}
```

### Response

```json
{
  "success": true,
  "trip_id": 1
}
```

---

## Retrieve Trip

### Endpoint

```http
GET /trips/{trip_id}
```

### Response

```json
{
  "trip_id": 1,
  "employee_id": "EMP104",
  "destination": "Jaipur",
  "start_date": "2026-11-20",
  "end_date": "2026-11-23",
  "purpose": "Client Meeting",
  "status": "ACTIVE"
}
```

---

## Travel Advisory Chat

### Endpoint

```http
POST /chat
```

### First Request

```json
{
  "session_id": "session123",
  "trip_id": 1,
  "question": "What weather should I expect for my trip?"
}
```

### Example Response

```text
For your upcoming trip to Jaipur, you can expect warm temperatures and a low chance of rainfall. Lightweight business attire, comfortable shoes, sunglasses, and a reusable water bottle are recommended. A light jacket may be useful in the evenings. Have a productive and comfortable trip.
```

---

### Follow-Up Request

```json
{
  "session_id": "session123",
  "question": "Should I carry an umbrella?"
}
```

### Example Response

```text
Based on the current forecast for Jaipur, rain probability is low, so carrying an umbrella is optional. A compact umbrella can still be useful in case of unexpected weather changes.
```

---

## Health Check

### Endpoint

```http
GET /
```

### Response

```json
{
  "status": "running"
}
```

---

# Example Test Scenarios

### Scenario 1

Create a new business trip.

Expected Result:

- Trip is validated.
- Trip is stored in PostgreSQL.
- Trip ID is generated.

---

### Scenario 2

Request travel advice.

Expected Result:

- Trip details retrieved from PostgreSQL.
- Weather retrieved from Open-Meteo.
- Travel advice generated by LangChain and OpenRouter.

---

### Scenario 3

Ask a follow-up question.

Expected Result:

- Redis retrieves previous destination context.
- Assistant responds without requiring trip ID.

---

### Scenario 4

Retrieve a saved trip.

Expected Result:

- Previously stored trip details are returned.

---

### Scenario 5

Provide an invalid destination.

Expected Result:

- Assistant reports destination could not be located.
- No weather information is fabricated.
 
---

## Author

AI-Powered Travel & Weather Advisory Assistant

Travel preparation assistant using FastAPI, PostgreSQL, Redis, Open-Meteo, LangChain, and OpenRouter.