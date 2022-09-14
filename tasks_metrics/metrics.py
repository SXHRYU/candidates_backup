from datetime import date, datetime
from typing import Iterable

from db import TABLE_METRICS, reconnect_on_failure
from config.env import PLATE_VALUES
from .types import T_metrics, T_task


def _avg(_iterable: Iterable) -> float:
    return sum(_iterable) / len(_iterable)

def _transform_to_datetime(date_string: str) -> datetime:
    # Needed because of different possible date fields.
    popular_formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ", # -> "2022-08-11T21:09:01.123456Z"
        "%Y-%m-%dT%H:%M:%SZ", # -> "2018-03-12T10:12:45Z"
        "%b %d %Y at %I:%M%p", # -> "Jun 28 2018 at 7:40AM"
        "%B %d, %Y, %H:%M:%S",  # -> "September 18, 2017, 22:19:55"
        "%a,%d/%m/%y,%I:%M%p", # -> "Sun,05/12/99,12:30PM"
        "%a, %d %B, %Y", # -> "Mon, 21 March, 2015"
    ]
    for format_ in popular_formats:
        try:
            datetime_obj: datetime = datetime.strptime(date_string, format_)
        except ValueError:
            continue
        else:
            break
    return datetime_obj

def get_car_IoU_average(car_iou: list[float]) -> float:
    return _avg(car_iou)

def get_plate_IoU_average(plate_iou: list[float]) -> float:
    return _avg(plate_iou)

def get_plate_accuracy(candidate_plate_values: list[str]) -> float:
    original_plate_values = PLATE_VALUES

    plates_correct = 0
    for plate_value in candidate_plate_values:
        if plate_value in original_plate_values:
            plates_correct += 1
    
    avg_plate_accuracy = plates_correct / len(candidate_plate_values) * 100
    return round(avg_plate_accuracy, 2)

def get_task_start_time(task: T_task) -> datetime:
    created_date = task["created_date"]
    created_date = _transform_to_datetime(created_date) 
    return created_date

def get_task_end_time(task: T_task) -> datetime:
    updated_date = task["updated_date"]
    updated_date = _transform_to_datetime(updated_date)
    return updated_date

@reconnect_on_failure
def update_metrics(candidate_username: str, metrics: T_metrics, *, conn) -> None:
    car_iou: float = metrics["car_iou"]
    plate_iou: float = metrics["plate_iou"]
    plate_accuracy: float = metrics["plate_accuracy"]
    task_started: date = str(metrics["task_started"])
    task_ended: date = str(metrics["task_ended"])
    times_attempted: int = metrics["times_attempted"]

    with conn.cursor() as cur:
        cur.execute(f"UPDATE {TABLE_METRICS} SET\
                        {car_iou=},\
                        {plate_iou=},\
                        {plate_accuracy=},\
                        {task_started=}::timestamp(0),\
                        {task_ended=}::timestamp(0),\
                        {times_attempted=}\
                            WHERE {candidate_username=}")
        conn.commit()

@reconnect_on_failure
def get_all_metrics(*, conn):
    with conn.cursor() as cur:
        results = []
        cur.execute(f"SELECT * FROM {TABLE_METRICS};")
        
        cur_results = list(map(list, cur.fetchall()))
        for row in cur_results:
            time_started_row = row[4]
            time_ended_row = row[5]
            row[6] = str(time_ended_row - time_started_row).replace(":", "--")

        results.append([i.name for i in cur.description])
        results.append(cur_results)
        return results

@reconnect_on_failure
def get_candidate_metrics(candidate_username: str, *, conn) -> T_metrics:
    with conn.cursor() as cur:
        results = []
        cur.execute(f"SELECT * FROM {TABLE_METRICS}\
                        WHERE candidate_username = '{candidate_username}';")
        results.append([i.name for i in cur.description])
        results.append(cur.fetchall())
        return results

@reconnect_on_failure
def update_times_attempted(candidate_username: str,
                           *, conn,
                           times_attempted) -> int:
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {TABLE_METRICS} SET\
                        {times_attempted=}\
                        WHERE {candidate_username=}")
        conn.commit()
        return times_attempted
