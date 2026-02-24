from uuid import uuid4

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/auth/me", None),
        ("GET", "/users", None),
        ("GET", "/users/00000000-0000-0000-0000-000000000001", None),
        ("GET", "/companies", None),
        ("POST", "/companies/create", {"name": "Company"}),
        ("GET", "/roles", None),
        ("POST", "/roles/create", {"name": "Role", "company_id": "00000000-0000-0000-0000-000000000001"}),
        ("GET", f"/link/by-company/{uuid4()}", None),
        ("GET", "/workdays", None),
        ("POST", "/workdays", {"date": "2026-01-01", "user_id": "00000000-0000-0000-0000-000000000001", "role_id": "00000000-0000-0000-0000-000000000001"}),
    ],
)
async def test_protected_routes_require_access_token(client, method: str, path: str, payload: dict | None):
    response = await client.request(method, path, json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Access token not found"
