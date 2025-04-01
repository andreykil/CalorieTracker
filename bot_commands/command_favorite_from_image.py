import json
import numpy as np
from aiogram import Router, types, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from datetime import datetime

from database import get_db
from models import User, FavoriteProduct
from states import AddFavoriteFromImage
from image_recognition import extract_feature_vector, cosine_similarity
from utils import get_daily_stats, entry_from_favorite, text_add_favorite_from_image

router = Router()

@router.message(lambda message: message.text == text_add_favorite_from_image)
async def handle_favorite_from_image_button(message: types.Message, state: FSMContext):
    await favorite_from_image_command(message, state)

@router.message(Command("favorite_from_image"))
async def favorite_from_image_command(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото блюда:")
    await state.set_state(AddFavoriteFromImage.waiting_for_image)

class PhotoFilter(BaseFilter):
    async def __call__(self, message: types.Message) -> bool:
        return message.content_type == types.ContentType.PHOTO

@router.message(PhotoFilter(), AddFavoriteFromImage.waiting_for_image)
async def process_image(message: types.Message, state: FSMContext, bot: Bot):
    try:
        db = next(get_db())
        user_id = message.from_user.id
        user = db.query(User).filter_by(telegram_id=user_id).first()
        if not user:
            await message.answer("Ошибка: пользователь не найден.")
            await state.clear()
            return

        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        query_vector = extract_feature_vector(downloaded_file.read())

        favorite_products = (
            db.query(FavoriteProduct)
            .filter(FavoriteProduct.user_id == user.id)
            .filter(FavoriteProduct.feature_vector.isnot(None))
            .all()
        )

        if not favorite_products:
            await message.answer("У вас нет своих блюд с изображениями для поиска.")
            await state.clear()
            return

        max_similarity = -1
        best_match = None

        for product in favorite_products:
            stored_vector = np.array(json.loads(product.feature_vector))
            similarity = cosine_similarity(query_vector, stored_vector)
            if similarity > max_similarity:
                max_similarity = similarity
                best_match = product

        similarity_limit = 0.5 # настроить
        if best_match and max_similarity > similarity_limit:
            db.add(entry_from_favorite(best_match, user))
            db.commit()
            response = (f"Добавлено: {best_match.name} ({best_match.quantity}г.)\n\nСтатистика за сегодня:\n" +
                        get_daily_stats(user, datetime.now().date()))
            await message.answer(response)
        else:
            await message.answer("Не удалось найти похожее среди ваших блюд.")

        # debug info
        if best_match:
            await message.answer(f"Similarity: {max_similarity}\nSimilarity limit: {similarity_limit}")

        await state.clear()

    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
        await state.clear()
