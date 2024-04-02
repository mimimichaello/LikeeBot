﻿from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.get_keyboard import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Добавить подпискy",
    "Изменить подпискy",
    "Удалить подпискy",
    "Я так, просто посмотреть зашел",
    placeholder="Выберите действие",
    sizes=(2, 1, 1),
)


@admin_router.message(Command("admin"))
async def add_subscribe(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Я так, просто посмотреть зашел")
async def starring_at_subscribe(message: types.Message):
    await message.answer("Ок, вот список подписок")


@admin_router.message(F.text == "Изменить подпискy")
async def change_subscribe(message: types.Message):
    await message.answer("ОК, вот список подписок")


@admin_router.message(F.text == "Удалить подпискy")
async def delete_subscribe(message: types.Message):
    await message.answer("Выберите подписку(и) для удаления")


# Машины состояний (FSM)


class AddSubscribe(StatesGroup):
    name = State()
    description = State()
    price = State()

    texts = {
        "AddSubscribe:name": "Введите название заново",
        "AddSubscribe:description": "Введите описание заново",
        "AddSubscribe:price": "Введите стоимость заново",
    }


@admin_router.message(StateFilter(None), F.text == "Добавить подпискy")
async def add_subscribe(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите название подписки", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSubscribe.name)


@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_KB)


@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddSubscribe.name:
        await message.answer(
            "Предыдущего шага нет, или введите название подписки или напишите отмена"
        )
        return

    previous = None
    for step in AddSubscribe.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Ок, вы вернулись к прошлому шагу \n{AddSubscribe.texts[previous.state]}"
            )
            return
        previous = step


@admin_router.message(AddSubscribe.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите описание подписки")
    await state.set_state(AddSubscribe.description)


@admin_router.message(AddSubscribe.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите стоимость подписки")
    await state.set_state(AddSubscribe.price)


@admin_router.message(AddSubscribe.price, F.text)
async def add_image(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Подписка добавлена", reply_markup=ADMIN_KB)
    data = await state.get_data()
    await message.answer(str(data))
    await state.clear()
