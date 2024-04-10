import os
from datetime import datetime
from datetime import timedelta
from aiogram import types, Router, F
from aiogram.filters import CommandStart

from dotenv import find_dotenv, load_dotenv

from database.orm_query import (
    get_links_sent_count,
    get_user_subscription,
    invoice,
    orm_add_links_sent,
    orm_add_user,
    orm_get_subscribe,
    orm_get_subscriptions,
    orm_get_user,
    orm_increment_links_sent,
    orm_update_link_sent,
    orm_update_subscribe,
    pre_checkout,
    send_invoice_and_update_db,
    send_to_private_channel,
)
from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from aiogram import types

from aiogram.types import ContentType


from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.get_keyboard import get_keyboard

from keyboards.inline import MenuCallBack


user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


ACTIVE_KB = get_keyboard(
    "Отправить ссылку",
    placeholder="Выберите действие",
    sizes=(2,),
)


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    text, reply_markup = await get_menu_content(session, level=0, menu_name="main")

    await message.answer(text, reply_markup=reply_markup)


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):

    if callback_data.menu_name == "payment":
        await buy_subscription(callback, callback_data, session)
        return

    text, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        subscribe_id=callback_data.subscribe_id,
        page=callback_data.page,
    )

    await callback.message.edit_text(text, reply_markup=reply_markup)
    await callback.answer()


async def buy_subscription(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):
    subscribe_id = callback_data.subscribe_id
    subscription = await orm_get_subscribe(session, subscribe_id=subscribe_id)

    # Получаем данные для отправки счета
    user_id = callback.from_user.id
    subscription_name = subscription.name
    subscription_description = subscription.description
    subscription_price = subscription.price

    # Отправляем счет пользователю и передаем данные
    await invoice(
        user_id, subscription_name, subscription_description, subscription_price
    )




@user_private_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout(pre_checkout_query)


@user_private_router.message()
async def process_successful_payment(
    message: types.Message,
):
    if (
        message.successful_payment
        and message.successful_payment.invoice_payload == "month_sub"
    ):
        await message.answer("Подписка оформлена")


@user_private_router.callback_query(F.data == "active")
async def active_button(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "Пожалуйста, прикрепите ссылку, которую хотите отправить."
    )


@user_private_router.message()
async def process_link(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    text = message.text

    if text.startswith("http") or text.startswith("www."):
        await send_link(message, session)  # Если получена ссылка, обрабатываем ее
    else:
        await message.answer("Вы не отправили ссылку. Пожалуйста, прикрепите ссылку.")


async def send_link(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    username = message.from_user.username

    user = await orm_get_user(session, user_id)

    if not user:
        await orm_add_user(session, user_id, username=username)
        user = await orm_get_user(
            session, user_id
        )  # Получаем информацию о созданном пользователе

    current_time = datetime.now()
    last_sent_time = user.link_sent

    if last_sent_time and (current_time - last_sent_time) < timedelta(hours=24):
        await message.answer("Вы уже отправляли ссылку в течение последних 24 часов.")
        return

    subscription = await get_user_subscription(session, user_id)

    if not subscription:
        links_sent_today = await get_links_sent_count(
            session, user_id, timedelta(days=1)
        )

        if links_sent_today > 0:
            await message.answer(
                "У вас нет активной подписки. Вы можете отправить только одну ссылку в сутки."
            )
            return
    else:
        max_links_per_day = int(subscription.description)
        links_sent_today = await get_links_sent_count(
            session, user_id, timedelta(days=1)
        )

        if links_sent_today >= max_links_per_day:
            await message.answer(
                "Вы исчерпали лимит ссылок на сегодня по вашей подписке."
            )
            return

    # Отправляем ссылку в закрытый ТГ канал
    await send_to_private_channel(
        user_id,
        f"<strong>Имя пользователя(username):</strong> {username}\n<strong>Ссылка:</strong> {message.text}",
    )

    # Если все проверки пройдены, обновляем информацию о пользователе и использовании ссылок
    new_date = datetime.now()
    await orm_update_link_sent(session, user_id, new_date)

    count = await get_links_sent_count(session, user_id, timedelta(days=1))
    if count:
        await orm_increment_links_sent(session, user_id)
    else:
        await orm_add_links_sent(session, user_id)

    await session.commit()

    await message.answer("Ссылка успешно отправлена в телеграм канал.")





# async def process_successful_payment(
#     message: types.Message,
#     session: AsyncSession,
#     subscription_name: str,
#     subscription_description: str,
#     subscription_price: float,
#     user_id: int,
# ):
#     if (
#         message.successful_payment
#         and message.successful_payment.invoice_payload == "month_sub"
#     ):
#         try:
#             await send_invoice_and_update_db(
#                 user_id,
#                 subscription_name,
#                 subscription_description,
#                 subscription_price,
#                 session,
#             )
#             await update_subscription_data(user_id, session, subscription_name, subscription_description, subscription_price)
#             await message.answer("Подписка оплачена и данные обновлены.")
#         except Exception as e:
#             print(f"Ошибка при обновлении базы данных: {e}")

# async def update_subscription_data(
#     user_id: int,
#     session: AsyncSession,
#     subscription_name: str,
#     subscription_description: str,
#     subscription_price: float,
# ):
#     try:
#         # Обновляем информацию о подписке пользователя
#         await orm_update_subscribe(session, user_id, {
#             "name": subscription_name,
#             "description": subscription_description,
#             "price": subscription_price,
#         })
#         await session.commit()
#     except Exception as e:
#         print(f"Ошибка при обновлении базы данных: {e}")
#         await session.rollback()
