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
def create_post():
    data = {
        "title": "Test post",
        "description": "This is a test post.",
        "creator_id": "1",
        "is_private": False,
        "tags": ["test", "pytest"]
    }

    response = httpx.post(f"{BASE_URL}/posts", json=data)
    assert response.status_code == 200
    return response.json()


def test_create_post():
    data = {
        "title": "Test post",
        "description": "This is a test post.",
        "creator_id": "1",
        "is_private": False,
        "tags": ["test", "pytest"],
    }

    response = httpx.post(f"{BASE_URL}/posts", json=data)
    assert response.status_code == 200

    post = response.json()
    assert post["title"] == data["title"]
    assert post["description"] == data["description"]
    assert post["creator_id"] == data["creator_id"]


def test_get_post(create_post):
    post_id = create_post["id"]
    response = httpx.get(f"{BASE_URL}/posts/{post_id}?requester_id=1")
    assert response.status_code == 200

    post = response.json()
    assert post["id"] == post_id
    assert post["title"] == create_post["title"]


def test_not_existing_post():
    response = httpx.get(f"{BASE_URL}/posts/123?requester_id=1")
    assert response.status_code == 404


def test_update_post(create_post):
    post_id = create_post["id"]
    updated_data = {
        "title": "Updated post",
        "description": "This is an updated test post.",
        "is_private": False,
        "tags": ["updated", "pytest"],
        "requester_id": "1",
    }

    response = httpx.put(f"{BASE_URL}/posts/{post_id}", json=updated_data)
    assert response.status_code == 200

    post = response.json()
    assert post["title"] == updated_data["title"]
    assert post["description"] == updated_data["description"]
    assert post["tags"] == updated_data["tags"]


def test_update_not_existing_post():
    updated_data = {
        "title": "Updated post",
        "description": "This is an updated test post.",
        "is_private": False,
        "tags": ["updated", "pytest"],
        "requester_id": "1",
    }

    response = httpx.put(f"{BASE_URL}/posts/123", json=updated_data)
    assert response.status_code == 404


def test_list_posts():
    response = httpx.get(f"{BASE_URL}/posts?page=1&page_size=5&requester_id=1")
    assert response.status_code == 200

    posts = response.json()
    assert "posts" in posts
    assert isinstance(posts["posts"], list)
    assert len(posts["posts"]) != 0


def test_delete_post(create_post):
    post_id = create_post["id"]
    response = httpx.delete(f"{BASE_URL}/posts/{post_id}?requester_id=1")
    assert response.status_code == 204

    response = httpx.get(f"{BASE_URL}/posts/{post_id}?requester_id=1")
    assert response.status_code == 404


def test_delete_not_existing_post():
    response = httpx.delete(f"{BASE_URL}/posts/123?requester_id=1")
    assert response.status_code == 404
