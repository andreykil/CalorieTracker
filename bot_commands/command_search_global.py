from aiogram import Router, types
from aiogram.filters.command import Command

from database import get_db
from models import User, GlobalProduct, CalorieEntry, FavoriteProduct
from aiogram.fsm.context import FSMContext
from states import SearchGlobalProduct
from utils import info_global_product, info_favorite_product

router = Router()

@router.message(lambda message: message.text == "Найти базовое блюдо")
async def handle_search_global_button(message: types.Message, state: FSMContext):
    await start_search_global_product(message, state)

@router.message(Command("search_global"))
async def start_search_global_product(message: types.Message, state: FSMContext):
    await message.answer("Введите часть названия блюда:")
    await state.set_state(SearchGlobalProduct.waiting_for_search)


@router.message(SearchGlobalProduct.waiting_for_search)
async def search_global_product(message: types.Message, state: FSMContext):
    search_query = (message.text.strip().lower())

    if not search_query:
        await message.answer("Ошибка: введите часть названия блюда.")
        return

    db = next(get_db())
    products = db.query(GlobalProduct).filter(GlobalProduct.name.ilike(f"%{search_query}%")).all()

    if not products:
        await message.answer("Блюда не найдены. Попробуйте другой запрос.")
        await state.clear()
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=products[i].name, callback_data=f"global_product_{products[i].id}"),
         types.InlineKeyboardButton(text=products[i+1].name, callback_data=f"global_product_{products[i+1].id}")]
        if i + 1 < len(products) else
        [types.InlineKeyboardButton(text=products[i].name, callback_data=f"global_product_{products[i].id}")]
        for i in range(0, len(products), 2)
    ])

    await message.answer("Найдены следующие блюда:", reply_markup=keyboard)
    await state.clear()

@router.callback_query(lambda c: c.data.startswith("global_product_"))
async def process_global_product(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split("_")[-1])

    db = next(get_db())
    product = db.query(GlobalProduct).filter_by(id=product_id).first()

    if not product:
        await callback_query.message.answer("Ошибка: Блюдо не найдено.")
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
         types.InlineKeyboardButton(text="Добавить", callback_data=f"add_global_product"),
         types.InlineKeyboardButton(text="В избранные", callback_data=f"global_to_favorite"),
         types.InlineKeyboardButton(text="Информация", callback_data=f"info_global"),
    ]])

    await callback_query.message.answer(f"Вы выбрали: {product.name}\n", reply_markup = keyboard)
    await state.clear()
    await state.update_data(product_id = product_id)

@router.callback_query(lambda c: c.data == "add_global_product")
async def add_global_quantity_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите количество (в граммах):")
    await state.set_state(SearchGlobalProduct.waiting_for_add_quantity)

@router.message(SearchGlobalProduct.waiting_for_add_quantity)
async def add_global(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        data = await state.get_data()
        product_id = data.get("product_id")

        db = next(get_db())
        user_id = message.from_user.id

        user = db.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            await message.answer("Ошибка: пользователь не найден.")
            await state.clear()
            return

        product = db.query(GlobalProduct).filter_by(id=product_id).first()
        if not product:
            await message.answer("Ошибка: блюдо не найдено.")
            await state.clear()
            return

        new_entry = CalorieEntry(
            user_id=user.id,
            product_id=product.id,
            quantity=quantity
        )
        db.add(new_entry)
        db.commit()

        await message.answer(
            f"Добавлено {quantity} граммов {product.name}.\n"
            f"Калорий: {(product.calories*quantity/100):.0f}\n"
            f"Белков: {(product.proteins*quantity/100):.0f}\n"
            f"Жиров: {(product.fats*quantity/100):.0f}\n"
            f"Углеводов: {(product.carbs*quantity/100):.0f}"
        )

    except ValueError:
        await message.answer("Некорректное число.")
    finally:
        await state.clear()

@router.callback_query(lambda c: c.data.startswith("global_to_favorite"))
async def to_favorite_quantity_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите количество (в граммах):")
    await state.set_state(SearchGlobalProduct.waiting_for_favorite_quantity)

@router.message(SearchGlobalProduct.waiting_for_favorite_quantity)
async def to_favorite_name_request(message: types.Message, state: FSMContext):
    try:
        quantity = int(message.text)
        await state.update_data(quantity = quantity)
        await message.answer("Введите название избранного блюда:")
        await state.set_state(SearchGlobalProduct.waiting_for_favorite_name)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
        await state.clear()

@router.message(SearchGlobalProduct.waiting_for_favorite_name)
async def to_favorite(message: types.Message, state: FSMContext):
    name = str(message.text)
    data = await state.get_data()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    db = next(get_db())
    user_id = message.from_user.id

    user = db.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        await message.answer("Ошибка: пользователь не найден.")
        await state.clear()
        return

    product = db.query(GlobalProduct).filter_by(id=product_id).first()
    if not product:
        await message.answer("Ошибка: блюдо не найден.")
        await state.clear()
        return

    new_favorite = FavoriteProduct(
        user_id=user.id,
        global_product_id=product.id,
        quantity=quantity,
        name=name,
        calories=product.calories,
        proteins=product.proteins,
        fats=product.fats,
        carbs=product.carbs
    )
    db.add(new_favorite)
    db.commit()

    await message.answer(f"Cоздано избранное блюдо:\n" + info_favorite_product(new_favorite))
    await state.clear()

@router.callback_query(lambda c: c.data.startswith("info_global"))
async def process_global_info(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_id = data.get("product_id")
    db = next(get_db())
    product = db.query(GlobalProduct).filter_by(id=product_id).first()
    if not product:
        await callback_query.message.answer("Ошибка: блюдо не найдено.")
        await state.clear()
        return

    await callback_query.message.answer("Информация о блюде:\n" + info_global_product(product))
    await state.clear()