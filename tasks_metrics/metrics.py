from datetime import date, datetime
from typing import Iterable

from db import TABLE_METRICS, reconnect_on_failure
from config.env import PLATE_VALUES
from .types import T_metrics, T_task


"""`README.md`, sec. "Metrics`" ("Метрики")."""

def _avg(_iterable: Iterable) -> float:
    return sum(_iterable) / len(_iterable)

def _transform_to_datetime(date_string: str) -> datetime:
    """Normalises different datetimes and turns them into `datetime`
    objects.

    Needed in case time output from the site changes in the future.

    Parameters
    ----------
    date_string : str
        Datetime presented in `str` format.
    
    Returns
    -------
    datetime : datetime.datetime
        Datetime presented in `datetime.datetime` format.
    """
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
    """Returns average IoU of all car images.
    
    Parameters
    ----------
    car_iou : list[float]
        List of individual car IoU's.

    Returns
    -------
    avg_car_iou : float
        Average car IoU across all user inputs.
    """
    return _avg(car_iou)

def get_plate_IoU_average(plate_iou: list[float]) -> float:
    """Returns average IoU of all car images.
    
    Parameters
    ----------
    plate_iou : list[float]
        List of individual plate IoU's.

    Returns
    -------
    avg_plate_iou : float
        Average plate IoU across all user inputs.
    """
    return _avg(plate_iou)

def get_plate_accuracy(candidate_plate_values: list[str]) -> float:
    """Returns average plates` values` annotation accuracy.
    
    Individual plate accuracy is a binary value, either
    'ENTIRELY correct' or 'wrong', e.g.:

        ground_truth: ('BITNY427', '123OwO321', 'Yy298bm')
        user_input: ('BITNY427', '123OWO321', 'Yу298bm')
        
        Result = 1/3:
            * 2nd had uppercase 'W' but original had lowercase;
            * 3rd had Russian 'у' instead of English 'y'.
        Which means no matter how close or similar the results are,
        even if 1 letter is off by a capitalisation, the result will be
        'wrong'.
    
    Parameters
    ----------
    candidate_plate_values : list[str]
        Plates' values' annotations from user input.
    
    Returns
    -------
    avg_values_accuracy : float
        Average plates' values' accuracy across all user inputs.
    """
    original_plate_values = PLATE_VALUES

    plates_correct = 0
    for plate_value in candidate_plate_values:
        if plate_value in original_plate_values:
            plates_correct += 1
    
    avg_plate_accuracy = plates_correct / len(candidate_plate_values) * 100
    return round(avg_plate_accuracy, 2)

def get_task_start_time(task: T_task) -> datetime:
    """Returns date of task generation.

    Parameters
    ----------
    task : T_task
        Task that was assigned to the account.
    
    Returns
    -------
    created_date : datetime.datetime
        Date of task creation (when user requested a task)
    """
    created_date = task["created_date"]
    created_date = _transform_to_datetime(created_date) 
    return created_date

def get_task_end_time(task: T_task) -> datetime:
    """Returns date of task completion (when user informed the bot).

    Parameters
    ----------
    task : T_task
        Task that was assigned to the account.
    
    Returns
    -------
    updated_date : datetime.datetime
        Last date of task updation (when user last edited a task).
    """
    updated_date = task["updated_date"]
    updated_date = _transform_to_datetime(updated_date)
    return updated_date

@reconnect_on_failure
def update_metrics(candidate_username: str, metrics: T_metrics, *, conn) -> None:
    """Updates `metrics` table in database with new metrics.

    Parameters
    ----------
    candidate_username : str
        Username of a candidate
        that informed the bot of task completion.
    metrics : T_metrics
        All the user metrics (iou, accuracy, dates).
    conn : psycopg2.connection
        Connection object with info about connection to db.
        Must be passed as a keyword-argument.

    Returns
    -------
    None

    Notes
    -----
    Executes SQL UPDATE query.

    See also
    --------
    `reconnect_on_failure()`
    """
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
def get_all_metrics(*, conn) -> list[tuple[T_metrics]]:
    """Returns all users' metrics 
    from the `metrics` table of the database.

    Parameters
    ----------
    conn : psycopg2.connection
        Connection object with info about connection to db.
        Must be passed as a keyword-argument.

    Returns
    -------
    all_metrics : list[tuple[T_metrics]]
        ALL metrics of ALL users from the `metrics` table.

    See also
    --------
    `reconnect_on_failure()`
    """
    with conn.cursor() as cur:
        results = []
        cur.execute(f"SELECT * FROM {TABLE_METRICS};")
        
        cur_results = list(map(list, cur.fetchall()))
        for row in cur_results:
            time_started_row = row[4]
            time_ended_row = row[5]
            try:
                row[6] = str(time_ended_row - time_started_row).replace(":", "--")
            except TypeError:
                row[6] = "В процессе"

        results.append([i.name for i in cur.description])
        results.append(cur_results)
        return results

@reconnect_on_failure
def get_candidate_metrics(candidate_username: str, *, conn) -> T_metrics:
    """Returns metrics of a specified user
    from the `metrics` table of the database.

    Parameters
    ----------
    candidate_username : str
        Telegram username of a candidate, whose metrics to return.
    
    Returns
    -------
    metrics : T_metrics
        ALL metrics of INDIVIDUAL candidate from the `metrics` table.

    See also
    --------
    `reconnect_on_failure()`
    """
    with conn.cursor() as cur:
        results = []
        cur.execute(f"SELECT * FROM {TABLE_METRICS}\
                        WHERE {candidate_username=};")
        results.append([i.name for i in cur.description])
        results.append(cur.fetchall())
        return results

@reconnect_on_failure
def update_times_attempted(candidate_username: str,
                           *, conn,
                           times_attempted) -> int:
    """Updates `metrics` table in database with new metrics.

    Parameters
    ----------
    candidate_username : str
        Username of a candidate
        that informed the bot of task completion.
    conn : psycopg2.connection
        Connection object with info about connection to db.
        Must be passed as a keyword-argument.
    times_attempted : int
        Updated number of times the candidate has requested a task.

    Returns
    -------
    times_attempted : int
        Updated number of times the candidate has requested a task.

    Notes
    -----
    Executes SQL UPDATE query.

    See also
    --------
    `reconnect_on_failure()`
    """
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {TABLE_METRICS} SET\
                        {times_attempted=}\
                        WHERE {candidate_username=}")
        conn.commit()
        return times_attempted
