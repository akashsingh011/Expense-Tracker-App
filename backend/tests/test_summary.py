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


def test_summary_requires_authentication(client):
    response = client.get("/api/v1/expenses/summary")

    assert response.status_code == 401


def test_expense_summary(client):
    token = register_and_login(
        client,
        "summary_user",
        "summary@example.com",
    )

    expenses = [
        {
            "date": "2026-09-01",
            "amount": 100,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "Lunch",
        },
        {
            "date": "2026-09-02",
            "amount": 200,
            "category": "Food",
            "subcategory": "Dinner",
            "note": "Dinner",
        },
        {
            "date": "2026-09-03",
            "amount": 300,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "Taxi",
        },
    ]

    for expense in expenses:
        create_expense(client, token, expense)

    response = client.get(
        "/api/v1/expenses/summary",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_expenses"] == 600
    assert data["total_transactions"] == 3

    assert data["by_category"]["Food"]["total"] == 300
    assert data["by_category"]["Food"]["transactions"] == 2

    assert data["by_category"]["Travel"]["total"] == 300
    assert data["by_category"]["Travel"]["transactions"] == 1

    assert data["by_subcategory"]["Lunch"]["total"] == 100
    assert data["by_subcategory"]["Dinner"]["total"] == 200
    assert data["by_subcategory"]["Taxi"]["total"] == 300


def test_expense_summary_with_date_filter(client):
    token = register_and_login(
        client,
        "summary_date_user",
        "summary_date@example.com",
    )

    expenses = [
        {
            "date": "2026-09-01",
            "amount": 100,
            "category": "Food",
            "subcategory": "Lunch",
            "note": "Before range",
        },
        {
            "date": "2026-09-05",
            "amount": 200,
            "category": "Food",
            "subcategory": "Dinner",
            "note": "Inside range",
        },
        {
            "date": "2026-09-10",
            "amount": 300,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "After range",
        },
    ]

    for expense in expenses:
        create_expense(client, token, expense)

    response = client.get(
        "/api/v1/expenses/summary"
        "?start_date=2026-09-02"
        "&end_date=2026-09-06",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_expenses"] == 200
    assert data["total_transactions"] == 1

    assert data["by_category"]["Food"]["total"] == 200
    assert data["by_category"]["Food"]["transactions"] == 1

    assert data["by_subcategory"]["Dinner"]["total"] == 200
    assert "Travel" not in data["by_category"]


def test_summary_only_returns_current_users_expenses(client):
    user_a_token = register_and_login(
        client,
        "summary_user_a",
        "summary_user_a@example.com",
    )

    user_b_token = register_and_login(
        client,
        "summary_user_b",
        "summary_user_b@example.com",
    )

    create_expense(
        client,
        user_a_token,
        {
            "date": "2026-09-01",
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
            "date": "2026-09-01",
            "amount": 1000,
            "category": "Travel",
            "subcategory": "Taxi",
            "note": "User B",
        },
    )

    response = client.get(
        "/api/v1/expenses/summary",
        headers={
            "Authorization": f"Bearer {user_a_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_expenses"] == 500
    assert data["total_transactions"] == 1

    assert "Food" in data["by_category"]
    assert "Travel" not in data["by_category"]