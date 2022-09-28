import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
from config.env import USER_IMAGES_DIR


def generate_image_name(object: str,
                        image_number: int,
                        account_username: str) -> str:
    """Generates image name.

    Parameters
    ----------
    object : str
        'car' or 'plate'
    image_number : int
        1-10
    account_username:
        Username of the account that submitted results.
    
    Returns
    -------
    image_name : str
        Image name that will be used for generated image.
        e.g.
        'car/car1_SXRu1_test_Annotator.png'
        'plate/plate7_gvanrossum_test_Annotator.png'
    """
    return f"{object}/{object}{image_number}_{account_username}.png"

def generate_image(image_name: str, account_username: str,
                   *, polygon: list[int]) -> None:
    """Generates individual image from user input.

    Parameters
    ----------
    image_name : str
    account_username : str
        Username of the account that submitted results.
    polygon : list[int]
        User input from the site.
        Will be used to generate mask and image.

    Returns
    -------
    None but generates and saves image to specified directory.

    See also
    --------
    `generate_image_name()`
        How an image's name is generated.
    `generate_car_plate_imageset()`
        If `generate_image()` is used to generate individual image,
        this function generates a batch of images and uses
        `generate_image()` as a main dependency.
    """
    # os.mkdir(USER_IMAGES_DIR / candidate_username )
    # https://stackoverflow.com/a/3732128/17601156

    img = Image.new('1', (1920, 1080), 0)
    ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
    img.save(USER_IMAGES_DIR / account_username / image_name)

def generate_car_plate_imageset(account_username: str,
                                car_points_list: list[list[int]],
                                plate_points_list: list[list[int]],
                                times_attempted: int) -> None:
    """Generates a batch of images* from user input.

    *both car and plate images

    Parameters
    ----------
    account_username : str
        Username of the account that submitted results.
    car_points_list : list[list[int]]
        A list of user input of the cars from the site.
        Will be used to generate mask and image.
    plate_points_list : list[list[int]]
        A list of user input of the plates from the site.
        Will be used to generate mask and image.
    times_attempted : int
        Number of times the candidate has requested a task.
        Will be used to make a name for an image.

    Returns
    -------
    None but generates and saves all images.

    See also
    --------
    `generate_image()`
        How image generation works.
    """
    if times_attempted == 1:
        start = 1
    else:
        start = 6
        shutil.rmtree(USER_IMAGES_DIR / account_username)
    try:
        os.makedirs(USER_IMAGES_DIR / account_username / "car")
    except FileExistsError:
        ...
    try:
        os.makedirs(USER_IMAGES_DIR / account_username / "plate")
    except FileExistsError:
        ...
    for index, (car_points, plate_points) in enumerate(
                                                zip(car_points_list, 
                                                    plate_points_list),
                                                start=start):
        car_image_name = generate_image_name("car", index, account_username)
        car_image_polygon = car_points
        
        plate_image_name = generate_image_name("plate", index, account_username)
        plate_image_polygon = plate_points

        generate_image(car_image_name,
                       account_username, polygon=car_image_polygon)
        generate_image(plate_image_name,
                       account_username, polygon=plate_image_polygon)
    
def generate_path_to_images(account_username: str) -> Path:
    """Returns absolute path to images.

    e.g.
    'home/.../trainingdata_candidates/user_images/SXRu1_test_Annotator'
    'home/.../trainingdata_candidates/user_images/gvanrossum_test_Annotator'
    """
    # e.g. home/.../trainingdata_candidates/user_images/SXRu1_test_Annotator
    return USER_IMAGES_DIR / account_username

def generate_path_to_ground_truth() -> Path:
    """Returns absolute path to ground truth.

    e.g.
    'home/.../trainingdata_candidates/user_images/ground_truth'
    """
    return USER_IMAGES_DIR / "ground_truth" 
