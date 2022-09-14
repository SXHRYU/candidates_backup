import requests

from action_logs import log
from connection import establish_connection, get_user
from config.env import API_TOKEN, REGISTER_URL, USERS_LIST_URL

from .types import T_payload


def register_account(**data: T_payload) -> requests.Response:
    """Registers generated accounts in the database.
    
    Parameters
    ----------
    **data : dict[str, str, str, list[str | None]]
        In base case: `username=`, `password1=`, 
        `password2=`, `confirmations=`.

    Returns
    -------
    response : requests.Response
        Response from the API. If success, 201.

    Notes
    -----
    Accounts don't have any role by default.
    """
    return requests.post(REGISTER_URL, data=data)

@log
def delete_account(**data: dict[str, str]) -> requests.Response:
    session = establish_connection()

    user = get_user(session, **data)
    user_id = user["id"]

    session.delete(
        f"{USERS_LIST_URL}/{user_id}",
        headers={
            "Authorization": f"Token {API_TOKEN}",
        }
    )
    return user["username"]

def patch_role(role: list[str] = ["worker"],
               **data: dict[str, str]) -> requests.Response:
    """PATCHes to generated account a role of 'worker'.

    Because generated accounts don't have any role by default,
    we need to assign them some roles. Because generated
    annotators require only 1 role ('worker'), we PATCH it to them.

    Parameters
    ----------
    role : str
        Role that'll be PATCHed to the user. By default - 'worker',
        but can be many, e.g. ['worker', 'user', 'admin']
    **data : dict[str, str]
        In base case: `username=`, `password=`

    Returns
    -------
    server_response : requests.Response
        Can be used to check if the request was a success or not.
    """
    session = establish_connection()

    user = get_user(session, **data)
    user_id = user["id"]

    return session.patch(
        
        f"{USERS_LIST_URL}/{user_id}",
        data={
            "groups": role,
        },
        headers={
            "Authorization": f"Token {API_TOKEN}",
        },
    )
