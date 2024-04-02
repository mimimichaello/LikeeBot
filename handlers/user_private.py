from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.enums import ParseMode
from filters.chat_types import ChatTypeFilter
from keyboards import get_keyboard, utils_reply


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
            reply_markup=utils_reply.start_menu()
        )
    else:
        await message.answer(
            f"{message.from_user.username}, выберите опцию. \nЧтобы открыть меню, введите команду /menu.",
            reply_markup=utils_reply.start_menu()
        )


@user_private_router.message(Command("menu"))
async def menu_cmd(message: types.Message):
    await message.answer("Меню", reply_markup=utils_reply.start_menu())


@user_private_router.message(
    or_f(Command("navigation"), (F.text.lower() == "навигация"))
)
@user_private_router.message(Command("navigation"))
async def navigation_cmd(message: types.Message):
    await message.answer("Навигация")


@user_private_router.message(
    or_f(Command("instruction"), (F.text.lower() == "инструкция"))
)
@user_private_router.message(Command("instruction"))
async def instruction_cmd(message: types.Message):
    await message.answer("Инструкция")


@user_private_router.message(or_f(Command("rules"), (F.text.lower() == "правила")))
@user_private_router.message(Command("rules"))
async def rules_cmd(message: types.Message):
    await message.answer("Правила")


@user_private_router.message(or_f(Command("active"), (F.text.lower() == "актив")))
@user_private_router.message(Command("active"))
async def active_cmd(message: types.Message):
    await message.answer("Актив")


@user_private_router.message(
    or_f(Command("payment"), (F.text.lower() == "купить публикацию"))
)
@user_private_router.message(Command("payment"))
async def payment_cmd(message: types.Message):
    await message.answer("Купить публикацию")


@user_private_router.message(or_f(Command("faq"), (F.text.lower() == "faq")))
@user_private_router.message(Command("faq"))
async def faq_cmd(message: types.Message):
    await message.answer("FAQ")


