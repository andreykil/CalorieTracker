from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime

from database import get_db
from models import User, GlobalProduct
from states import SearchGlobalProduct
from utils import global_product_stats, get_daily_stats, entry_from_global, text_search_global
from bot_commands.command_create_favorite import image_request

router = Router()

# Команда /search_global нужна для поиска базового блюда по названию. Пользователь вводит часть названия блюда,
# затем бот выводит базовые блюда, в названии которых есть введенная строка, в виде inline-клавиатуры.
# Пользователь может "съесть" блюдо, указав вес, либо добавить его в собственный список, указав название и вес порции.

@router.message(lambda message: message.text == text_search_global)
async def handle_search_global_button(message: types.Message, state: FSMContext):
    await search_global_product_command(message, state)

@router.message(Command("search_global"))
async def search_global_product_command(message: types.Message, state: FSMContext):
    await message.answer('Введите часть названия блюда или "Все", чтобы увидеть полный список:')
    await state.set_state(SearchGlobalProduct.waiting_for_search)

@router.message(SearchGlobalProduct.waiting_for_search)
async def process_global_product_search(message: types.Message, state: FSMContext):
    search_query = (message.text.strip().lower())

    if not search_query:
        await message.answer("Ошибка: введите часть названия блюда.")
        return

    if search_query == 'все':
        search_query = ''

    db = next(get_db())
    products = db.query(GlobalProduct).filter(GlobalProduct.name.ilike(f"%{search_query}%")).all()

    if not products:
        await message.answer("Блюда не найдены. Попробуйте другой запрос.")
        await state.clear()
        return

    products = products[:5]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=products[i].name, callback_data=f"global_product_{products[i].id}")]
        for i in range(0, len(products))
    ])

    await message.answer("Найдены следующие блюда:", reply_markup=keyboard)
    await state.clear()

@router.callback_query(lambda c: c.data.startswith("global_product_"))
async def process_chosen_global_product(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split("_")[-1])
    db = next(get_db())
    product = db.query(GlobalProduct).filter_by(id=product_id).first()
    if not product:
        await callback_query.message.answer("Ошибка: Блюдо не найдено.")
        await state.clear()
        return

    await callback_query.message.delete()
    await callback_query.message.answer(f"Вы выбрали: {product.name}")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
         types.InlineKeyboardButton(text="Съесть", callback_data=f"add_global_product"),
         types.InlineKeyboardButton(text="В свои", callback_data=f"global_to_favorite"),
         types.InlineKeyboardButton(text="Назад", callback_data=f"finish_search_global")
    ]])

    await callback_query.message.answer(f"Что дальше? Подробнее о блюде:\n" + global_product_stats(product),
                                        reply_markup = keyboard)

    await state.update_data(global_product_id=product.id)
    await state.update_data(telegram_id=callback_query.from_user.id)
    await state.update_data(calories=product.calories)
    await state.update_data(proteins=product.proteins)
    await state.update_data(fats=product.fats)
    await state.update_data(carbs=product.carbs)

@router.callback_query(lambda c: c.data == "add_global_product")
async def process_add_global_button(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer("Введите количество (в граммах):")
    await state.set_state(SearchGlobalProduct.waiting_for_add_quantity)

@router.message(SearchGlobalProduct.waiting_for_add_quantity)
async def process_add_global_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        data = await state.get_data()
        product_id = data.get("global_product_id")
        telegram_id = data.get("telegram_id")

        db = next(get_db())
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            await message.answer("Ошибка: пользователь не найден.")
            await state.clear()
            return

        product = db.query(GlobalProduct).filter_by(id=product_id).first()
        if not product:
            await message.answer("Ошибка: блюдо не найдено.")
            await state.clear()
            return

        db.add(entry_from_global(product, user, quantity))
        db.commit()

        await message.answer(f"Добавлено {quantity}г. {product.name}.\n\nСтатистика за сегодня:\n" +
                             get_daily_stats(user, datetime.now().date()))

    except ValueError:
        await message.answer("Ошибка: некорректное число.")
    finally:
        await state.clear()

@router.callback_query(lambda c: c.data == "global_to_favorite")
async def process_to_favorite_button(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer("Введите название вашего блюда:")
    await state.set_state(SearchGlobalProduct.waiting_for_favorite_name)

@router.message(SearchGlobalProduct.waiting_for_favorite_name)
async def process_to_favorite_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите количество (в граммах):")
    await state.set_state(SearchGlobalProduct.waiting_for_favorite_quantity)

@router.message(SearchGlobalProduct.waiting_for_favorite_quantity)
async def process_to_favorite_quantity(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        await state.update_data(quantity=quantity)
        await state.set_state(None)
        await image_request(message, state)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()

@router.callback_query(lambda c: c.data == "finish_search_global")
async def finish_search_global_product(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.clear()
