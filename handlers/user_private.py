from aiogram import types, Router
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode


user_private_router = Router()

user_last_submission = {}
users_started = set()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_started:
        users_started.add(user_id)
        await message.answer(
            f"Привет, {message.from_user.first_name}! \nДля начала внимательно изучите вкладки <b>Навигация</b> и <b>Инструкция</b>! \nЧтобы открыть меню, введите команду /menu.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(f"{message.from_user.first_name}, выберите опцию. \nЧтобы открыть меню, введите команду /menu.")


@user_private_router.message(Command("menu"))
async def menu_cmd(message: types.Message):
    await message.answer("Вот меню")

# @user_private_router.message(Command("active"))
# async def active_cmd(message: types.Message):
#     await message.answer("Актив")

# @user_private_router.message(Command("navigation"))
# async def active_cmd(message: types.Message):
#     await message.answer("Навигация")

# @user_private_router.message(Command("instruction"))
# async def instruction_cmd(message: types.Message):
#     await message.answer("Инструкция")

# @user_private_router.message(Command("rules"))
# async def rules_cmd(message: types.Message):
#     await message.answer("Правила")

# @user_private_router.message(Command("payment"))
# async def payment_cmd(message: types.Message):
#     await message.answer("Купить публикацию")


