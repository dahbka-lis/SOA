from datetime import datetime, timezone

import subprocess
import pytest
import httpx
import time
import json

BASE_URL = "http://localhost:8080"
DOCKER_COMPOSE_FILE = "/home/daniil/soa/src/docker-compose.yml"


@pytest.fixture(scope="session", autouse=True)
def setup_services():
    subprocess.run(
        ["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d"], check=True
    )
    time.sleep(10)
    yield
    subprocess.run(["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "down"], check=True)


@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "password": "password123",
        "email": "test@example.com",
    }


def test_register_success(test_user):
    response = httpx.post(f"{BASE_URL}/register", json=test_user)

    assert response.status_code == 200


def test_register_duplicate(test_user):
    httpx.post(f"{BASE_URL}/register", json=test_user)
    response = httpx.post(f"{BASE_URL}/register", json=test_user)

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


def test_login_success(test_user):
    httpx.post(f"{BASE_URL}/register", json=test_user)
    login_data = {"username": test_user["username"], "password": test_user["password"]}
    response = httpx.post(f"{BASE_URL}/login", json=login_data)

    assert response.status_code == 200
    assert "token" in response.json()


def test_login_invalid_password(test_user):
    httpx.post(f"{BASE_URL}/register", json=test_user)
    login_data = {"username": test_user["username"], "password": "wrongpassword"}
    response = httpx.post(f"{BASE_URL}/login", json=login_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"


def test_get_profile_success(test_user):
    username = test_user["username"]
    httpx.post(f"{BASE_URL}/register", json=test_user)
    response = httpx.get(
        f"{BASE_URL}/profile?username={username}"
    )

    assert response.status_code == 200
    assert "user_id" in response.json()


def test_get_profile_not_found():
    username = "49123abacaba"
    response = httpx.get(f"{BASE_URL}/profile?username={username}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_profile_success(test_user):
    httpx.post(f"{BASE_URL}/register", json=test_user)
    login_data = {"username": test_user["username"], "password": test_user["password"]}
    login_response = httpx.post(f"{BASE_URL}/login", json=login_data)
    token = login_response.json()["token"]

    update_data = {
        "token": token,
        "phone": "+12345678",
        "email": "doej@gmail.ru",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I'm so tired",
        "date_of_birth": datetime(2000, 3, 11).isoformat(),
        "avatar": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80_%D0%9F%D1%83%D1%82%D0%B8%D0%BD_%2808-03-2024%29_%28cropped%29_%28higher_res%29.jpg/260px-%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80_%D0%9F%D1%83%D1%82%D0%B8%D0%BD_%2808-03-2024%29_%28cropped%29_%28higher_res%29.jpg",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    response = httpx.put(f"{BASE_URL}/profile", json=update_data)
    assert response.status_code == 200


def test_update_profile_invalid_token():
    update_data = {
        "token": "invalid",
        "phone": "+12345678",
        "email": "doej@gmail.ru",
        "first_name": "John",
        "last_name": "Doe",
        "bio": "I'm so tired",
        "date_of_birth": datetime(2000, 3, 11).isoformat(),
        "avatar": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80_%D0%9F%D1%83%D1%82%D0%B8%D0%BD_%2808-03-2024%29_%28cropped%29_%28higher_res%29.jpg/260px-%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80_%D0%9F%D1%83%D1%82%D0%B8%D0%BD_%2808-03-2024%29_%28cropped%29_%28higher_res%29.jpg",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    response = httpx.put(f"{BASE_URL}/profile", json=update_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired session"
