from fastapi.testclient import TestClient

from app.main import app


def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser_auth",
            "email": "test_auth@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "testuser_auth"
    assert data["email"] == "test_auth@example.com"

    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_email_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "another_test_user",
            "email": "test_auth@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409


def test_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test_auth@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test_auth@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 401


def test_me(client):
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test_auth@example.com",
            "password": "password123",
        },
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "testuser_auth"
    assert data["email"] == "test_auth@example.com"

def test_me_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"