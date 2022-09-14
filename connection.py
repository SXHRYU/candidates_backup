import requests

from config.env import (
    TASKS_URL,
    USERNAME,
    PASSWORD,
    API_TOKEN,
    USERS_LIST_URL,
)


def get_session() -> requests.Session:
    """Returns session instance with authorized credentials.
    
    Authorizes bot via API using given credentials.
    Credentials are given either as global or environmental variables.

    Returns
    -------
    session : requests.Session
        Session that is used to connect to trainingdata API as admin.
    
    See also
    --------
    establish_connection()
        Driver function to use in other modules and packages to
        have a one-liner interface with `connection.py` module.
    """
    session = requests.Session()
    session.auth = (USERNAME, PASSWORD)

    return session

def get_page_size(session: requests.Session,
                  url: str) -> int:
    """Returns the number of all users.
    
    Desired param in `get_users` and `get_tasks` API query.
    """
    response = session.get(url)
    page_size = response.json()["count"]

    return page_size

def get_users(session: requests.Session) -> list[dict]:
    """Returns a list of users from the JSON response from
    corresponding API call.
    """
    response = session.get(
        USERS_LIST_URL,
        params={
            "page_size": get_page_size(session, USERS_LIST_URL),
        },
        headers={
            "Authorization": f"Token {API_TOKEN}",
        }
    )
    return response.json()["results"]

def get_user(
    session: requests.Session,
    **kwargs: dict[str, str]) -> dict[str,
                                      str | int | bool | list[str | None]]:
    """Returns user by specified parameter.
    
    Connects to server via API endpoint and returns either a user or
    raises an IndexError in case user not found.

    Parameters
    ----------
    session : requests.Session
        Session that is used to connect to trainingdata API as admin.
    users_list_url : str
        URL of API endpoint through which to get user from the server.
    **kwargs : dict[str, str]
        Either `username=` or `first_name=` or `last_name=`.
        These are the filters which are available for searching the db.

    Returns
    -------
    user : {str: str | int | bool | list[str | None]}
        Full information about the user fetched from the database.
        Includes his URL, id, username, first name, last name,
        groups, staff status, date joined, etc.

    Raises
    ------
    IndexError
        In case the user was not found.
    """
    if kwargs.get("username") or kwargs.get("first_name") or kwargs.get("last_name"):
        response = session.get(
            USERS_LIST_URL,
            params={
                "search": list(kwargs.values())[0]
            },
            headers={
                "Authorization": f"Token {API_TOKEN}"
            }
        )
    return response.json()["results"][0]

def get_tasks(session: requests.Session) -> list[dict]:
    response = session.get(
        TASKS_URL,
        params={
            "page_size": get_page_size(session, TASKS_URL),
        },
        headers={
            "Authorization": f"Token {API_TOKEN}",
        }
    )
    return response.json()["results"]

def get_user_tasks(
    session: requests.Session,
    **kwargs: dict[str, str]) -> dict[str,
                                      str | int | bool | list[str | None]]:
    if kwargs.get("owner") or kwargs.get("assignee") or kwargs.get("name"):
        response = session.get(
            TASKS_URL,
            params={
                "search": list(kwargs.values())[0]
            },
            headers={
                "Authorization": f"Token {API_TOKEN}"
            }
        )
    return response.json()["results"]

def get_task_annotations(session: requests.Session,
            task_id: int) -> dict[str, str | int | bool | list[str | None]]:
    response = session.get(
        f"{TASKS_URL}/{task_id}/annotations",
        headers={
            "Authorization": f"Token {API_TOKEN}"
        }
    )
    return response.json()["shapes"]

def establish_connection() -> requests.Session:
    """Driver function to export to other modules/packages.
    
    See also
    --------
    get_session()
    """
    session = get_session()

    return session
