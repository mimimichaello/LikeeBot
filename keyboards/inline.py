from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    # category: int | None = None
    # page: int = 1
    # subscribe_id: int | None = None


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    btns = {
        "Навигация": "https://telegra.ph/Navigaciya-v-LikeeUp-Bot-03-29",
        "Инструкция": "https://telegra.ph/Instrukciya-po-Botu-LikeeUp-03-29",
        "Правила": "https://telegra.ph/Pravila-LikeeUp-03-29",
        "FAQ": "https://telegra.ph/FAQ-LikeeUp-03-30",
        "Актив": "active",
        "Купить подписку": "payment",
        "Каталог": "catalog",
    }
    for text, menu_name in btns.items():
        if menu_name == "catalog":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()
                )
            )
    for text, menu_name in btns.items():
        if "://" in menu_name:
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    url=menu_name
                )
            )

    return keyboard.adjust(*sizes).as_markup()


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_url_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():

        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


# Микс из CallBack и URL кнопок
def get_inlineMix_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):

    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if "://" in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()
