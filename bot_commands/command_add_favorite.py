# from aiogram import Router, types
# from aiogram.filters.command import Command
# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
#
# from database import get_db
# from models import User, GlobalProduct, FavoriteProduct, CalorieEntry
# from aiogram.fsm.context import FSMContext
# from states import CreateFavoriteProduct
#
# router = Router()
#
# @router.message(lambda message: message.text == "Добавить избранное блюдо")
# async def handle_add_global_button(message: types.Message, state: FSMContext):
#     await add_global_product(message, state)
#
# @router.message(Command("add_favorite"))
# async def add_global_product(message: types.Message, state: FSMContext):
#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton(text="Выбрать из базовых", callback_data=f"find_global_for_favorite"),
#          types.InlineKeyboardButton(text="Создать собственное блюдо", callback_data=f"create_favorite"),]
#     ])
#
#     await message.answer("Ты хочешь создать новое блюдо или выбрать из существующих?", reply_markup=keyboard)
#     await state.clear()
#
# @router.message(Command("find_global_for_favorite"))
# async def add_global_product(message: types.Message, state: FSMContext):
#     await message.answer("Введите часть названия блюда:")
#     await state.set_state(CreateFavoriteProduct.waiting_for_search_global)
#
#
# @router.message(AddGlobalProduct.waiting_for_search)
# async def search_global_product(message: types.Message, state: FSMContext):
#     search_query = (message.text.strip().lower())
#
#     if not search_query:
#         await message.answer("Ошибка: введите часть названия блюда.")
#         return
#
#     db = next(get_db())
#     products = db.query(GlobalProduct).filter(GlobalProduct.name.ilike(f"%{search_query}%")).all()
#
#     if not products:
#         await message.answer("Продукты не найдены. Попробуйте другой запрос.")
#         await state.clear()
#         return
#
#     keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
#         [types.InlineKeyboardButton(text=products[i].name, callback_data=f"global_product_{products[i].id}"),
#          types.InlineKeyboardButton(text=products[i+1].name, callback_data=f"global_product_{products[i+1].id}")]
#         if i + 1 < len(products) else
#         [types.InlineKeyboardButton(text=products[i].name, callback_data=f"global_product_{products[i].id}")]
#         for i in range(0, len(products), 2)
#     ])
#
#     await message.answer("Найдены следующие продукты:", reply_markup=keyboard)
#     await state.clear()
#
# @router.callback_query(lambda c: c.data.startswith("global_product_"))
# async def process_global_product(callback_query: types.CallbackQuery, state: FSMContext):
#     product_id = int(callback_query.data.split("_")[-1])
#
#     db = next(get_db())
#     product = db.query(GlobalProduct).filter_by(id=product_id).first()
#
#     if not product:
#         await callback_query.message.answer("Продукт не найден.")
#         return
#
#     await state.update_data(product_id=product_id)
#
#     await callback_query.message.answer(f"Ты выбрал: {product.name}. Укажи количество (в граммах):")
#     await state.set_state(AddGlobalProduct.waiting_for_quantity)
#
# @router.message(AddGlobalProduct.waiting_for_quantity)
# async def process_quantity(message: types.Message, state: FSMContext):
#     try:
#         quantity = int(message.text)
#         data = await state.get_data()
#         product_id = data.get("product_id")
#
#         db = next(get_db())
#         user_id = message.from_user.id
#
#         user = db.query(User).filter_by(telegram_id=user_id).first()
#         if not user:
#             await message.answer("Ошибка: пользователь не найден.")
#             await state.clear()
#             return
#
#         product = db.query(GlobalProduct).filter_by(id=product_id).first()
#         if not product:
#             await message.answer("Ошибка: продукт не найден.")
#             await state.clear()
#             return
#
#         new_entry = CalorieEntry(
#             user_id=user.id,
#             product_id=product.id,
#             quantity=quantity
#         )
#         db.add(new_entry)
#         db.commit()
#
#         total_calories = (product.calories * quantity) / 100
#         await message.answer(f"Добавлено {quantity} граммов {product.name}. Калорий: {total_calories:.0f} ккал.")
#
#     except ValueError:
#         await message.answer("Пожалуйста, введи корректное число.")
#     finally:
#         await state.clear()
