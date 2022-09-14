import os
from pathlib import Path
from datetime import datetime

import pandas as pd

from db import db_conn
from config.env import ALL_RESULTS_EXCEL_DIR
from .checker import (
    check_all_images,
    check_only_polygons,
    check_plates_points,
    check_plates_values,
)
from .differences import get_difference
from .generation import (
    generate_car_plate_imageset,
    generate_path_to_ground_truth,
    generate_path_to_images
)
from .getters import (
    _get_user,
    _get_user_id,
    _get_user_username,
    _get_task,
    _get_task_id,
    _get_task_labels,
    _get_task_annotations,
    _get_task_car_annotations,
    _get_task_car_annotations_points,
    _get_task_plate_annotations,
    _get_task_plate_annotations_points,
    _get_task_plate_values,
    _get_times_attempted,
)
from .metrics import (
    get_car_IoU_average,
    get_plate_IoU_average,
    get_plate_accuracy,
    get_task_start_time,
    get_task_end_time,
    update_metrics,
    update_times_attempted,
    get_all_metrics,
    get_candidate_metrics,
)
from .types import T_annotation, T_task, T_user, T_metrics


def task_complete(telegram_username: str) -> bool | str:
    candidate: T_user = _get_user(telegram_username)
    candidate_username: str = _get_user_username(candidate)
    
    task: T_task = _get_task(candidate_username)
    task_id: int = _get_task_id(task)
    task_labels: dict[str, int] = _get_task_labels(task)
    task_annotations: list[T_annotation] = _get_task_annotations(task_id)

    all_images_done: bool = check_all_images(task_annotations)
    only_polygons: bool = check_only_polygons(task_annotations)
    _plate_label_id: int = task_labels["plate"]
    correct_plates: bool = check_plates_points(task_annotations, _plate_label_id)
    all_plates_done: bool = check_plates_values(task_annotations, _plate_label_id)

    error_message: str = ""
    if all_images_done and only_polygons and correct_plates and all_plates_done:
        return True
    elif not all_images_done:
        error_message = ("Не все разметки сделаны. "
            + "У вас должно быть размечено 5 машин и 5 номеров (с указанием букв и цифр).")
    elif not only_polygons or not correct_plates:
        error_message = ("Неправильно размечены номера машин. "
            + "Их нужно размечать только с помощью polygon, используя 4 точки.")
    elif not all_plates_done:
        error_message = "Не все значения номеров написаны."
    return error_message
        

def send_HR_metrics(telegram_username: str) -> None:
    candidate: T_user = _get_user(telegram_username)
    candidate_username: str = _get_user_username(candidate)
    times_attempted: int = _get_times_attempted(candidate_username)
    
    task: T_task = _get_task(candidate_username)
    task_id: int = _get_task_id(task)
    task_labels: dict[str, int] = _get_task_labels(task)
    task_annotations: list[T_annotation] = _get_task_annotations(task_id)

    _car_label_id: int = task_labels["car"]
    _car_annotations: list[T_annotation] = _get_task_car_annotations(task_annotations, _car_label_id)
    car_annotations_points: list[list[int]] = _get_task_car_annotations_points(_car_annotations)

    _plate_label_id: int = task_labels["plate"]
    _plate_annotations: list[T_annotation] = _get_task_plate_annotations(task_annotations, _plate_label_id)
    plate_annotations_points: list[list[int]] = _get_task_plate_annotations_points(_plate_annotations)
    plate_values: list[str] = _get_task_plate_values(_plate_annotations)

    generate_car_plate_imageset(candidate_username,
                                car_annotations_points,
                                plate_annotations_points,
                                times_attempted)

    path_to_car_images: Path = generate_path_to_images(candidate_username) / "car"
    path_to_car_ground_truth: Path = generate_path_to_ground_truth() / "car"
    path_to_plate_images: Path = generate_path_to_images(candidate_username) / "plate"
    path_to_plate_ground_truth: Path = generate_path_to_ground_truth() / "plate"

    car_images: list[str] = sorted(os.listdir(path_to_car_images))
    car_ground_truth: list[str] = sorted(os.listdir(path_to_car_ground_truth))
    # Sorted `car_ground_truth` = ["car10_.png", "car1_.png", "car2_.png",...].
    # Because such sort disrupts all the order-sensitive calculations,
    # we need to normalise the output by putting the "car10_.png"
    # to the end of the list.
    # Normalising sorted list:
    car_ground_truth.append(car_ground_truth.pop(0))
    
    plate_images: list[str] = sorted(os.listdir(path_to_plate_images))
    plate_ground_truth: list[str] = sorted(os.listdir(path_to_plate_ground_truth))
    # Same normalisation goes for the `plate_ground_truth`:
    plate_ground_truth.append(plate_ground_truth.pop(0))

    start =  0 if times_attempted == 1 else 5
    car_iou: list[float] = []
    for car_image, ground_truth in zip(car_images, car_ground_truth[start:]):
        car_path: str = str(path_to_car_images / car_image)
        ground_truth_path: str = str(path_to_car_ground_truth / ground_truth)
        car_diff: float = get_difference(car_path, ground_truth_path)
        car_iou.append(car_diff)
    
    plate_iou: list[float] = []
    for plate_image, ground_truth in zip(plate_images, plate_ground_truth[start:]):
        plate_path: str = str(path_to_plate_images / plate_image)
        ground_truth_path: str = str(path_to_plate_ground_truth / ground_truth)
        plate_diff: float = get_difference(plate_path, ground_truth_path)
        plate_iou.append(plate_diff)

    db_metrics: T_metrics = {
        "car_iou": get_car_IoU_average(car_iou),
        "plate_iou": get_plate_IoU_average(plate_iou),
        "plate_accuracy": get_plate_accuracy(plate_values),
        "task_started": get_task_start_time(task),
        "task_ended": get_task_end_time(task),
        "times_attempted": times_attempted,
    }
    
    # HR_metrics: T_metrics = {
    #     "Car IoU": db_metrics["car_iou"],
    #     "Plate IoU": db_metrics["plate_iou"],
    #     "Plate Accuracy": db_metrics["plate_accuracy"],
    #     "Task Start Time": db_metrics["task_started"],
    #     "Task End Time": db_metrics["task_ended"],
    #     "Task Completion Time": db_metrics["task_completed"],
    #     "Times Attempted": db_metrics["times_attempted"],
    # }

    update_metrics(telegram_username, db_metrics, conn=db_conn)

def generate_excel() -> tuple[str, str]:
    all_results = get_all_metrics(conn=db_conn)
    column_names = all_results[0]
    df = pd.DataFrame(*all_results[1:], columns=column_names)
    
    excel_file_name = f"{ALL_RESULTS_EXCEL_DIR}/{datetime.today().date()}.xlsx"
    df.to_excel(excel_file_name)
    actual_file_name_length = len(str(datetime.today().date())) + len(".xlsx")
    excel_output_name = excel_file_name[-actual_file_name_length:]

    return (excel_file_name, excel_output_name)

def get_candidate_formatted_results(telegram_username: str) -> str:
    results = get_candidate_metrics(telegram_username, conn=db_conn)
    formatted_results = ""
    for column_name, value in zip(results[0], *results[1]):
        formatted_results += f"{column_name}: {value}\n"
    return formatted_results

def get_candidate_results(telegram_username: str) -> T_metrics:
    _results = get_candidate_metrics(telegram_username, conn=db_conn)
    results = {}
    for column_name, value in zip(_results[0], *_results[1]):
        results[column_name] = value
    return results
