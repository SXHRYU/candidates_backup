from io import TextIOWrapper
from requests import Response


T_images = list[tuple[str, tuple[str, TextIOWrapper, str]]]
T_user = dict[str, str | int | bool | list[str | None]]
T_task = dict[str, str | int | bool | list[str | None]]
T_response = Response
