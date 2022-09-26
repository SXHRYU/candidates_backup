from db import (
    TABLE_CANDIDATES,
    reconnect_on_failure,
)
from .types import T_connection


@reconnect_on_failure
def get_all_candidates(*, conn: T_connection) -> list[tuple] | None:
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {TABLE_CANDIDATES};")
        result = cur.fetchall()
        return [i[0] for i in result]

@reconnect_on_failure
def add_candidate_to_db(telegram_username: str,
                        candidate_username: str,
                        candidate_password: str,
                        *, conn: T_connection) -> str | None:

    with conn.cursor() as cur:
        cur.execute(f"INSERT INTO {TABLE_CANDIDATES}\
                        VALUES (\
                            '{telegram_username}', \
                            '{candidate_username}', \
                            '{candidate_password}' \
                        );")
        conn.commit()
        return telegram_username

@reconnect_on_failure
def delete_candidate_from_db(candidate_username: str,
                             *, conn: T_connection) -> str | None:
    username = candidate_username
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {TABLE_CANDIDATES}\
                        WHERE {username=};")
        conn.commit()
        return candidate_username

@reconnect_on_failure
def remember_username_password(candidate_username: str,
                               *, conn: T_connection) -> dict[str, str]:
    username = candidate_username
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {TABLE_CANDIDATES}\
                        WHERE {username=};")
        _result = cur.fetchone() 
        result = {"username": _result[1],
                  "password": _result[2]}
        return result

def error_raised(candidate: str) -> bool:
    if not candidate:
        return True
    else:
        return False
