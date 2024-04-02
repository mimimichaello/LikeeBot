from aiogram import F, Router, types
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.utils_reply import admin_kb



admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())



@admin_router.message(Command("admin"))
async def add_subscribe(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=admin_kb)


@admin_router.message(F.text == "Я так, просто посмотреть зашел")
async def starring_at_subscribe(message: types.Message):
    await message.answer("ОК, вот список подпискок")


@admin_router.message(F.text == "Изменить товар")
async def change_subscribe(message: types.Message):
    await message.answer("ОК, вот список подпискок")


@admin_router.message(F.text == "Удалить товар")
async def delete_subscribe(message: types.Message):
    await message.answer("Выберите подписку(и) для удаления")


#Код ниже для машины состояний (FSM)

@admin_router.message(F.text == "Добавить товар")
async def add_subscribe(message: types.Message):
    await message.answer(
        "Введите название подписки", reply_markup=types.ReplyKeyboardRemove()
    )


@admin_router.message(Command("отмена"))
@admin_router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message) -> None:
    await message.answer("Действия отменены", reply_markup=admin_kb)


@admin_router.message(Command("назад"))
@admin_router.message(F.text.casefold() == "назад")
async def cancel_handler(message: types.Message) -> None:
    await message.answer(f"ок, вы вернулись к прошлому шагу")


@admin_router.message(F.text)
async def add_name(message: types.Message):
    await message.answer("Введите описание подписки")


@admin_router.message(F.text)
async def add_description(message: types.Message):
    await message.answer("Введите стоимость подписки")



@admin_router.message(F.photo)
async def add_image(message: types.Message):
    await message.answer("Подписка добавлена", reply_markup=admin_kb)
