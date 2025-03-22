from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database import get_db
from models import User
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить блюдо"), KeyboardButton(text="Добавить избранное блюдо")],
            [KeyboardButton(text="Новое избранное блюдо"), KeyboardButton(text="Изменить цель по калориям")],
        ],
        resize_keyboard=True,
        # one_time_keyboard=True
    )

    user_id = message.from_user.id
    username = message.from_user.username

    db = next(get_db())

    user = db.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        new_user = User(telegram_id=user_id, username=username)
        db.add(new_user)
        db.commit()
        await message.answer(f"Приветствую, {username or 'друг'}! Я помогу вам учитывать калории.",
                             reply_markup=keyboard)
    else:
        await message.answer(f"C возвращением, {username or 'друг'}!",
                             reply_markup=keyboard)

    # запрос цели калорий
    # if not user or user.calorie_goal is None:
    #     await message.answer("Укажи твою цель по калориям (число):")
    #     await state.set_state(SetCalorieGoal.waiting_for_calorie_goal)

