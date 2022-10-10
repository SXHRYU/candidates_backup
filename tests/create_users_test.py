from os import environ, getenv
import pytest
import psycopg2

if getenv("CI"):
    ...
else:
    environ["ADMIN_ID"] = "1"
    environ["PLATE_VALUES"] = ""
    environ["ROOT_DIR"] = ""
    environ["ALL_RESULTS_EXCEL_DIR"] = ""
    environ["USER_IMAGES_DIR"] = ""

@pytest.fixture
def db_conn(monkeypatch):
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_NAME", "test_db")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("DB_HOST", "localhost")

    DB_PORT = getenv("DB_PORT")
    DB_NAME = getenv("DB_NAME")
    DB_USER = getenv("DB_USER")
    DB_PASSWORD = getenv("DB_PASSWORD")
    DB_HOST = getenv("DB_HOST")
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )

@pytest.fixture
def fake_transaction(db_conn, monkeypatch):
    monkeypatch.setenv("CANDIDATES", "candidates")
    TABLE_CANDIDATES = getenv("CANDIDATES")
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
        db_conn.commit()
        yield
        cur.execute(f"DROP TABLE {TABLE_CANDIDATES};")
        db_conn.commit()

def test_get_all_candidates(db_conn, fake_transaction):
    from create_users.db_operations import get_all_candidates

    fake_transaction
    unwrapped_get_all_candidates = get_all_candidates.__wrapped__
    result = ['1', '2', '3']
    if getenv("CI"):
        result = ["2222"]
    assert unwrapped_get_all_candidates(conn=db_conn) == result
