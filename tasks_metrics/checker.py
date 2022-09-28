from .types import T_annotation


def check_all_images(task_annotations: T_annotation,
                     total_shapes: int = 10) -> bool:
    """Checks that all images are done by an account.


    Parameters
    ----------
    task_annotations : T_annotations
        Actual annotations that were made by an account.
    total_shapes : int
        Total number of annotations that need to be done.
    
    Returns
    -------
    all_images_done : bool
        `True` if all images done, `False` otherwise.
    """
    # 1 shape == 1 label on 1 image,
    # total = 2 labels * 5 images = 10 shapes.
    return len(task_annotations) == total_shapes

def check_only_polygons(task_annotations: T_annotation,
                        type_: str = "polygon") -> bool:
    """Checks that images are annotated only using "polygon" figure.

    Parameters
    ----------
    task_annotations : T_annotations
        Actual annotations that were made by an account.
    type_ : str
        Type of annotation shape to check against.
        (Other options can be fetched from the site)
    
    Returns
    -------
    only_polygon : bool
        `True` if only "polygon" used, `False` otherwise.
    """
    # Checks so everything's annotated only using "POLYGON".
    return all([i["type"]==type_ for i in task_annotations])

def check_plates_points(task_annotations: T_annotation,
                        label_id: int,
                        total_points: int = 8) -> bool:
    """Checks that all plates are annotated using 4 points.

    Part of a test assignment is to also annotate plates
    but using only 4 points of a 'polygon'.

    Parameters
    ----------
    task_annotations : T_annotations
        Actual annotations that were made by an account.
    label_id : int
        ID of a "plates" label.
    total_points : int
        Total number of points that need to be done on 1 plate.

    Returns
    -------
    4_points : bool
        `True` if plates are annotated using 4 points of a 'polygon',
        `False` otherwise.
    """
    # Checks that plates are annotated using only 4 points.
    # len((x1, y1); (x2, y2); (x3, y3); (x4, y4)) == 8
    return all(
        [len(i["points"])==total_points for i in task_annotations if i["label_id"] == label_id]
    )

def check_plates_values(task_annotations: T_annotation,
                        label_id: int) -> bool:
    """Checks that all plates' values are annotated.

    Part of a test assignment is to also annotate plates` values,
    e.g. '623BITNY' or '123UwU321'

    Parameters
    ----------
    task_annotations : T_annotations
        Actual annotations that were made by an account.
    label_id : int
        ID of a "plates" label.

    Returns
    -------
    all_values_done : bool
        `True` if there are no empty plates' values, `False` otherwise.
    """
    # Checks that all plates' values are annotated.
    plates = [i for i in task_annotations if i["label_id"] == label_id]
    empty_values = 0
    for plate in plates:
        if plate["attributes"][0]["value"] == "":
            empty_values += 1
            break
    return not empty_values
