import redis
import json
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True
)

def save_context(session_id, context):

    redis_client.set(
        session_id,
        json.dumps(context),
        ex=3600
    )

def get_context(session_id):

    data = redis_client.get(session_id)

    if not data:
        return {}

    return json.loads(data)