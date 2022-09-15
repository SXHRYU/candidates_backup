from functools import wraps
import time
import psycopg2
from psycopg2 import OperationalError, InternalError, InterfaceError

from config.env import (
    # Database schemas are present in bot architecture picture.
    CANDIDATES,
    METRICS,
    TRAININGDATA_WHITELIST,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)

TABLE_CANDIDATES = CANDIDATES
TABLE_METRICS = METRICS
TABLE_TRAININGDATA_WHITELIST = TRAININGDATA_WHITELIST

# # Should protect from "SSL SYSCALL error: EOF detected".
# # https://stackoverflow.com/a/63130830/17601156
# keepalive_kwargs = {
#     "keepalives": 1,
#     "keepalives_idle": 30,
#     "keepalives_interval": 5,
#     "keepalives_count": 5,
# }

db_conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    # **keepalive_kwargs,
)

db_retries: int = 5
db_sleep_secs: int = 1
def reconnect_on_failure(function_with_db_operation):
    @wraps(function_with_db_operation)
    def wrapper(*args, conn, **kwargs):
        for _ in range(db_retries):
            try:
                return function_with_db_operation(*args, conn=db_conn, **kwargs)
            except (OperationalError, InternalError, InterfaceError):
                try:
                    new_conn = psycopg2.connect(
                        host=DB_HOST,
                        port=DB_PORT,
                        dbname=DB_NAME,
                        user=DB_USER,
                        password=DB_PASSWORD,
                    )
                    return function_with_db_operation(*args, conn=new_conn, **kwargs)
                except (OperationalError, InternalError, InterfaceError):
                    time.sleep(db_sleep_secs)
                    continue
    return wrapper
