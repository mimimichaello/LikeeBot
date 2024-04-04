import math
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from datetime import datetime

from database.models import Subscribe, MenuText, User, Category


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
    query = select(MenuText)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([MenuText(text=text) for text in data])
    await session.commit()


async def orm_change_menu_image(session: AsyncSession, text: str):
    query = update(MenuText).where(MenuText.text == text)
    await session.execute(query)
    await session.commit()


async def orm_get_menu(session: AsyncSession, page: str):
    query = select(MenuText).where(MenuText.text == page)
    result = await session.execute(query)
    return result.scalar()


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


async def orm_get_subscriptions(session: AsyncSession, category_id):
    query = select(Subscribe).where(Subscribe.category_id == int(category_id))
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


# Добавление юзера в БД

async def orm_add_user(
        session: AsyncSession,
        user_id: int,
        current_subscription_id: int | None = None,
        subscription_end_date: datetime | None = None,
):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(
                id=user_id,
                current_subscription_id=current_subscription_id,
                subscription_end_date=subscription_end_date,
            )
        )
        await session.commit()
