from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from users import router as user_router
from projects import router as project_router
from tasks import router as task_router
from dashboard import router as dashboard_router
from audit_routes import router as audit_router

app = FastAPI(
    title="Task Allotment Management System"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(user_router)

app.include_router(project_router)

app.include_router(task_router)
#
app.include_router(dashboard_router)

app.include_router(audit_router)

@app.get("/")
def root():

    return {
        "message":
            "Task Allotment Management System API Running"
    }
