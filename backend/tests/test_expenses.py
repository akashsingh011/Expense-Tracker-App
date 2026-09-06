from fastapi.testclient import TestClient

from app.main import app
import uuid


def test_expenses_requires_authentication(client):
    response = client.get("/api/v1/expenses")
    assert response.status_code == 401


def register_and_login(client, username: str, email: str):
    # Create a unique random string suffix (e.g., "abc123")
    unique_suffix = uuid.uuid4().hex[:6]
    
    # Split the email to insert the unique suffix (e.g., filter_start_abc123@example.com)
    email_parts = email.split("@")
    unique_email = f"{email_parts[0]}_{unique_suffix}@{email_parts[1]}"
    unique_username = f"{username}_{unique_suffix}"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": unique_username,
            "email": unique_email,
            "password": "password123",
        },
    )

    assert register_response.status_code == 201
    
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_email,
            "password": "password123",
        },
    )

    assert login_response.status_code == 200
    return login_response.json()["access_token"]



def test_user_cannot_access_another_users_expense(client):
    user_a_token = register_and_login(
        client,
        "expense_user_a",
        "expense_user_a@example.com",
    )

    user_b_token = register_and_login(
        client,
        "expense_user_b",
        "expense_user_b@example.com",
    )

    # User A creates an expense
    create_response = client.post(
        "/api/v1/expenses",
        headers={
            "Authorization": f"Bearer {user_a_token}",
        },
        json={
            "date": "2026-09-06",
            "amount": 500,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "User A expense",
        },
    )

    assert create_response.status_code == 201
    expense_id = create_response.json()["id"]

    # User A can access their own expense
    own_response = client.get(
        f"/api/v1/expenses/{expense_id}",
        headers={
            "Authorization": f"Bearer {user_a_token}",
        },
    )

    assert own_response.status_code == 200

    # User B cannot access User A's expense
    other_user_response = client.get(
        f"/api/v1/expenses/{expense_id}",
        headers={
            "Authorization": f"Bearer {user_b_token}",
        },
    )

    assert other_user_response.status_code == 404


def test_expenses_filter_by_start_date(client):
    token = register_and_login(
        client,
        "filter_start_user",
        "filter_start@example.com",
    )

    headers = {
        "Authorization": f"Bearer {token}",
    }

    client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "date": "2026-09-01",
            "amount": 100,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "Old expense",
        },
    )

    client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "date": "2026-09-05",
            "amount": 200,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "Recent expense",
        },
    )

    response = client.get(
        "/api/v1/expenses?start_date=2026-09-05",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["date"] == "2026-09-05"


def test_expenses_filter_by_end_date(client):
    token = register_and_login(
        client,
        "filter_end_user",
        "filter_end@example.com",
    )

    headers = {
        "Authorization": f"Bearer {token}",
    }

    client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "date": "2026-09-01",
            "amount": 100,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "Early expense",
        },
    )

    client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "date": "2026-09-10",
            "amount": 200,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "Later expense",
        },
    )

    response = client.get(
        "/api/v1/expenses?end_date=2026-09-05",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["date"] == "2026-09-01"


def test_expenses_filter_by_category(client):
    token = register_and_login(
        client,
        "filter_category_user",
        "filter_category@example.com",
    )

    headers = {
        "Authorization": f"Bearer {token}",
    }

    client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "date": "2026-09-01",
            "amount": 100,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "Food expense",
        },
    )

    client.post(
        "/api/v1/expenses",
        headers=headers,
        json={
            "date": "2026-09-02",
            "amount": 200,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "Travel expense",
        },
    )

    response = client.get(
        "/api/v1/expenses?category=Food",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"


def test_expenses_combined_filters(client):
    token = register_and_login(
        client,
        "filter_combined_user",
        "filter_combined@example.com",
    )

    headers = {
        "Authorization": f"Bearer {token}",
    }

    expenses = [
        {
            "date": "2026-09-01",
            "amount": 100,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "Before range",
        },
        {
            "date": "2026-09-03",
            "amount": 200,
            "category": "Food",
            "subcategory": "Dinner",
            "note": "Matching expense",
        },
        {
            "date": "2026-09-04",
            "amount": 300,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "Wrong category",
        },
        {
            "date": "2026-09-07",
            "amount": 400,
            "category": "Food",
            "subcategory": "Dinner",
            "note": "After range",
        },
    ]

    for expense in expenses:
        response = client.post(
            "/api/v1/expenses",
            headers=headers,
            json=expense,
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/expenses"
        "?start_date=2026-09-02"
        "&end_date=2026-09-06"
        "&category=Food",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["date"] == "2026-09-03"
    assert data[0]["category"] == "Food"


