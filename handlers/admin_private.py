from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_add_subscribe,
    orm_delete_subscribe,
    orm_get_subscribe,
    orm_get_subscriptions,
    orm_update_subscribe,
)

from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.get_keyboard import get_keyboard
from keyboards.inline import get_callback_btns


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

ADMIN_KB = get_keyboard(
    "Добавить подпискy",
    "Список подписок",
    placeholder="Выберите действие",
    sizes=(2,),
)


class AddSubscribe(StatesGroup):
    name = State()
    description = State()
    price = State()

    subscribe_for_change = None

    texts = {
        "AddSubscribe:name": "Введите название заново",
        "AddSubscribe:description": "Введите допустимое количество ссылок в сутки заново",
        "AddSubscribe:price": "Введите стоимость заново",
    }


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Список подписок")
async def starring_at_subscribe(message: types.Message, session: AsyncSession):
    for subscribe in await orm_get_subscriptions(session):
        await message.answer(
            f"Название: <strong>{subscribe.name}</strong> \nДопустимое количество ссылок в сутки: {subscribe.description} \nСтоимость: {round(subscribe.price)}",
            reply_markup=get_callback_btns(
                btns={
                    "Изменить ✏️": f"change_{subscribe.id}",
                    "Удалить ❌": f"delete_{subscribe.id}",
                }
            ),
        )
    await message.answer("Ок, вот список подписок ⏫")


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_subscribe(callback: types.CallbackQuery, session: AsyncSession):
    subscribe_id = callback.data.split("_")[-1]
    await orm_delete_subscribe(session, int(subscribe_id))

    await callback.answer("Подписка удалена!")
    await callback.message.answer("Подписка удалена!")


@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_subscribe_callback(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    subscribe_id = callback.data.split("_")[-1]
    subscribe_for_change = await orm_get_subscribe(session, int(subscribe_id))

    AddSubscribe.subscribe_for_change = subscribe_for_change
    await callback.answer()
    await callback.message.answer(
        "Введите название подписки", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddSubscribe.name)


# Машины состояний (FSM)


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
    if AddSubscribe.subscribe_for_change:
        AddSubscribe.subscribe_for_change = None

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


@admin_router.message(AddSubscribe.name, or_f(F.text, F.text == "."))
async def add_name(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(name=AddSubscribe.subscribe_for_change.name)
    else:
        if len(message.text) >= 50:
            await message.answer("Название не может быть больше 50 символов")
            return

        await state.update_data(name=message.text)
    await message.answer("Введите допустимое количество ссылок в сутки")
    await state.set_state(AddSubscribe.description)


@admin_router.message(AddSubscribe.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer(
        "Вы ввели не допустимые данные, введите текст названия подписки"
    )


@admin_router.message(AddSubscribe.description, or_f(F.text, F.text == "."))
async def add_description(message: types.Message, state: FSMContext):
    if message.text == ".":
        await state.update_data(description=AddSubscribe.subscribe_for_change.description)
    else:
        if not message.text.isdigit():
            await message.answer("Введите допустимое количество ссылок в сутки")
            return
        await state.update_data(description=int(message.text))
    await message.answer("Введите стоимость подписки")
    await state.set_state(AddSubscribe.price)


@admin_router.message(AddSubscribe.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer(
        "Вы ввели не допустимые данные, введите допустимое количество ссылок в сутки"
    )


@admin_router.message(AddSubscribe.price, or_f(F.text, F.text == "."))
async def add_price(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == ".":
        await state.update_data(price=AddSubscribe.subscribe_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Введите корректное значение цены")
            return

        await state.update_data(price=message.text)
    data = await state.get_data()
    try:
        if AddSubscribe.subscribe_for_change:
            await orm_update_subscribe(session, AddSubscribe.subscribe_for_change.id, data)
        else:
            await orm_add_subscribe(session, data)
        await message.answer("Подписка добавлена | Изменена", reply_markup=ADMIN_KB)
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}", reply_markup=ADMIN_KB)
        await state.clear()

    AddSubscribe.subscribe_for_change = None

@admin_router.message(AddSubscribe.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer("Вы ввели не допустимые данные, введите стоимость подписки")
