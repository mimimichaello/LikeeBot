from aiogram import types, Router
from aiogram.filters import CommandStart


user_private_router = Router()

user_last_submission = {}
users_started = set()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_started:
        users_started.add(user_id)
        await message.answer(
            f"Привет, {message.from_user.first_name}! Для начала внимательно изучи вкладки Навигация и Инструкция!"
        )
    else:
        await message.answer(f"{message.from_user.first_name}, выберите опцию")


@user_private_router.message()
async def answer(message: types.Message):
    await message.answer("Ответ")
