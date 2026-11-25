# WAM Observability – AI-Powered Wealth & Asset Management

Portfolio app with an **AI insight agent** that is fully observable:

- **React portal** (`wealth-portal/`) – portfolios, holdings, AI insights, feedback, observability dashboard, Trace Explorer
- **FastAPI backend** (`Backend/`) – REST APIs on PostgreSQL
- **AI agent** (`Backend/ai/`) – LangChain agent + read-only portfolio tools, model via the Goedel inference API
- **MLflow** – records every AI call as a trace (prompt, tool calls, tokens, latency) and runs the evaluation (`Backend/evaluation/`)

```
Browser ──► React (5173) ──► FastAPI (8000) ──► PostgreSQL (wealth_observability_db)
                                   │
                                   └──► AI agent ──► Goedel model API
                                            │
                                            └──► MLflow traces ──► Backend/mlflow.db ──► MLflow UI (5000)
```

When you run this setup, you get **4 things running**: PostgreSQL, the FastAPI backend, the React app and the MLflow UI.

---

## 1. Prerequisites

| Tool | Version used | Check |
|---|---|---|
| Python | 3.12+ (developed on 3.14) | `python --version` |
| Node.js | 20+ (developed on 22) | `node --version` |
| PostgreSQL | 15+ | `psql --version` |
| Git | any | `git --version` |

You also need a **Goedel API key**. Get one from https://inference.goedelmachines.com/docs/. A free key is fine.

---

## 2. Get the code

```powershell
git clone https://github.com/v1shal-k-l/AI---Training-.git
cd AI---Training-
git checkout sourabh
cd Capstone_Project
```

Folder layout:

```
Capstone_Project/
├── requirements.txt          Python packages (FastAPI, MLflow, LangChain, ...)
├── Backend/
│   ├── app.py                FastAPI app (all endpoints)
│   ├── database.py           Postgres connection (reads .env)
│   ├── db.sql                Database schema + sample data
│   ├── .env                  YOUR secrets (not in git, you create it, step 4)
│   ├── mlflow.db             MLflow store: traces + evaluation results
│   ├── mlruns/               MLflow artifact files
│   ├── ai/                   AI agent (config, llm, prompts, tools, agent)
│   └── evaluation/           Evaluation dataset, scorers, runner
└── wealth-portal/            React + Vite frontend
```

---

## 3. Python environment + MLflow install

From the `Capstone_Project` folder:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

This installs **MLflow** with the rest: FastAPI, LangChain, langchain-openai and openai. Check it:

```powershell
mlflow --version                     # should print 3.18 or newer
```

> If PowerShell blocks `Activate.ps1`, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## 4. Create `Backend/.env`

This file holds your secrets and is **never committed**. Create `Backend/.env` with:

```ini
# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wealth_observability_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password

# AI model (Goedel, OpenAI-compatible)
GOEDEL_API_KEY=your_goedel_key
```

Optional settings. The defaults below are used when you leave them out:

```ini
GOEDEL_BASE_URL=https://api.goedelmachines.com/v1
AI_MODEL_ID=deepseek/deepseek-v4.1-flash
MLFLOW_TRACKING_URI=sqlite:///<full path to Backend>/mlflow.db
MLFLOW_EXPERIMENT=wealth-insights
MLFLOW_UI_URL=http://localhost:5000      # used to build the "Open in MLflow" links
```

> The free Goedel key allows about 2 parallel requests and 60 requests per minute, and **keeps your prompts**. That's fine here because all portfolio data is synthetic.

---

## 5. Database (PostgreSQL)

`Backend/db.sql` creates the database, all tables and the sample data.

**Option A – pgAdmin**
1. Right-click *Databases* → *Create* → name it `wealth_observability_db`.
2. Open the *Query Tool* on that database and run `db.sql` **from the first `CREATE TABLE` line onwards**. Skip the `CREATE DATABASE` block at the top.

**Option B – psql**
```powershell
psql -U postgres -c "CREATE DATABASE wealth_observability_db;"
psql -U postgres -d wealth_observability_db -f Backend/db.sql
```
The `CREATE DATABASE` statement inside the file will fail because the database already exists. You can ignore that error; the tables and data are still created.

> The `CREATE DATABASE` block in `db.sql` uses the Windows locale `English_India.1252`. That's another reason to create the database yourself as shown above.

**Already have the database from an older version?** Add the new column once:
```sql
ALTER TABLE ai_runs ADD COLUMN IF NOT EXISTS mlflow_trace_id VARCHAR(64);
```

---

## 6. Start everything (3 terminals)

Activate the venv in every Python terminal: `.\venv\Scripts\Activate.ps1`.

### Terminal 1 – FastAPI backend (port 8000)
```powershell
cd Backend
uvicorn app:app --reload --port 8000
```
Check: http://localhost:8000/docs shows all the APIs.

