import requests

BASE_URL = "http://localhost:5000"

def test_full_encryption_flow():
    # Call the encryption endpoint with live services
    response = requests.post(f"{BASE_URL}/encrypt", json={"user_input": "xyz"})
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    # The encryption service may return either an "encrypted" key or an "id" after storage.
    encrypted = data.get("encrypted") or data.get("id")
    assert encrypted is not None

    # Call the decryption endpoint with the encrypted string
    response = requests.post(f"{BASE_URL}/decode", json={"encrypted_string": encrypted})
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True
    # Expecting the decrypted value to match the original user input
    assert data.get("decrypted") == "xyz"
