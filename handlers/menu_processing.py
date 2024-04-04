

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_menu
from keyboards.inline import get_user_main_btns


async def main_menu(session, level, menu_name):

    menu = await orm_get_menu(session, menu_name)
    text = menu.description

    kbds = get_user_main_btns(level=level)

    return text, kbds


async def get_menu_content(
        session: AsyncSession,
        level: int,
        menu_name: str,
):
    if level == 0:
        return await main_menu(session, level, menu_name)
