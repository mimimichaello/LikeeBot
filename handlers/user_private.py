from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from filters.chat_types import ChatTypeFilter


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

user_last_submission = {}
users_started = set()


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_started:
        users_started.add(user_id)
        await message.answer(
            f"Привет, {message.from_user.username}! \nДля начала внимательно изучите вкладки <b>Навигация</b> и <b>Инструкция</b>! \nЧтобы открыть меню, введите команду /menu.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer(
            f"{message.from_user.username}, выберите опцию. \nЧтобы открыть меню, введите команду /menu."
        )


@user_private_router.message(Command("menu"))
async def menu_cmd(message: types.Message):
    await message.answer("Вот меню")


@user_private_router.message(F.text)
async def active_cmd(message: types.Message):
    await message.answer(
        "Вы отправили неккоректное сообщение. Прочитайте еще раз <b>Инструкцию</b>, или откройте <b>Меню</b> с помощью /menu и выберите нужную команду.",
        parse_mode=ParseMode.HTML,
    )


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
