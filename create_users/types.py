from psycopg2 import extensions


T_payload = dict[str | str, str, list[str | None]]
T_connection = extensions.connection
