from aiogram import Router, types, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
import json

from database import get_db
from models import User, GlobalProduct, CalorieEntry, FavoriteProduct
from states import CreateFavoriteProduct
from utils import favorite_product_stats, extract_feature_vector
from bot_commands.command_start import text_create_favorite

router = Router()

@router.message(lambda message: message.text == text_create_favorite)
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
        await state.update_data(quantity = int(message.text))
        await message.answer("Введите количество калорий на 100г:")
        await state.set_state(CreateFavoriteProduct.waiting_for_calories)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()

@router.message(CreateFavoriteProduct.waiting_for_calories)
async def process_favorite_calories(message: types.Message, state: FSMContext):
    try:
        await state.update_data(calories=int(message.text))
        await message.answer("Введите количество белков на 100г:")
        await state.set_state(CreateFavoriteProduct.waiting_for_proteins)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()

@router.message(CreateFavoriteProduct.waiting_for_proteins)
async def process_favorite_proteins(message: types.Message, state: FSMContext):
    try:
        await state.update_data(proteins=int(message.text))
        await message.answer("Введите количество жиров на 100г:")
        await state.set_state(CreateFavoriteProduct.waiting_for_fats)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()

@router.message(CreateFavoriteProduct.waiting_for_fats)
async def process_favorite_fats(message: types.Message, state: FSMContext):
    try:
        await state.update_data(fats=int(message.text))
        await message.answer("Введите количество углеводов на 100г:")
        await state.set_state(CreateFavoriteProduct.waiting_for_carbs)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()


@router.message(CreateFavoriteProduct.waiting_for_carbs)
async def process_favorite_carbs(message: types.Message, state: FSMContext):
    try:
        await state.update_data(carbs=int(message.text))
        await state.clear()
        await image_request(message, state)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()

async def image_request(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="Да", callback_data=f"add_image"),
        types.InlineKeyboardButton(text="Нет", callback_data=f"not_add_image"),
    ]])
    await message.answer("Хотите ли вы добавить фото блюда для быстрого распознавания?", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "add_image")
async def process_add_image_button(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer("Отправьте изображение блюда.")
    await state.set_state(CreateFavoriteProduct.waiting_for_image)

class PhotoFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.content_type == types.ContentType.PHOTO

@router.message(PhotoFilter(), CreateFavoriteProduct.waiting_for_image)
async def process_image(message: types.Message, state: FSMContext, bot: Bot):

    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    feature_vector = extract_feature_vector(downloaded_file.read())
    feature_vector_str = json.dumps(feature_vector.tolist())
    await state.update_data(feature_vector=feature_vector_str)

    await message.answer("Теперь блюдо будет распознаваться по изображению!")
    await finish_creating_favorite_product(message, state)

@router.callback_query(lambda c: c.data == "not_add_image")
async def process_no_image_button(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer("Изображение блюда отсутствует.")
    await state.update_data(feature_vector=None)
    await finish_creating_favorite_product(callback_query.message, state)

async def finish_creating_favorite_product(message: types.Message, state: FSMContext):
    db = next(get_db())
    user_id = message.from_user.id
    user = db.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        await message.answer("Ошибка: пользователь не найден.")
        await state.clear()
        return
    data = await state.get_data()
    new_favorite = FavoriteProduct(
        global_product_id=data.get("global_product_id"),
        name=data.get("name"),
        user_id=user.id,
        quantity=data.get("quantity"),
        calories=data.get("calories"),
        proteins=data.get("proteins"),
        fats=data.get("fats"),
        carbs=data.get("carbs"),
        feature_vector=data.get("feature_vector")
    )
    db.add(new_favorite)
    db.commit()
    await message.answer(f"Создано ваше блюдо {new_favorite.name}\n" + favorite_product_stats(new_favorite))
    await state.clear()