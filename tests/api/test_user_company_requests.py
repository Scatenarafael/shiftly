import pytest


async def _register_user(
    client,
    *,
    first_name: str = "A",
    last_name: str = "B",
    email: str,
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


async def _login_user(client, *, email: str, password: str = "secret"):
    response = await client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response


@pytest.mark.asyncio
async def test_user_company_request_approve_flow(client):
    owner_email = "owner-request@b.com"
    requester_email = "requester@b.com"

    owner_res = await _register_user(client, email=owner_email)
    assert owner_res.status_code == 201
    await _login_user(client, email=owner_email)

    company_res = await client.post("/companies/create", json={"name": "Company Request Flow"})
    assert company_res.status_code == 201
    company_id = company_res.json()["id"]

    requester_res = await _register_user(client, email=requester_email)
    assert requester_res.status_code == 201
    await _login_user(client, email=requester_email)

    request_res = await client.post("/company-requests", json={"company_id": company_id})
    assert request_res.status_code == 201
    request_id = request_res.json()["id"]
    assert request_res.json()["status"] == "pending"

    await _login_user(client, email=owner_email)
    approve_res = await client.patch(f"/company-requests/{request_id}/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"


@pytest.mark.asyncio
async def test_approve_request_forbidden_for_non_owner(client):
    owner_email = "owner-nonowner@b.com"
    requester_email = "requester-nonowner@b.com"
    intruder_email = "intruder@b.com"

    owner_res = await _register_user(client, email=owner_email)
    assert owner_res.status_code == 201
    await _login_user(client, email=owner_email)

    company_res = await client.post("/companies/create", json={"name": "Company Non Owner"})
    assert company_res.status_code == 201
    company_id = company_res.json()["id"]

    requester_res = await _register_user(client, email=requester_email)
    assert requester_res.status_code == 201
    await _login_user(client, email=requester_email)

    request_res = await client.post("/company-requests", json={"company_id": company_id})
    assert request_res.status_code == 201
    request_id = request_res.json()["id"]

    intruder_res = await _register_user(client, email=intruder_email)
    assert intruder_res.status_code == 201
    await _login_user(client, email=intruder_email)

    approve_res = await client.patch(f"/company-requests/{request_id}/approve")
    assert approve_res.status_code == 403
