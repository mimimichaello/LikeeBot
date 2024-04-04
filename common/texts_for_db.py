from aiogram.utils.formatting import Bold, as_list, as_marked_section


categories = ['Подписки', "Акции"]


description_for_info_pages = {
    "main": "Добро пожаловать!",
    "navigation": "Нажмите на кнопку navigation для перехода",
    "instructions": "Нажмите на кнопку instructions для перехода",
    "rules": "Нажмите на кнопку rules для перехода",
    "faq": "Нажмите на кнопку faq для перехода",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        marker="✅ ",).as_html(),
    'catalog': 'Категории:',
}
