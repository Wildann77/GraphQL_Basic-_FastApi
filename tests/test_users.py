import pytest
from httpx import AsyncClient

from src.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_user(client):
    query = """
    mutation {
        createUser(input: {name: "Test User", email: "test@example.com"}) {
            ... on User {
                id
                name
                email
            }
            ... on ValidationError {
                message
            }
        }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]["createUser"]
    assert data["name"] == "Test User"
    assert "id" in data
