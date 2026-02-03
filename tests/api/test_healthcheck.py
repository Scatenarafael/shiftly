import pytest


@pytest.mark.asyncio
async def test_healthcheck(client):
    res = await client.get("/health")
    assert res.status_code == 200
