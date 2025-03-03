import pytest
from unittest.mock import patch, MagicMock
from storage_service import get_db_connection

@patch.dict("os.environ", {
    "DB_NAME": "test_db",
    "DB_USERNAME": "test_user",
    "DB_PASSWORD": "test_pass",
    "DB_HOST": "localhost",
    "DB_PORT": "5432"
})
@patch("storage_service.psycopg2.connect")
def test_db_connection(mock_connect):
    mock_connect.return_value = MagicMock()
    conn = get_db_connection()
    assert conn is not None
    mock_connect.assert_called_once_with(
        dbname="test_db",
        user="test_user",
        password="test_pass",
        host="localhost",
        port="5432"
    )
