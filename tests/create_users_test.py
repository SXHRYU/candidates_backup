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
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    conn.autocommit = True
    return conn

@pytest.fixture
def mock_table(monkeypatch):
    monkeypatch.setenv("CANDIDATES", "candidates")

@pytest.fixture
def fake_transaction(db_conn, mock_table):
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
        yield
        cur.execute(f"DROP TABLE {TABLE_CANDIDATES};")


@pytest.fixture
def fake_select(db_conn, mock_table):
    TABLE_CANDIDATES = getenv("CANDIDATES")
    def select():
        with db_conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {TABLE_CANDIDATES};")
            return cur.fetchall()
    return select

def test_get_all_candidates(db_conn, fake_transaction):
    from create_users.db_operations import get_all_candidates

    unwrapped_get_all_candidates = get_all_candidates.__wrapped__
    result = ['1', '2', '3']
    assert unwrapped_get_all_candidates(conn=db_conn) == result

def test_add_candidate_to_db(db_conn, fake_transaction, fake_select):
    from create_users.db_operations import add_candidate_to_db

    unwrapped_add_candidate_to_db = add_candidate_to_db.__wrapped__
    unwrapped_add_candidate_to_db(
        "tester",
        "tester-username",
        "tester-password",
        conn=db_conn
    )

    results = fake_select()
    assert results == [
        ('1', '1_username', '1_password'),
        ('2', '2_username', '2_password'),
        ('3', '3_username', '3_password'),
        ("tester", "tester-username", "tester-password")
    ]

def test_add_candidate_to_db_return(db_conn, fake_transaction):
    from create_users.db_operations import add_candidate_to_db

    unwrapped_add_candidate_to_db = add_candidate_to_db.__wrapped__
    added_candidate = unwrapped_add_candidate_to_db(
        "tester",
        "tester-username",
        "tester-password",
        conn=db_conn
    )

    assert added_candidate == "tester"

def test_delete_candidate_from_db(db_conn, fake_transaction, fake_select):
    from create_users.db_operations import delete_candidate_from_db

    unwrapped_delete_candidate_from_db = delete_candidate_from_db.__wrapped__
    unwrapped_delete_candidate_from_db(
        "2",
        conn=db_conn
    )

    results = fake_select()

    assert results == [
        ('1', '1_username', '1_password'),
        ('3', '3_username', '3_password'),
    ]

def test_delete_candidate_from_db_return(db_conn, fake_transaction):
    from create_users.db_operations import delete_candidate_from_db

    unwrapped_delete_candidate_from_db = delete_candidate_from_db.__wrapped__
    result = unwrapped_delete_candidate_from_db(
        "2",
        conn=db_conn
    )

    assert result == '2'

