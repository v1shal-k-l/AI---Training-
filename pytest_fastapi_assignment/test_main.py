from fastapi.testclient import TestClient
from main import app, tasks
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_tasks():
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Prepare report", "status": "Pending"},
        {"id": 2, "title": "Review invoice", "status": "Completed"},
        {"id": 3, "title": "Update dashboard", "status": "Pending"},
    ])


def test_get_tasks():
    response = client.get("/tasks")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_task_by_id():
    response = client.get("/tasks/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1


def test_get_invalid_task():
    response = client.get("/tasks/999")

    assert response.status_code == 404


def test_add_task():
    response = client.post(
        "/tasks",
        json={
            "id": 4,
            "title": "Check server logs",
            "status": "Pending"        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 4
    assert data["title"] == "Check server logs"
    assert data["status"] == "Pending"


def test_invalid_post():
    response = client.post(
        "/tasks",
        json={
            "id": 5,
            "title": "Missing Status"
        }
    )

    assert response.status_code == 422


def test_update_task():
    response = client.put(
        "/tasks/2",
        json={
            "id": 2,
            "title": "Review invoice",
            "status": "Completed"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 2
    assert data["status"] == "Completed"


def test_delete_task():
    response = client.delete("/tasks/3")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Task deleted successfully"


def test_get_deleted_task():
    client.delete("/tasks/3")

    response = client.get("/tasks/3")

    assert response.status_code == 404