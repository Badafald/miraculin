import pytest
from encryption_service import encrypt_string, decrypt_string

def test_encrypt_string():
    expected = "YWJjbWlyYWN1bGlu"
    assert encrypt_string("abc") == expected

def test_decrypt_string():
    encrypted = "YWJjbWlyYWN1bGlu"
    assert decrypt_string(encrypted) == "abc"
