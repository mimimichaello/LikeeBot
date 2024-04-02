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


def admin_kb():
    return get_keyboard(
        "Добавить подписку",
        "Изменить подписку",
        "Удалить подписку",
        "Я так, просто посмотреть зашел",
        placeholder="Выберите действие",
        sizes=(2, 1, 1),
    )
