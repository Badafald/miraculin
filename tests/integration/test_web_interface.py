import pytest
from unittest.mock import patch
from web_interface_service import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("web_interface_service.requests.get")
def test_index(mock_get, client):

    mock_get.return_value.json.return_value = {"entries": [[1, "encrypted1"], [2, "encrypted2"]]}
    response = client.get("/")
    assert response.status_code == 200

    assert b"encrypted1" in response.data
    assert b"encrypted2" in response.data
