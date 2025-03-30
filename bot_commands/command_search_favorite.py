from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime

from database import get_db
from models import User, CalorieEntry, FavoriteProduct
from states import SearchFavoriteProduct
from utils import favorite_product_stats, get_daily_stats, entry_from_favorite
from bot_commands.command_start import text_search_favorite

router = Router()

@router.message(lambda message: message.text == text_search_favorite)
async def handle_search_favorite_button(message: types.Message, state: FSMContext):
    await start_search_favorite_product(message, state)

@router.message(Command("search_favorite"))
async def start_search_favorite_product(message: types.Message, state: FSMContext):
    await message.answer("Введите часть названия вашего блюда.")
    await state.set_state(SearchFavoriteProduct.waiting_for_search)


@router.message(SearchFavoriteProduct.waiting_for_search)
async def search_favorite_product(message: types.Message, state: FSMContext):
    search_query = (message.text.strip().lower())

    if not search_query:
        await message.answer("Ошибка: введите часть названия вашего блюда.")
        return

    if search_query == '?':
        search_query = ''
    db = next(get_db())
    products = db.query(FavoriteProduct).filter(FavoriteProduct.name.ilike(f"%{search_query}%")).all()

    if not products:
        await message.answer("Ваши блюда не найдены. Попробуйте другой запрос.")
        await state.clear()
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=products[i].name, callback_data=f"favorite_product_{products[i].id}"),
         types.InlineKeyboardButton(text=products[i+1].name, callback_data=f"favorite_product_{products[i+1].id}")]
        if i + 1 < len(products) else
        [types.InlineKeyboardButton(text=products[i].name, callback_data=f"favorite_product_{products[i].id}")]
        for i in range(0, len(products), 2)
    ])

    await message.answer("Найдены следующие ваши блюда:", reply_markup=keyboard)
    await state.clear()

@router.callback_query(lambda c: c.data.startswith("favorite_product_"))
async def process_favorite_product(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split("_")[-1])
    db = next(get_db())
    fav_product = (db.query(FavoriteProduct).filter_by(id=product_id).first())
    if not fav_product:
        await callback_query.message.answer("Ошибка: ваше блюдо не найдено.")
        return

    await callback_query.message.delete()
    await callback_query.message.answer(f"Вы выбрали: {fav_product.name}")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
         types.InlineKeyboardButton(text="Добавить", callback_data=f"add_favorite_product"),
        types.InlineKeyboardButton(text="Удалить", callback_data=f"delete_favorite"),
        types.InlineKeyboardButton(text="Назад", callback_data=f"finish_search_favorite"),
    ]])

    await callback_query.message.answer(f"Что дальше? Подробнее о блюде:\n" + favorite_product_stats(fav_product),
                                        reply_markup = keyboard)
    await state.clear()
    await state.update_data(product_id = product_id, product_name = fav_product.name)

@router.callback_query(lambda c: c.data == "add_favorite_product")
async def add_favorite_product(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")

    db = next(get_db())
    telegram_id = callback_query.from_user.id

    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        await callback_query.message.answer("Ошибка: пользователь не найден.")
        await state.clear()
        return

    product = db.query(FavoriteProduct).filter_by(id=product_id).first()
    if not product:
        await callback_query.message.answer("Ошибка: ваше блюдо не найдено.")
        await state.clear()
        return

    db.add(entry_from_favorite(product, user))
    db.commit()

    await callback_query.message.delete()
    await callback_query.message.answer(
        f"Добавлено блюдо {product.name} ({product.quantity}г.).\n\nСтатистика за сегодня:\n" +
        get_daily_stats(user, datetime.now().date())
    )

@router.callback_query(lambda c: c.data == "delete_favorite")
async def delete_favorite_request(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_name = data.get("product_name")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="Да", callback_data=f"deleting_accepted"),
        types.InlineKeyboardButton(text="Нет", callback_data=f"deleting_rejected"),
    ]])
    await callback_query.message.delete()
    await callback_query.message.answer(f"Вы точно хотите удалить блюдо {product_name}?", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "deleting_accepted")
async def delete_favorite(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")
    product_name = data.get("product_name")

    db = next(get_db())
    product = db.query(FavoriteProduct).filter_by(id=product_id).first()
    await callback_query.message.delete()
    if product:
        db.delete(product)
        db.commit()
        await callback_query.message.answer(f"Удалено ваше блюдо {product_name}.")
    else:
        await callback_query.message.answer("Ошибка: удаляемое блюдо не найдено.")
        await state.clear()

@router.callback_query(lambda c: c.data == "deleting_rejected")
async def delete_favorite(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer("Удаление отменено.")
    await state.clear()

@router.callback_query(lambda c: c.data == "finish_search_favorite")
async def finish_search_favorite_product(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.clear()