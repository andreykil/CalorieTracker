from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from database import get_db
from models import User
from states import SetCalorieGoal
from bot_commands.command_start import text_set_goal

router = Router()

@router.message(lambda message: message.text == text_set_goal)
async def handle_set_goal_button(message: types.Message, state: FSMContext):
    await set_calorie_goal(message, state)

@router.message(Command("set_goal"))
async def set_calorie_goal(message: types.Message, state: FSMContext):
    await message.answer("Укажите вашу цель по калориям (число):")
    await state.set_state(SetCalorieGoal.waiting_for_calorie_goal)

@router.message(SetCalorieGoal.waiting_for_calorie_goal)
async def process_calorie_goal(message: types.Message, state: FSMContext):
    try:
        calorie_goal = int(message.text)

        db = next(get_db())
        telegram_id = message.from_user.id

        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            await message.answer("Ошибка: пользователь не найден")
            await state.clear()
            return

        user.calorie_goal = calorie_goal
        db.commit()

        await message.answer(f"Ваша цель по калориям: {calorie_goal} ккал.")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число.")
    finally:
        await state.clear()

