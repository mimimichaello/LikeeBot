from datetime import datetime
from datetime import timedelta
import logging

from aiogram.filters import CommandStart


from database.models import User
from database.orm_query import (
    get_links_sent_count,
    invoice,
    orm_add_links_sent,
    orm_add_user,
    orm_get_subscribe,
    orm_get_user,
    orm_increment_links_sent,
    orm_update_link_sent,
    pre_checkout,
    send_to_private_channel,
    update_user_sub_id,
    update_user_subscription,
)
from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from aiogram import F, types

from aiogram import Router

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

    # Проверяем, что сообщение содержит текст и начинается с "http" или "www."
    if text and (text.startswith("http") or text.startswith("www.")):
        await send_link(message, session)
    else:
        await process_successful_payment(message, session)



@user_private_router.message()
async def send_link(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    username = message.from_user.username

    user = await orm_get_user(session, user_id)
    if not user:
        await orm_add_user(session, user_id, username=username)
    else:
        user = await orm_get_user(session, user_id)

    links_sent_today = user.links_sent

    # Проверяем, сколько пользователь уже отправил ссылок сегодня

    if links_sent_today >= user.daily_link_limit:
        await message.answer("Вы исчерпали лимит ссылок на сегодня. Попробуйте через 24 часа.")
        return

    else:
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

        await message.answer("Ссылка успешно отправлена в телеграм-канал.")


async def buy_subscription(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):
    subscribe_id = callback_data.subscribe_id
    subscription = await orm_get_subscribe(session, subscribe_id=subscribe_id)

    user_id = callback.from_user.id
    username = callback.from_user.username

    subscription_name = subscription.name
    subscription_description = subscription.description
    subscription_price = subscription.price
    await invoice(
        user_id, subscription_name, subscription_description, subscription_price
    )

    user = await orm_get_user(session, user_id)
    if not user:
        await orm_add_user(session, user_id, username=username)
        user = await orm_get_user(session, user_id)

    await update_user_sub_id(session, user_id, subscribe_id)


@user_private_router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout(pre_checkout_query)

@user_private_router.message()
async def process_successful_payment(message: types.Message, session: AsyncSession):
    if message.successful_payment and message.successful_payment.invoice_payload == "month_subscription":
        await message.answer("Подписка оформлена")
        user_id = message.from_user.id
        user = await orm_get_user(session, user_id)
        subscribe_id = user.current_subscription_id
        await update_user_subscription(session, user_id, subscribe_id)
        return
