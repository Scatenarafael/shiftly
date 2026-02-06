import pytest


@pytest.mark.asyncio
async def test_register_user_success(client):
    payload = {
        "first_name": "A",
        "last_name": "B",
        "email": "a@b.com",
        "password": "secret",
        "active": True,
    }

    res = await client.post("/users/register", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "a@b.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_user_conflict(client):
    payload = {
        "first_name": "A",
        "last_name": "B",
        "email": "conflict@b.com",
        "password": "secret",
        "active": True,
    }

    res1 = await client.post("/users/register", json=payload)
    assert res1.status_code == 201

    res2 = await client.post("/users/register", json=payload)
    assert res2.status_code == 409
