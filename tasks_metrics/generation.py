import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
from config.env import USER_IMAGES_DIR


def generate_image_name(object: str,
                        image_number: int,
                        candidate_username: str) -> str:
    return f"{object}/{object}{image_number}_{candidate_username}.png"

def generate_image(image_name: str, candidate_username: str,
                   *, polygon: list[int]) -> None:
    # os.mkdir(USER_IMAGES_DIR / candidate_username )
    # https://stackoverflow.com/a/3732128/17601156

    img = Image.new('1', (1920, 1080), 0)
    ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
    img.save(USER_IMAGES_DIR / candidate_username / image_name)

def generate_car_plate_imageset(candidate_username: str,
                                car_points_list: list[list[int]],
                                plate_points_list: list[list[int]],
                                times_attempted: int) -> None:
    if times_attempted == 1:
        start = 1
    else:
        start = 6
        shutil.rmtree(USER_IMAGES_DIR / candidate_username)
    try:
        os.makedirs(USER_IMAGES_DIR / candidate_username / "car")
    except FileExistsError:
        ...
    try:
        os.makedirs(USER_IMAGES_DIR / candidate_username / "plate")
    except FileExistsError:
        ...
    for index, (car_points, plate_points) in enumerate(
                                                zip(car_points_list, 
                                                    plate_points_list),
                                                start=start):
        car_image_name = generate_image_name("car", index, candidate_username)
        car_image_polygon = car_points
        
        plate_image_name = generate_image_name("plate", index, candidate_username)
        plate_image_polygon = plate_points

        generate_image(car_image_name,
                       candidate_username, polygon=car_image_polygon)
        generate_image(plate_image_name,
                       candidate_username, polygon=plate_image_polygon)
    
def generate_path_to_images(candidate_username: str) -> Path:
    # e.g. home/.../trainingdata_candidates/user_images/SXRu1
    return USER_IMAGES_DIR / candidate_username

def generate_path_to_ground_truth() -> Path:
    return USER_IMAGES_DIR / "ground_truth" 
