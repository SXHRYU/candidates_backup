from action_logs import log
from .types import T_payload
from db import db_conn
from .db_operations import (
    add_candidate_to_db,
    error_raised,
    get_all_candidates,
    delete_candidate_from_db,
    remember_username_password,
)
from .generation import generate_account
from .registration import delete_account, patch_role, register_account


# WORKFLOW of the package:
## generation.py
### 1.1)Generate username;
### 1.2)Generete password;
### 1.3)Generate account payload.
## registration.py
### 2.1)Register user;
## to_handlers.py
### 3.1.1)If registered successfully, continue;
### 3.1.2)If registration failed, return error message;
### 3.2)Add user to database of registered candidates;
### 3.2.1)If database operation was a success, 
###         return (username, password);
### 3.2.2)If database operation was a failure,
###         return error message and delete from server;
### 3.3)If all checks passed, PATCH a "worker" role to account;
### 3.4)Send credentials to candidate.

@log
def get_user_credentials(telegram_username: str) -> T_payload | str:
    """Returns user's credentials or sends an error message.

    Because the result of `generate_accounts()` in success scenario
    is a tuple of (username, password) we check result's `isinstance()`.
    If not tuple, send an error message. This is a driver function to
    export to handlers.

    Parameters
    ----------
    telegram_username : str
        Telegram login/username of candidate that requested account.
        Is used to generate account.

    Returns
    -------
    created_account : T_payload
        Returns on success of registration.
    error_message : str
        Returns on failure of registration.
    
    See also
    --------
    generate_account()
    
    Notes
    -----
    This function uses `generate_account()` function that is logged,
    in case of failure, the error message in that function is logged,
    not the message here.
    """
    ERROR_MESSAGE_REGISTRATION = ("Произошла ошибка при регистрации!\n"
                        + "Свяжитесь с HR или попробуйте зарегистрироваться"
                        + "через другой аккаунт.")
    ERROR_MESSAGE_DB = ("Произошла ошибка с нашей стороны!\n"
                        + "Свяжитесь с HR или попробуйте зарегистрироваться"
                        + "через другой аккаунт.")

    account_data = generate_account(telegram_username)
    account_username = account_data["username"]
    account_password = account_data["password1"]

    register_result = register_account(**account_data)
    

    if not str(register_result.status_code).startswith("2"):
        delete_account(username=telegram_username)
        return ERROR_MESSAGE_REGISTRATION
    else:
        new_candidate = add_candidate_to_db(telegram_username,
                                            account_username,
                                            account_password,
                                            conn=db_conn)
        if error_raised(new_candidate):
            delete_candidate_from_db(telegram_username, conn=db_conn)
            delete_account(username=telegram_username)
            return ERROR_MESSAGE_DB
        else:
            patch_role(username=telegram_username)
            return account_data