> Always start it **from the `Backend` folder**, so it finds `.env` and `mlflow.db`.

### Terminal 2 – MLflow UI (port 5000)
```powershell
cd Backend
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```
Check: open http://localhost:5000 → experiment **wealth-insights** → **Traces** tab.

### Terminal 3 – React portal (port 5173)
```powershell
cd wealth-portal
npm install          # first time only
npm run dev
```
Check: open http://localhost:5173.

---

## 7. See it working end to end

1. In the React app, open **AI Insights**, choose a portfolio and click **Generate Insight**.
   - The backend runs the AI agent. The agent calls tools such as `calculate_allocation` and `check_concentration`, then writes a 3–5 sentence summary.
   - The run is saved in Postgres (`ai_runs` and `trace_events`), and MLflow records the full trace.
2. Click **View Trace** under the insight, or open **Trace Explorer** and enter the run ID. You see the stage waterfall and an **Open in MLflow ↗** button.
3. Click **Open in MLflow ↗**. MLflow opens the same run and shows:
   - the prompt and the model's answer
   - each tool call with its inputs and outputs
   - tokens and latency per step
   - tags: `run_id`, `portfolio_id`, `model_id`, `prompt_version`

The "Open in MLflow" button is a plain link that the backend builds (field `mlflow_url` in `/observability/runs/{id}`). The MLflow UI from Terminal 2 must be running for the link to load.

### Try the agent without the UI
```powershell
cd Backend
python -m ai.try_agent 1           # 1 = portfolio id
```
Refresh MLflow → a new trace appears.

---

## 8. Run the AI evaluation

The evaluation asks the agent 15 test questions. There are three kinds:
- normal questions it should answer
- questions it **must refuse**: investment advice, predictions, personal data, trades, off-topic questions, prompt injection
- edge cases: an unknown portfolio and a comparison

Four scorers grade every answer:

| Scorer | Type | Checks |
|---|---|---|
| `right_tools_used` | code | The agent called the expected tools (or no tools, for refusals) |
| `correct_answer` | code | Key facts and numbers match the database |
| `claims_grounded` | LLM judge | Every claim is backed by tool data, with nothing made up |
| `safe_and_compliant` | LLM judge | No advice or predictions, refuses when it should, and doesn't over-refuse |

```powershell
cd Backend
python -m evaluation.test_scorers              # sanity-check the scorers (free, instant)
python -m evaluation.run_eval --pilot          # 4 cases, quick check
python -m evaluation.run_eval                  # all 15 cases
```

The scorecard prints in the terminal. In MLflow, open **wealth-insights → Evaluation runs** (named `eval-qa-v1` / `pilot-qa-v1`) to see each question, its answer, its trace and its score.

---

## 9. About `mlflow.db` in git

`Backend/mlflow.db` is committed **on purpose**. When you clone, the MLflow UI already shows the team's past traces and evaluation runs. Each trace's steps are stored inside the database, so it works from any folder.

- Your own runs are added to your local copy. **Don't commit your `mlflow.db` changes** unless the team agrees, because a binary file can't be merged. To discard yours: `git checkout -- Backend/mlflow.db`
- To start with an empty MLflow, stop the MLflow UI and delete `Backend/mlflow.db` and `Backend/mlruns/`. Both are recreated on the next AI run.
- The **Open in MLflow** links only exist for runs in *your* Postgres. Shared traces from other machines are browsed directly in the MLflow UI.

---

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `GOEDEL_API_KEY is missing` | Add it to `Backend/.env` and restart uvicorn |
| Insight fails with `AUTH_ERROR` | Wrong or expired Goedel key |
| Insight fails with `RATE_LIMIT` | Free-key limit reached; wait a minute |
| Backend can't connect to DB | Check the `DB_*` values in `.env` and that Postgres is running |
| `column "mlflow_trace_id" does not exist` | Run the `ALTER TABLE` from step 5 |
| MLflow UI is empty | Start it **from `Backend/`** with `--backend-store-uri sqlite:///mlflow.db`, then pick experiment **wealth-insights** |
| "Open in MLflow" page doesn't load | Start the MLflow UI (Terminal 2), or fix `MLFLOW_UI_URL` |
| "No MLflow trace" badge | The run was created before tracing was added; generate a new insight |
| `database is locked` (SQLite) | Close extra MLflow UI or eval processes that use `mlflow.db` |
| React shows network errors | Backend not running on port 8000 (`BASE_URL` in `wealth-portal/src/api/api.js`) |

---

## Ports at a glance

| Service | URL |
|---|---|
| React portal | http://localhost:5173 |
| FastAPI + Swagger | http://localhost:8000/docs |
| MLflow UI | http://localhost:5000 |
| PostgreSQL | localhost:5432 |
