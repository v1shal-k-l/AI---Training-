import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Always read Backend/.env, whatever folder the server is started from.
load_dotenv(BACKEND_DIR / ".env")

# ---------- Model provider ----------
# LLM_PROVIDER=azure   -> Azure OpenAI (AZURE_OPENAI_API_KEY / _BASE_URL / _DEPLOYMENT)
# LLM_PROVIDER=goedel  -> Goedel inference (GOEDEL_API_KEY / GOEDEL_BASE_URL / AI_MODEL_ID)   [default]
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "goedel").strip().lower()
IS_AZURE = LLM_PROVIDER == "azure"

if IS_AZURE:
    API_KEY_NAME = "AZURE_OPENAI_API_KEY"
    LLM_BASE_URL = os.getenv("AZURE_OPENAI_BASE_URL")          # https://<resource>.openai.azure.com/openai/v1
    MODEL_ID = os.getenv("AZURE_OPENAI_DEPLOYMENT")            # the deployment name, e.g. gpt-6-astra
    # Reasoning model: no temperature; the token limit also covers its hidden reasoning.
    REASONING_EFFORT = os.getenv("AZURE_REASONING_EFFORT", "low")
    MODEL_MAX_TOKENS = 4000
else:
    API_KEY_NAME = "GOEDEL_API_KEY"
    LLM_BASE_URL = os.getenv("GOEDEL_BASE_URL", "https://api.goedelmachines.com/v1")
    MODEL_ID = os.getenv("AI_MODEL_ID", "deepseek/deepseek-v4.1-flash")
    MODEL_MAX_TOKENS = 600

LLM_API_KEY = os.getenv(API_KEY_NAME)

MODEL_TEMPERATURE = 0.2       # Goedel only (low = more consistent summaries)
MODEL_TIMEOUT_S = 90

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
    if not LLM_API_KEY:
        raise RuntimeError(f"{API_KEY_NAME} is missing - add it to Backend/.env (LLM_PROVIDER={LLM_PROVIDER})")
    if not LLM_BASE_URL or not MODEL_ID:
        raise RuntimeError(f"Base URL or model/deployment is missing in Backend/.env (LLM_PROVIDER={LLM_PROVIDER})")
    return LLM_API_KEY