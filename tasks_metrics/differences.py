import numpy
import cv2


def get_difference(path_to_image1: str, path_to_image2: str) -> float:
    img1 = cv2.imread(path_to_image1, 0)
    img2 = cv2.imread(path_to_image2, 0) # Ground Truth.
    
    # https://stackoverflow.com/a/65904093/17601156
    intersection = numpy.logical_and(img1, img2)
    union = numpy.logical_or(img1, img2)
    iou_score = numpy.sum(intersection) / numpy.sum(union) * 100

    return round(iou_score, 2)
