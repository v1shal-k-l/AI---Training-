import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Always read Backend/.env, whatever folder the server is started from.
load_dotenv(BACKEND_DIR / ".env")

# ---------- Model (Goedel inference, OpenAI-compatible) ----------
GOEDEL_API_KEY = os.getenv("GOEDEL_API_KEY")
GOEDEL_BASE_URL = os.getenv("GOEDEL_BASE_URL", "https://api.goedelmachines.com/v1")
MODEL_ID = os.getenv("AI_MODEL_ID", "deepseek/deepseek-v4.1-flash")

MODEL_TEMPERATURE = 0.2       # low = more consistent summaries
MODEL_MAX_TOKENS = 600
MODEL_TIMEOUT_S = 60

# ---------- MLflow ----------
# Default: a local SQLite file in Backend/, so no MLflow server is needed to record traces.
# View them with (from the Backend folder):  mlflow ui --backend-store-uri sqlite:///mlflow.db
MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "sqlite:///" + (BACKEND_DIR / "mlflow.db").as_posix(),
)
MLFLOW_EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT", "wealth-insights")

# Where the MLflow UI runs (used to build "Open in MLflow" links for the React app).
MLFLOW_UI_URL = os.getenv("MLFLOW_UI_URL", "http://localhost:5000").rstrip("/")


def require_api_key() -> str:
    if not GOEDEL_API_KEY:
        raise RuntimeError("GOEDEL_API_KEY is missing - add it to Backend/.env")
    return GOEDEL_API_KEY
