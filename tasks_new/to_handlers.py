from tasks_generator.generation import (
    combine_task_and_images,
    generate_images,
    generate_task
)
from tasks_generator.getters import (
    _get_task,
    _get_task_id,
    _get_user,
    _get_user_id,
    _get_user_username
)
from tasks_generator.types import T_images, T_response, T_task, T_user


"""Module with driver functions to export to handlers.

Same as `tasks_generator.to_handlers` but with `times_attempted=2`
in some places.
"""

def new_task_generated(telegram_username: str) -> bool:
    """Used to generate new task once it is requested.
    
    See also
    --------
    `tasks_generator.to_handlers.task_generated()`
    """
    assignee: T_user = _get_user(telegram_username)
    assignee_id: int = _get_user_id(assignee)
    assignee_username: str = _get_user_username(assignee)

    generate_task(assignee_username, assignee_id, times_attempted=2)
    task: T_task = _get_task(assignee_username)
    task_id: int = _get_task_id(task)

    images: T_images = generate_images(times_attempted=2)
    result: T_response = combine_task_and_images(task_id, images)

    success = not (str(result.status_code).startswith("4") 
                    or str(result.status_code).startswith("5"))
    return success
