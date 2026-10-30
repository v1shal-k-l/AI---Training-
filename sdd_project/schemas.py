
from pydantic import BaseModel

class ProjectUpdate(BaseModel):
    project_name: str
    description: str
    status: str

class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreate(BaseModel):

    employee_id: str

    full_name: str

    email: str

    password: str

    role: str

    team_id: int

    created_by: int


class ProjectCreate(BaseModel):

    project_name: str

    description: str

    status: str

    manager_id: int

    created_by: int


class TaskCreate(BaseModel):

    project_id: int

    task_name: str

    description: str

    assigned_to: int

    priority: str

    status: str

    estimated_hours: int


class AssignTaskRequest(BaseModel):

    assigned_to: int

    assigned_by: int


class UpdateStatusRequest(BaseModel):

    user_id: int

    status: str


class CommentCreate(BaseModel):

    task_id: int

    user_id: int

    comment_text: str

class TaskUpdate(BaseModel):

    task_name: str

    description: str

    priority: str

    status: str

    estimated_hours: int