import pytest
from unittest.mock import patch
from web_interface_service import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("web_interface_service.requests.post")
def test_full_workflow(mock_post, client):

    mock_post.return_value.json.side_effect = [
        {"success": True, "encrypted": "test_encrypted"},
        {"success": True, "id": 1}                           
    ]
    enc_response = client.post("/encrypt", json={"user_input": "abc"})
    assert enc_response.status_code == 200
    enc_data = enc_response.get_json()
    assert enc_data["success"] is True
    assert "id" in enc_data

    mock_post.return_value.json.side_effect = [{"success": True, "decrypted": "abc"}]
    dec_response = client.post("/decode", json={"encrypted_string": "test_encrypted"})
    assert dec_response.status_code == 200
    dec_data = dec_response.get_json()
    assert dec_data["success"] is True
    assert dec_data["decrypted"] == "abc"
