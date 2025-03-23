from aiogram import Router, types
from aiogram.filters.command import Command

from database import get_db
from models import User, GlobalProduct, CalorieEntry, FavoriteProduct
from aiogram.fsm.context import FSMContext
from states import CreateFavoriteProduct
from utils import info_favorite_product

router = Router()

@router.message(lambda message: message.text == "Создать избранное блюдо")
async def handle_create_favorite_product_button(message: types.Message, state: FSMContext):
    await create_favorite_product(message, state)

@router.message(Command("create_favorite"))
async def create_favorite_product(message: types.Message, state: FSMContext):
    await message.answer("Введите название блюда:")
    await state.set_state(CreateFavoriteProduct.waiting_for_name)

@router.message(CreateFavoriteProduct.waiting_for_name)
async def process_favorite_name(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer("Введите вес блюда (в граммах):")
    await state.set_state(CreateFavoriteProduct.waiting_for_quantity)

@router.message(CreateFavoriteProduct.waiting_for_quantity)
async def process_favorite_quantity(message: types.Message, state: FSMContext):
    try:
        await state.update_data(quantity = message.text)
        await message.answer("Введите количество калорий на 100г:")
        await state.set_state(CreateFavoriteProduct.waiting_for_calories)
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
        await state.clear()

@router.message(CreateFavoriteProduct.waiting_for_calories)
async def process_favorite_calories(message: types.Message, state: FSMContext):
    try:
        await state.update_data(calories=message.text)
        await message.answer("Введите количество белков на 100г:")
        await state.set_state(CreateFavoriteProduct.waiting_for_proteins)
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
        await state.clear()

@router.message(CreateFavoriteProduct.waiting_for_proteins)
async def process_favorite_proteins(message: types.Message, state: FSMContext):
    try:
        await state.update_data(proteins=message.text)
        await message.answer("Введите количество жиров на 100г:")
        await state.set_state(CreateFavoriteProduct.waiting_for_fats)
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
        await state.clear()

@router.message(CreateFavoriteProduct.waiting_for_fats)
async def process_favorite_fats(message: types.Message, state: FSMContext):
    try:
        await state.update_data(fats=message.text)
        await message.answer("Введите количество углеводов на 100г:")
        await state.set_state(CreateFavoriteProduct.waiting_for_carbs)
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
        await state.clear()

@router.message(CreateFavoriteProduct.waiting_for_carbs)
async def process_favorite_carbs(message: types.Message, state: FSMContext):
    try:
        carbs = int(message.text)
        db = next(get_db())
        user_id = message.from_user.id
        user = db.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            await message.answer("Ошибка: пользователь не найден.")
            await state.clear()
            return
        data = await state.get_data()
        new_favorite = FavoriteProduct(
            name=data.get("name"),
            user_id=user.id,
            quantity=data.get("quantity"),
            calories=data.get("calories"),
            proteins=data.get("proteins"),
            fats=data.get("fats"),
            carbs=carbs
        )
        db.add(new_favorite)
        db.commit()

        await message.answer(f"Cоздано избранное блюдо:\n" + info_favorite_product(new_favorite))
    except ValueError:
        await message.answer("Ошибка: введите корректное число.")
    finally:
        await state.clear()