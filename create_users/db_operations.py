from db import (
    TABLE_CANDIDATES,
    reconnect_on_failure,
)
from .types import T_connection


@reconnect_on_failure
def get_all_candidates(*, conn: T_connection) -> list[str | None]:
    """Returns normalised list of all candidates from database.

    Parameters
    ----------
    conn : psycopg2.connection
        Connection object with info about connection to db.
        Must be passed as a keyword-argument.

    Returns
    -------
    candidates : list[str | None]
        List of candidates (telegram usernames) from db.
        If no candidates present, returns `[]`.
    
    Raises
    ------
    OperationalError, InternalError, InterfaceError
        In case connection to database goes down, one of these
        is raised.

    Notes
    -----
    Catches disconnection errors and tries to reconnect.

    See also
    --------
    `reconnect_on_failure()`
    """
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {TABLE_CANDIDATES};")
        result = cur.fetchall()
        return [i[0] for i in result]

@reconnect_on_failure
def add_candidate_to_db(telegram_username: str,
                        candidate_username: str,
                        candidate_password: str,
                        *, conn: T_connection) -> str:
    """INSERTs candidate's data into database.

    Parameters
    ----------
    telegram_username : str
        Candidate's telegram username.
    candidate_username : str
        Candidate's generated username that
        will be used to create an account on
        candidates.trainingdata.solutions.
    candidate_password : str
        Candidate's generated password that
        will be used to create an account on
        candidates.trainingdata.solutions.
        It is stored UNENCRYPTED.
    conn : psycopg2.connection
        Connection object with info about connection to db.
        Must be passed as a keyword-argument.
    
    Returns
    -------
    telegram_username : str
        Telegram username of an added to db candidate.

    Raises
    ------
    OperationalError, InternalError, InterfaceError
        In case connection to database goes down, one of these
        is raised.

    Notes
    -----
    Executes DML INSERT query.
    Catches disconnection errors and tries to reconnect.

    See also
    --------
    `reconnect_on_failure()`
    """
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
def delete_candidate_from_db(telegram_username: str,
                             *, conn: T_connection) -> str:
    """DELETEs candidate's data from database.

    Parameters
    ----------
    telegram_username : str
        Candidate's telegram username.
    conn : psycopg2.connection
        Connection object with info about connection to db.
        Must be passed as a keyword-argument.
    
    Returns
    -------
    telegram_username : str
        Telegram username of a deleted from db candidate.

    Raises
    ------
    OperationalError, InternalError, InterfaceError
        In case connection to database goes down, one of these
        is raised.

    Notes
    -----
    Executes DML DELETE query.
    Catches disconnection errors and tries to reconnect.

    See also
    --------
    `reconnect_on_failure()`
    """
    username = telegram_username
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {TABLE_CANDIDATES}\
                        WHERE {username=};")
        conn.commit()
        return telegram_username

@reconnect_on_failure
def remember_username_password(telegram_username: str,
                               *, conn: T_connection) -> dict[str, str]:
    """Fetches username and password of a candidate.

    Parameters
    ----------
    telegram_username : str
        Candidate's telegram username.
    conn : psycopg2.connection
        Connection object with info about connection to db.
        Must be passed as a keyword-argument.
    
    Returns
    -------
    account_data : dict[str, str]
        Dictionary of candidate's account data, e.g.
        {"username": "SXRu1_test_Annotator", "wsDBjui87"}

    Raises
    ------
    OperationalError, InternalError, InterfaceError
        In case connection to database goes down, one of these
        is raised.

    Notes
    -----
    Catches disconnection errors and tries to reconnect.

    See also
    --------
    `reconnect_on_failure()`
    """
    username = telegram_username
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {TABLE_CANDIDATES}\
                        WHERE {username=};")
        _result = cur.fetchone() 
        result = {"username": _result[1],
                  "password": _result[2]}
        return result

def error_raised(candidate: str) -> bool:
    """Redundant function that used to check for `None`.

    It was used when the results of any of the above queries
    could return `None`. It should be deleted from here and
    from `to_handlers.py` eventually.
    TODO
    """
    if not candidate:
        return True
    else:
        return False
