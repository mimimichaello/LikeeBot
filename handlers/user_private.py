from aiogram import types, Router, F
from aiogram.filters import CommandStart
from database.models import User
from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from aiogram import types
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
#from app import bot

from sqlalchemy.ext.asyncio import AsyncSession



user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    text, reply_markup = await get_menu_content(session, level=0, menu_name="main")

    await message.answer(text, reply_markup=reply_markup)




# class GetLink:
#     waiting_for_link = State()


# @user_private_router.callback_query(F.text == "Актив")
# async def process_active_button(callback: types.CallbackQuery):
#     await callback.message.answer(
#         "Пожалуйста, отправьте мне ссылку, которую вы хотите разместить в канале."
#     )
#     # Устанавливаем состояние ожидания ссылки от пользователя
#     await GetLink.waiting_for_link.set()


# # Обработчик для текстового сообщения (ссылки) от пользователя
# @user_private_router.message_handler(
#     state=GetLink.waiting_for_link, content_types=types.ContentTypes.TEXT
# )
# async def process_user_link(message: types.Message, state: FSMContext):
#     link = message.text
#     user = await User.get(message.from_user.id)
#     if user:
#         username = user.username
#         # Отправляем ссылку и имя пользователя в канал
#         await bot.send_message(
#             "https://t.me/+4mVEoYBhjl4wYTFi", f"Пользователь {username} прислал ссылку: {link}"
#         )
#         await bot.send_message(
#             message.chat.id, "Спасибо! Ваша ссылка отправлена в канал."
#         )
#     else:
#         # В случае, если пользователь не найден, отправляем только ссылку в канал без имени пользователя
#         await bot.send_message(
#             "https://t.me/+4mVEoYBhjl4wYTFi",
#             f"Пользователь с ID {message.from_user.id} прислал ссылку: {link}",
#         )
#         await bot.send_message(
#             message.chat.id, "Спасибо! Ваша ссылка отправлена в канал."
#         )

#     await state.finish()


