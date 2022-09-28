from connection import (
    establish_connection,
    get_user_tasks,
    get_task_annotations,
    get_user,
)
from .types import T_annotation, T_task, T_user


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

def _get_user_username(user: T_user) -> str:
    return user["username"]

def _get_task(username: str) -> T_task:
    session = establish_connection()
    task = get_user_tasks(session, assignee=username)[0]
    return task

def _get_task_id(task: int) -> int:
    return task["id"]

def _get_task_labels(task: T_task) -> dict[str, int]:
    labels_name_id = {}
    for label in task["labels"]:
        labels_name_id[label["name"]] = label["id"]
    return labels_name_id


def _get_task_annotations(task_id: int) -> list[T_annotation]:
    session = establish_connection()
    annotations = get_task_annotations(session, task_id)
    return annotations

def _get_task_car_annotations(annotations: list[T_annotation],
                              car_label_id: int) -> list[T_annotation]:
    car_annotations = [i for i in annotations if i["label_id"] == car_label_id]
    return car_annotations

def _get_task_car_annotations_points(car_annotations: list[T_annotation]) -> list[list[int]]:
    return [i["points"] for i in car_annotations]

def _get_task_plate_annotations(annotations: list[T_annotation],
                                plate_label_id: int) -> list[list[int]]:
    plate_annotations = [i for i in annotations if i["label_id"] == plate_label_id]
    return plate_annotations

def _get_task_plate_annotations_points(plate_annotations: list[T_annotation]) -> list[list[int]]:
    return [i["points"] for i in plate_annotations]

def _get_task_plate_values(plate_annotations: list[T_annotation]) -> list[str]:
    plate_attributes = [i["attributes"] for i in plate_annotations]
    return [i[0]["value"] for i in plate_attributes]

def _get_times_attempted(username: str) -> int:
    session = establish_connection()
    
    tasks = get_user_tasks(session, assignee=username)
    times_attempted = len(tasks)
    return times_attempted
