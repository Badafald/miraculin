# tests/test_e2e_nodeport.py
import base64
import os
import time
import typing as t

import pytest
import requests

# NodePort web (main) — используем только его
MAIN_URL = os.getenv("MAIN_URL", "http://10.66.66.12:31234")
READY_TIMEOUT_S = int(os.getenv("READY_TIMEOUT_S", "60"))
REQ_TIMEOUT_S = int(os.getenv("REQ_TIMEOUT_S", "6"))


def wait_ready(url: str, path: str = "/ready", timeout_s: int = READY_TIMEOUT_S) -> None:
    deadline = time.time() + timeout_s
    last_exc: t.Optional[Exception] = None
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}{path}", timeout=REQ_TIMEOUT_S)
            if r.status_code == 200:
                return
        except Exception as e:
            last_exc = e
        time.sleep(0.5)
    if last_exc:
        raise AssertionError(f"Service not ready at {url}{path}: {last_exc}")
    raise AssertionError(f"Service not ready at {url}{path}: non-200 response")


@pytest.fixture(scope="session", autouse=True)
def ensure_web_ready():
    wait_ready(MAIN_URL)


def encrypt_locally(user_input: str) -> str:
    """Имитируем encryption-service: base64(user_input + 'miraculin')."""
    combined = (user_input + "miraculin").encode()
    return base64.b64encode(combined).decode()


def page_contains(text: str) -> bool:
    r = requests.get(f"{MAIN_URL}/", timeout=REQ_TIMEOUT_S)
    assert r.status_code == 200
    return text in r.text


def test_happy_path_via_web_only():
    # 1) Отправляем валидный ввод на /encrypt
    user_input = "abc"  # <= 3 символов — должно пройти
    r = requests.post(f"{MAIN_URL}/encrypt", json={"user_input": user_input}, timeout=REQ_TIMEOUT_S)
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload.get("success") is True, payload
    new_id = payload.get("id")
    assert isinstance(new_id, int) and new_id > 0

    # 2) Локально вычисляем encrypted_string (по фактической логике сервиса)
    encrypted_string = encrypt_locally(user_input)

    # 3) Проверяем, что зашифрованная строка попала на главную страницу (main рендерит entries из storage)
    assert page_contains(encrypted_string), "Ожидали увидеть encrypted_string на / после сохранения"

    # 4) Декодируем через основной веб
    r = requests.post(f"{MAIN_URL}/decode", json={"encrypted_string": encrypted_string}, timeout=REQ_TIMEOUT_S)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d.get("success") is True, d
    assert d.get("decrypted") == user_input

    # 5) Удаляем через основной веб
    r = requests.post(f"{MAIN_URL}/delete", json={"encrypted_string": encrypted_string}, timeout=REQ_TIMEOUT_S)
    assert r.status_code == 200, r.text
    del_payload = r.json()
    assert del_payload.get("success") is True, del_payload

    # 6) Проверяем, что на главной больше нет этой строки
    assert not page_contains(encrypted_string), "После удаления encrypted_string не должен отображаться на /"


def test_encrypt_too_long_input_returns_error_json():
    """Слишком длинный ввод: основной сервис возвращает 200, но в JSON — success: False."""
    too_long = "abcd"  # > 3
    r = requests.post(f"{MAIN_URL}/encrypt", json={"user_input": too_long}, timeout=REQ_TIMEOUT_S)
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload.get("success") is False
    assert "Input too long" in payload.get("error", "")
