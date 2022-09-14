from aiogram import types
from config.env import HR_USERS


def auth(func):
    """Authorises HR.
    
    See also
    --------
    config.HR_users
        A list of telegram IDs that are allowed to interract with
        whitelist.
    """
    async def wrapper(message: types.Message):
        if message.from_id not in HR_USERS:
            await message.reply("Разрешено только HR.")
        else:
            return await func(message)
    return wrapper
