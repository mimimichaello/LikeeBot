from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


from database.orm_query import (
    Paginator,
    orm_get_categories,
    orm_get_menu,
    orm_get_subscribe,
    orm_get_subscriptions,
    orm_get_user,
)

from keyboards.inline import (
    get_payment_btns,
    get_subscriptions_btns,
    get_user_main_btns,
    get_user_catalog_btns,
)


async def main_menu(session, level, menu_name):

    menu = await orm_get_menu(session, menu_name)
    text = menu.description

    kbds = get_user_main_btns(level=level)

    return text, kbds


async def catalog(session, level, menu_name):
    menu = await orm_get_menu(session, menu_name)
    text = menu.description

    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return text, kbds


async def payment_btns(session, level, subscribe_id):
    subscribe = await orm_get_subscribe(session, subscribe_id)
    categories = await orm_get_categories(session)
    text = f"Хотите оплатить:\nНазвание: {subscribe.name}\nОписание: {subscribe.description}\nСтоимость: {subscribe.price}"

    kbds = get_payment_btns(level=level, subscribe_id=subscribe_id, categories=categories)

    return text, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns



async def subscriptions(session, level, category, page):
    subscriptions = await orm_get_subscriptions(session, category_id=category)

    paginator = Paginator(subscriptions, page=page)
    subscribe = paginator.get_page()[0]

    text = f"<strong>{subscribe.name}\
                </strong>\nДопустимое количество ссылок в сутки: {subscribe.description}\nСтоимость: {round(subscribe.price, 2)}\n\
                <strong>Подписка {paginator.page} из {paginator.pages}</strong>"

    pagination_btns = pages(paginator)

    kbds = get_subscriptions_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        subscribe_id=subscribe.id,
    )

    return text, kbds


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    subscribe_id: int | None = None,
    page: int | None = None,
):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await subscriptions(session, level, category, page)
