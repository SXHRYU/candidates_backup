from aiogram import types
from bot_files import keyboards as kb
from db import TABLE_TRAININGDATA_WHITELIST, db_conn, reconnect_on_failure


@reconnect_on_failure
def get_whitelist(*, conn) -> tuple[str]:
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {TABLE_TRAININGDATA_WHITELIST}")
        result = cur.fetchall()
    return [i[0] for i in result]

def auth(func):
    """Authorises HR.
    
    See also
    --------
    config.HR_users
        A list of telegram IDs that are allowed to interract with
        whitelist.
    """
    async def wrapper(message: types.Message):
        whitelist = get_whitelist(conn=db_conn)
        if message.from_user.username not in whitelist:
            await message.reply(
                "Меню",
                reply_markup=kb.menu_kb
            )
        else:
            return await func(message)
    return wrapper
