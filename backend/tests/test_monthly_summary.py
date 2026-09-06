def register_and_login(client, username: str, email: str):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "password123",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "password123",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def create_expense(client, token: str, expense: dict):
    response = client.post(
        "/api/v1/expenses",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json=expense,
    )

    assert response.status_code == 201
    return response.json()


def test_monthly_summary_requires_authentication(client):
    response = client.get(
        "/api/v1/expenses/monthly-summary"
        "?year=2026&month=9"
    )

    assert response.status_code == 401


def test_monthly_summary(client):
    token = register_and_login(
        client,
        "monthly_summary_user",
        "monthly_summary@example.com",
    )

    create_expense(
        client,
        token,
        {
            "date": "2026-09-01",
            "amount": 100,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "September expense",
        },
    )

    create_expense(
        client,
        token,
        {
            "date": "2026-09-15",
            "amount": 200,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "September expense",
        },
    )

    create_expense(
        client,
        token,
        {
            "date": "2026-08-31",
            "amount": 500,
            "category": "Food",
            "subcategory": "Dinner",
            "note": "August expense",
        },
    )

    create_expense(
        client,
        token,
        {
            "date": "2026-10-01",
            "amount": 700,
            "category": "Food",
            "subcategory": "Dinner",
            "note": "October expense",
        },
    )

    response = client.get(
        "/api/v1/expenses/monthly-summary"
        "?year=2026&month=9",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["year"] == 2026
    assert data["month"] == 9
    assert data["total_expenses"] == 300
    assert data["total_transactions"] == 2


def test_monthly_summary_only_returns_current_users_expenses(client):
    user_a_token = register_and_login(
        client,
        "monthly_user_a",
        "monthly_user_a@example.com",
    )

    user_b_token = register_and_login(
        client,
        "monthly_user_b",
        "monthly_user_b@example.com",
    )

    create_expense(
        client,
        user_a_token,
        {
            "date": "2026-09-10",
            "amount": 500,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "User A",
        },
    )

    create_expense(
        client,
        user_b_token,
        {
            "date": "2026-09-10",
            "amount": 1000,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "User B",
        },
    )

    response = client.get(
        "/api/v1/expenses/monthly-summary"
        "?year=2026&month=9",
        headers={
            "Authorization": f"Bearer {user_a_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_expenses"] == 500
    assert data["total_transactions"] == 1


def test_monthly_summary_rejects_invalid_month(client):
    token = register_and_login(
        client,
        "invalid_month_user",
        "invalid_month@example.com",
    )

    response = client.get(
        "/api/v1/expenses/monthly-summary"
        "?year=2026&month=13",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Month must be between 1 and 12"