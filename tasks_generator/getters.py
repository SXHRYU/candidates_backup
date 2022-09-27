from connection import establish_connection, get_user_tasks, get_user
from .types import T_task, T_user


"""`README.md`, sec. "Why Use `getters`" ("Зачем нужны getters").

Helper functions that offer entry-point for `connection` module,
provide better isolation, higher cohesion and lower coupling.
"""

def _get_user(username: str) -> T_user:
    session = establish_connection()
    user = get_user(session, username=username)
    return user

def _get_user_id(user: T_user) -> int:
    return user["id"]

def _get_user_username(user: T_user) -> int:
    return user["username"]


def _get_task(username: str) -> T_task:
    session = establish_connection()
    task = get_user_tasks(session, assignee=username)[0]
    return task

def _get_task_id(task) -> int:
    return task["id"]
