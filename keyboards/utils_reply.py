from keyboards.get_keyboard import get_keyboard


def start_menu():
    return get_keyboard(
        "Навигация",
        "Инструкция",
        "Правила",
        "Актив",
        "Купить публикацию",
        "FAQ",
        placeholder="Что вас интересует?",
        sizes=(3, 2, 1),
    )

