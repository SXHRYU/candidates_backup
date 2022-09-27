from io import TextIOWrapper
from pathlib import Path

from connection import establish_connection
from config.env import ADMIN_ID, TASKS_URL
from .types import T_images, T_response


DEFAULT_LABELS = [
    {
        "name": "car", # label name
        "color": "#fa3253", # color in gui
        "attributes": []
    },
    {
        "name": "plate",
        "color":"#3d3df5",
        "attributes": [
            {
                "name": "plate",
                "mutable": False,
                "input_type": "text", # Select/Radio/Checkbox/Text/Number
                "default_value": "",
                "values": [""]
            }
        ]
    }
]

def generate_task(
    assignee_username: str, # Username исполнителя таска.
    assignee_id: int, # ID исполнителя таска.
    owner_id: int = ADMIN_ID, # ID создателя таска.
    overlap: int = 0, # Честно хз что это, но мне страшно это убирать.
    segment_size: int = 5, # Кол-во картинок на сегмент.
    image_quality: int = 100, # Сжатие.
    labels: list[dict[str, str | list]] = DEFAULT_LABELS, # То, что размечать.
    *,
    times_attempted: int = 1 # Номер попытки
    ) -> T_response:
    """Initial request that POSTs an "empty" task.

    Parameters
    ----------
    assignee_username : str
        Account username to which this task will be assigned.
        Will be used to make a name for a task.
    assignee_id : str
        Account id to which this task will be assigned.
        Mandatory argument to successfully create a task through API.
    owner_id : int
        Admin ID (creator of a task).
        Mandatory argument to successfully create a task through API.
    overlap : int
        TODO: find out if this is a mandatory parameter.
        I actually don't know what it is, and at this point,
        I'm too afraid to ask. But I've set `overlap=0` and it works.
    segment_size : int
        Number of images per job.
        Mandatory argument to successfully create a task through API.
    image_quality : int
        Image quality in percents.
        App will lower the images' resolution if the value is < 100.
        Mandatory (?) argument to successfully create a task through API.
    labels : list[dict[str, str | list]]
        The very things that need to be annotated.
        Can be simply a dict of key-value pairs, if no special
        attributes are needed, or you can some attributes
        as specified on the site.
        Mandatory argument to successfully create a task through API.
    times_attempted : int
        Number of times the candidate has requested a task.
        Will be used to make a name for a task.
    
    Returns
    -------
    response : requests.Response
        Response from the API. If success, 201.
    
    See also
    --------
    README, sec. "How Tasks are Created" ("Как создаются таски")
    """
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

    # I've experimented w/ `json=data` and `data=data`
    # and found that `json=data` was correct.
    return session.post(
        TASKS_URL,
        json=data,
    )

def generate_images(number: int = 5, *, times_attempted: int = 1) -> T_images:
    """Generates image payload for a POST request.

    This function only generates the list of required format.
    It doesn't POST the data to the API. The function
    `combine_task_and_images()` does that.

    Parameters
    ----------
    number : int
        Number of images to read and to add in a payload.
    times_attempted : int
        Number of times the candidate has requested a task.
        Will be used to read different images.

    Returns
    -------
    image_payload : list[tuple[str, tuple[str, TextIOWrapper, str]]]
        i.e. (times_attempted=1):
        [
            ("client_files[1]", <IMAGE 1 IN BINARY FORMAT>, "image/png")),
            ("client_files[2]", <IMAGE 2 IN BINARY FORMAT>, "image/png")),
                                        ...
            ("client_files[5]", <IMAGE 5 IN BINARY FORMAT>, "image/png")),
        ]
        i.e. (times_attempted=2):
        [
            ("client_files[1]", <IMAGE 6 IN BINARY FORMAT>, "image/png")),
            ("client_files[2]", <IMAGE 7 IN BINARY FORMAT>, "image/png")),
                                        ...
            ("client_files[5]", <IMAGE 10 IN BINARY FORMAT>, "image/png")),
        ]

    See also
    --------
    `combine_task_and_images()`
    """
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
    """POSTs image payload data to a task (can be any task).

    Reads image payload data acquired from `generate_images()`
    and POSTs it through the API to a given task,
    effectively making a task 'complete' and ready to be undertaken.

    Parameters
    ----------
    task_id : int
        ID of an "empty" task that will get the images.
    images : image_payload

    Returns
    -------
    response : requests.Response
        Response from the API. If success, 203.
        NOTE: if the upload failed, task isn't combined with images,
        but the API still returns 203. To check if the request was
        ACTUALLY a success, a JSON with a key "data" must be received.
        This "data" is a numerical value of image directory
        on a server.

    See also
    --------
    `generate_images()`
    """
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
        headers={"Upload-Start": "true",   # I don't know if these headers are actually needed,
                "Upload-Multiple": "true", # but they were listed in some examples I found online
                "Upload-Finish": "true"},  # and given in the corresponding API end-point through Swagger.
        # Same with `data=data` and `files=images` as in `generate_task()`.
        data=data,
        files=images
    )
