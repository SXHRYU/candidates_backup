# import hashlib
import secrets
import string

from action_logs import log
from .types import T_payload

def generate_username(telegram_username: str) -> str:
    """Returns username in specified format.
    
    The format is <prefix>_test_Annotator,
    where the <prefix> is candidate's telegram username.

    Parameters
    ----------
    telegram_username : str
        Telegram login/username of candidate that requested account.
        Will be used as a prefix to the generated username.

    Returns
    -------
    username : str
        Username that will be used to register to CVAT.

    See also
    --------
    generate_password()
    generate_accounts()
    """
    prefix = telegram_username
    annotator = "Annotator"

    return f"{prefix}_test_{annotator}"

def generate_password() -> str:
    """Returns 10-character alphanumeric password.
    
    Returns
    -------
    password : str
        Alphanumeric password generated using `secrets`
        module of Python. `secrets` is to be considered
        superior in safety than Python's `random` module.

    See also
    --------
    generate_username()
    generate_accounts()

    WARNING
    -------
    Generated passwords are logged in system unencrypted.
    """
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(10))

    return password

# Not needed (for now).
"""def hash_password(password: str) -> str:
    return hashlib.sha256(bytes(password, encoding="utf-8")).hexdigest()"""

@log
def generate_account(telegram_username: str) -> T_payload:
    """Creates account's payload to send to register_user() function.

    Parameters
    ----------
    telegram_username : str
        Telegram login/username of candidate that requested account.

    Returns
    -------
    created_account : tuple[str, str]
        (username, password).
        Usernames are generated with the specific format:
        <telegram_username>_test_Annotator

    See also
    --------
    generate_username()
    generate_password()
    register_account()
    
    Notes
    -----
    This function is logged.
    """
    username = generate_username(telegram_username)
    password = generate_password()

    data = {
        "username": username,
        "password1": password,
        "password2": password,
        "confirmations": [],
    }

    return data
