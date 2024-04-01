import asyncio
import os
from aiogram import Bot, Dispatcher
# from dotenv import find_dotenv, load_dotenv
# load_dotenv(find_dotenv())

from handlers.user_private import user_private_router
from settings.config import TOKEN


ALLOWED_UPDATES = ["message, edited_message"]

bot = Bot(token=TOKEN)
dp = Dispatcher()

dp.include_router(user_private_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())
