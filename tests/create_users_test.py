import pytest
import psycopg2
# from create_users.db_operations import get_all_candidates


@pytest.fixture
def db_conn():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="test_db",
        user="test_user",
        password="test_password",
    )

@pytest.fixture
def fake_transaction():
    b = "lolka"
    yield b
    print(b)
    b = "success"
    print(b)

def test_get_all_candidates(db_conn, fake_transaction):
    print(db_conn)
    print('something done')
    assert fake_transaction == "lolka"
    