from .types import T_annotation


def check_all_images(task_annotations: T_annotation,
                     total_shapes: int = 10) -> bool:
    # 1 shape == 1 label on 1 image,
    # total = 2 labels * 5 images = 10 shapes.
    return len(task_annotations) == total_shapes

def check_only_polygons(task_annotations: T_annotation,
                        type_: str = "polygon") -> bool:
    # Checks so everything's annotated only using "POLYGON".
    return all([i["type"]==type_ for i in task_annotations])

def check_plates_points(task_annotations: T_annotation,
                        label_id: int,
                        total_points: int = 8) -> bool:
    # Checks that plates are annotated using only 4 points.
    # len((x1, y1); (x2, y2); (x3, y3); (x4, y4)) == 8
    return all(
        [len(i["points"])==total_points for i in task_annotations if i["label_id"] == label_id]
    )

def check_plates_values(task_annotations: T_annotation,
                        label_id: int,
                        total_shapes: int = 10) -> bool:
    # Checks that all plates' values are annotated.
    plates = [i for i in task_annotations if i["label_id"] == label_id]
    empty_values = 0
    for plate in plates:
        if plate["attributes"][0]["value"] == "":
            empty_values += 1
    return not empty_values
