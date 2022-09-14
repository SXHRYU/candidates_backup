from .generation import (
    generate_task,
    generate_images,
    combine_task_and_images,
)
from .getters import (
    _get_task,
    _get_task_id,
    _get_user,
    _get_user_id,
    _get_user_username
)
from .types import T_images, T_response, T_task, T_user

def task_generated(telegram_username: str) -> bool:
    assignee: T_user = _get_user(telegram_username)
    assignee_id: int = _get_user_id(assignee)
    assignee_username: str = _get_user_username(assignee)
    
    generate_task(assignee_username, assignee_id)
    task: T_task = _get_task(assignee_username)
    task_id: int = _get_task_id(task)
    
    images: T_images = generate_images()
    result: T_response = combine_task_and_images(task_id, images)
    
    # I didn't put `.startswith("2")`
    # just in case in future this request returns 3xx.
    success = not (str(result.status_code).startswith("4") 
                    or str(result.status_code).startswith("5"))
    return success
