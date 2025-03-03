import pytest
from unittest.mock import patch, MagicMock
from storage_service import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("storage_service.get_db_connection")
def test_store_retrieve(mock_db, client):

    mock_cursor = MagicMock()
    
    mock_db.return_value.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = [1]

    mock_cursor.fetchall.return_value = [(1, "test_encrypted")]

    client.post("/store", json={"encrypted_string": "test"})

    response = client.get("/retrieve")
    assert response.status_code == 200
    data = response.get_json()

    assert [tuple(entry) for entry in data["entries"]] == [(1, "test_encrypted")]

    mock_cursor.execute.assert_any_call(
        "INSERT INTO xor_table (xor_value) VALUES (%s) RETURNING id", ("test",)
    )
    mock_cursor.execute.assert_any_call(
        "SELECT id, xor_value FROM xor_table ORDER BY id DESC LIMIT 100"
    )
