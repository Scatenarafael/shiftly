from uuid import uuid4

import pytest

from src.infra.security import create_access_token
from src.infra.settings.config import get_settings


async def _register_user(
    client,
    *,
    first_name: str = "A",
    last_name: str = "B",
    email: str = "a@b.com",
    password: str = "secret",
    active: bool = True,
):
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "active": active,
    }
    response = await client.post("/users/register", json=payload)
    return response


async def _login_user(client, *, email: str, password: str):
    login_response = await client.post("/auth/login", json={"email": email, "password": password})
    assert login_response.status_code == 200
    return login_response


def _authenticate_client_with_access_cookie(client, user_id: str):
    settings = get_settings()
    access_token = create_access_token(user_id)
    client.cookies.set(settings.ACCESS_COOKIE_NAME, access_token)


@pytest.mark.asyncio
async def test_register_user_success(client):
    res = await _register_user(client, email="a@b.com")
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "a@b.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_user_conflict(client):
    res1 = await _register_user(client, email="conflict@b.com")
    assert res1.status_code == 201

    res2 = await _register_user(client, email="conflict@b.com")
    assert res2.status_code == 409


@pytest.mark.asyncio
async def test_register_user_validation_error(client):
    res = await client.post(
        "/users/register",
        json={"first_name": "A", "last_name": "B", "password": "secret", "active": True},
    )

    assert res.status_code == 422


@pytest.mark.asyncio
async def test_list_users_requires_auth(client):
    res = await client.get("/users")
    assert res.status_code == 401
    assert res.json()["detail"] == "Access token not found"


@pytest.mark.asyncio
async def test_list_users_success(client):
    await _register_user(client, email="list@b.com")
    await _login_user(client, email="list@b.com", password="secret")

    res = await client.get("/users")
    assert res.status_code == 200
    users = res.json()
    assert any(user["email"] == "list@b.com" for user in users)


@pytest.mark.asyncio
async def test_retrieve_user_not_found(client):
    await _register_user(client, email="retrieve@b.com")
    await _login_user(client, email="retrieve@b.com", password="secret")

    res = await client.get(f"/users/{uuid4()}")
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_update_user_success(client):
    create_res = await _register_user(client, email="update@b.com")
    user_id = create_res.json()["id"]
    await _login_user(client, email="update@b.com", password="secret")

    res = await client.patch(f"/users/{user_id}", json={"first_name": "Updated"})
    assert res.status_code == 200
    assert res.json()["first_name"] == "Updated"


@pytest.mark.asyncio
async def test_update_user_not_found(client):
    await _register_user(client, email="update-not-found@b.com")
    await _login_user(client, email="update-not-found@b.com", password="secret")

    res = await client.patch(f"/users/{uuid4()}", json={"first_name": "Updated"})
    assert res.status_code == 404
    assert res.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_delete_user_success(client):
    create_res = await _register_user(client, email="delete@b.com")
    user_id = create_res.json()["id"]
    _authenticate_client_with_access_cookie(client, user_id)

    delete_res = await client.delete(f"/users/{user_id}")
    assert delete_res.status_code == 204

    retrieve_res = await client.get(f"/users/{user_id}")
    assert retrieve_res.status_code == 404
