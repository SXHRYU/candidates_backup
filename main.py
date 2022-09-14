from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot_files.handlers import FSM_handlers, general_handlers
from config.env import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Registers all the handlers defined in bot_files package.
FSM_handlers.register_FSM_handlers(dp)
general_handlers.register_general_handlers(dp)

async def on_startup(_):
    """Prints to stdout when the bot has started, passing by the logs.
    """
    return print("Bot started.")

async def on_shutdown(_):
    """Prints to stdout when the bot has stopped, passing by the logs.
    """
    return print("Bot stopped.")

if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
