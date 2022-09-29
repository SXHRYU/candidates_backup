import pytest
import psycopg2
from create_users.db_operations import get_all_candidates


TABLE_CANDIDATES = "candidates"

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
def fake_transaction(db_conn):
    with db_conn.cursor() as cur:
        cur.execute(f"CREATE TABLE {TABLE_CANDIDATES} \
                        (username varchar(255), \
                         candidate_username varchar(255), \
                         candidate_password varchar(255));")
        cur.execute(f"INSERT INTO {TABLE_CANDIDATES} \
                        VALUES ('1', '1_username', '1_password');")
        cur.execute(f"INSERT INTO {TABLE_CANDIDATES} \
                        VALUES ('2', '2_username', '2_password');")
        cur.execute(f"INSERT INTO {TABLE_CANDIDATES} \
                        VALUES ('3', '3_username', '3_password');")
        
        yield
        cur.execute(f"DELETE FROM {TABLE_CANDIDATES};")

def test_get_all_candidates(db_conn, fake_transaction):
    fake_transaction
    unwrapped_get_all_candidates = get_all_candidates.__wrapped__
    result = [
        ('1', '1_username', '1_password'),
        ('2', '2_username', '2_password'),
        ('3', '3_username', '3_password')
    ]
    assert unwrapped_get_all_candidates(db_conn) == result
    