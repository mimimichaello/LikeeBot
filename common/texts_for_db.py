from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ["Подписки"]


description_for_info_pages = {
    "main": "Добро пожаловать!",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        marker="✅ ",
    ).as_html(),
    "catalog": "Категории:",
    "active": "Актив",
}
