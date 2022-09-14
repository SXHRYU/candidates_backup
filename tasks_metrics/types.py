from datetime import datetime, timedelta
from typing import Any


T_user = dict[str, str | int | bool | list[str | None]]
T_task = dict[str, str | int | bool | list[str | None]]
T_metrics = dict[str, int | float | datetime]
T_annotation = dict[str, str | int | bool | list[float | Any]]
