from io import TextIOWrapper
from pathlib import Path

from connection import establish_connection
from config.env import ADMIN_ID, TASKS_URL, ORIGINAL_IMAGES_DIR
from .types import T_images, T_response


DEFAULT_LABELS = [
    {
        "name": "car",
        "color": "#fa3253",
        "attributes": []
    },
    {
        "name": "plate",
        "color":"#3d3df5",
        "attributes": [
            {
                "name": "plate",
                "mutable": False,
                "input_type": "text",
                "default_value": "",
                "values": [""]
            }
        ]
    }
]

def generate_task(
    assignee_username: str, # username исполнителя таска.
    assignee_id: int, # id исполнителя таска.
    owner_id: int = ADMIN_ID, # id создателя таска.
    overlap: int = 0, # Честно хз что это, но мне страшно это убирать.
    segment_size: int = 5, # Кол-во картинок на сегмент.
    image_quality: int = 100, # Сжатие.
    labels: list[dict[str, str]] = DEFAULT_LABELS, # То, что размечать.
    *,
    times_attempted: int = 1 # Номер попытки
    ) -> T_response:

    session = establish_connection()
    data = {
        "name": f"{times_attempted} Test Assignment {assignee_username}",
        "assignee_id": assignee_id,
        "owner_id": owner_id,
        "overlap": overlap,
        "segment_size": segment_size,
        "image_quality": image_quality,
        "labels": labels
    }

    return session.post(
        TASKS_URL,
        json=data,
    )

def generate_images(number: int = 5, *, times_attempted: int = 1) -> T_images:
    def read_image(path: str | Path) -> TextIOWrapper:
        return open(path, "rb")

    # path_to_original_images: Path = ORIGINAL_IMAGES_DIR.resolve()
    path_to_original_images: Path = Path(Path(__file__).parent.parent / "media" / "images").resolve()

    images = []
    for i in range(number):
        # ("client_files[1]", ("image1.png", read_image(.media/images/1.jpg), "image/png"))
        images.append(
            (
                f"client_files[{i+1}]",
                # f"server_files[{i+1}]",
                (
                    f"image{i+1}.png",
                    (read_image(path_to_original_images / f"{i+1}.jpg") 
                        if times_attempted == 1
                        else 
                            read_image(path_to_original_images / f"{i+6}.jpg")),
                    "image/png"
                )
            )
        )
    
    return images

def combine_task_and_images(task_id: int, images: T_images) -> T_response:
    session = establish_connection()

    data = {
        "image_quality": 100,
        "use_zip_chunks": False,
        "use_cache": False,
        "sorting_method": "natural",
        "storage": "local",
        "storage_method": "file_system",
    }

    return session.post(
        f"{TASKS_URL}/{task_id}/data",
        headers={"Upload-Start": "true",
                "Upload-Multiple": "true",
                "Upload-Finish": "true"},
        data=data,
        files=images
    )
