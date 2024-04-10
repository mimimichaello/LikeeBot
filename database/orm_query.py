import math
import os
from aiogram import Bot
from sqlalchemy import func, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from aiogram.enums import ParseMode

from database.models import LinkUsage, Subscribe, MenuText, User, Category

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


# Пагинатор
class Paginator:
    def __init__(self, array: list | tuple, page: int = 1, per_page: int = 1):
        self.array = array
        self.per_page = per_page
        self.page = page
        self.len = len(self.array)
        # math.ceil - округление в большую сторону до целого числа
        self.pages = math.ceil(self.len / self.per_page)

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self):
        page_items = self.__get_slice()
        return page_items

    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False

    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False

    def get_next(self):
        if self.page < self.pages:
            self.page += 1
            return self.get_page()
        raise IndexError(f"Next page does not exist. Use has_next() to check before.")

    def get_previous(self):
        if self.page > 1:
            self.page -= 1
            return self.__get_slice()
        raise IndexError(
            f"Previous page does not exist. Use has_previous() to check before."
        )


# Работа с MenuText (Информационными страницами)


async def orm_add_menu_description(session: AsyncSession, data: dict):
    # Добавляем новый или изменяем существующий по именам
    # пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(MenuText)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all(
        [
            MenuText(name=name, description=description)
            for name, description in data.items()
        ]
    )
    await session.commit()


async def orm_change_menu(session: AsyncSession, description: str, name: str):
    query = (
        update(MenuText).where(MenuText.name == name).values(description=description)
    )
    await session.execute(query)
    await session.commit()


async def orm_get_menu(session: AsyncSession, page: str):
    query = select(MenuText).where(MenuText.name == page)
    result = await session.execute(query)
    menu = result.scalar()
    return menu


async def orm_get_info_pages(session: AsyncSession):
    query = select(MenuText)
    result = await session.execute(query)
    return result.scalars().all()


# Категории


async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_create_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()


# Админка: Добавить/Изменить/Удалить подписку


async def orm_add_subscribe(session: AsyncSession, data: dict):
    obj = Subscribe(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        category_id=int(data["category_id"]),
    )
    session.add(obj)
    await session.commit()


async def orm_get_subscriptions(session: AsyncSession, category_id=None):
    if category_id is not None:
        query = select(Subscribe).where(Subscribe.category_id == int(category_id))
    else:
        query = select(Subscribe)

    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_subscribe(session: AsyncSession, subscribe_id: int):
    query = select(Subscribe).where(Subscribe.id == subscribe_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_subscribe(session: AsyncSession, subscribe_id: int, data):
    query = (
        update(Subscribe)
        .where(Subscribe.id == subscribe_id)
        .values(
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            category_id=int(data["category_id"]),
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_subscribe(session: AsyncSession, subscribe_id: int):
    query = delete(Subscribe).where(Subscribe.id == subscribe_id)
    await session.execute(query)
    await session.commit()


# user


async def orm_get_user(session: AsyncSession, user_id: int) -> User:
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    username: str,
    current_subscription_id: int | None = None,
    subscription_end_date: datetime | None = None,
    links_sent: datetime | None = None,
):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(
                id=user_id,
                username=username,
                current_subscription_id=current_subscription_id,
                subscription_end_date=subscription_end_date,
                links_sent=links_sent,
            )
        )
        await session.commit()


async def orm_update_link_sent(session: AsyncSession, user_id: int, new_date: datetime):
    query = update(User).where(User.id == user_id).values(link_sent=new_date)
    await session.execute(query)
    await session.commit()


async def get_user_subscription(session: AsyncSession, user_id: int):
    user = await orm_get_user(session, user_id)
    if user:
        return user.current_subscription
    else:
        return None


async def get_links_sent_count(
    session: AsyncSession, user_id: int, time_period: timedelta
) -> int:
    start_date = datetime.now() - time_period

    query = select(func.sum(LinkUsage.links_sent)).where(
        (LinkUsage.user_id == user_id) & (LinkUsage.created >= start_date)
    )

    result = await session.execute(query)
    count = result.scalar()

    return count if count else 0


async def send_to_private_channel(user_id: int, message: str):
    bot = Bot(token=os.getenv("TOKEN"))
    channel_id = os.getenv("CHANNEL_ID")
    await bot.send_message(chat_id=channel_id, text=message, parse_mode=ParseMode.HTML)


async def orm_increment_links_sent(session: AsyncSession, user_id: int):
    user = await orm_get_user(session, user_id)
    if user:
        user.links_sent += 1
        await session.commit()


async def orm_add_links_sent(session: AsyncSession, user_id: int):
    user = await orm_get_user(session, user_id)
    if not user:
        await orm_add_user(session, user_id, username="username")
        user = await orm_get_user(session, user_id)

    await orm_increment_links_sent(session, user_id)


async def invoice(
    user_id: int,
    subscription_name: str,
    subscription_description: str,
    subscription_price: float,
):
    bot = Bot(token=os.getenv("TOKEN"))
    await bot.send_invoice(
        chat_id=user_id,
        title="Оплата",
        description=f"{subscription_name} - {str(subscription_description)} ссылки в сутки",
        payload="month_sub",
        provider_token=os.getenv("PAYMENTS_TOKEN"),
        currency="RUB",
        start_parameter="payment",
        prices=[{"label": "Руб", "amount": int(subscription_price * 100)}],
    )


async def pre_checkout(pre_checkout_query):
    bot = Bot(token=os.getenv("TOKEN"))
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def send_invoice_and_update_db(
    user_id: int,
    subscription_name: str,
    subscription_description: str,
    subscription_price: float,
    session: AsyncSession,
):
    try:
        # Отправляем счет пользователю
        await invoice(
            user_id, subscription_name, subscription_description, subscription_price
        )

        # Получаем пользователя или добавляем нового пользователя
        await orm_add_user(session, user_id, user_id, subscription_name)

        # Обновляем информацию о текущей подписке пользователя
        await orm_update_subscribe(
            session,
            user_id,
            {
                "name": subscription_name,
                "description": subscription_description,
                "price": subscription_price,
            },
        )

        await session.commit()

    except Exception as e:
        print(f"Ошибка при обновлении базы данных: {e}")
        await session.rollback()
