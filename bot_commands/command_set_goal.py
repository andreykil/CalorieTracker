from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from database import get_db
from models import User
from states import SetCalorieGoal
from utils import text_set_goal

router = Router()

# Команда /set_goal нужна для изменения цели по КБЖУ. Пользователю предлагается ввести цель по калориям, белкам, жирам и
# углеводам. Указанные значения вносятся в БД, и при "съедении" блюд в дальнейшем пользователю будет выведены его
# текущие показатели питания за день по сравнению с целью калорий.

@router.message(lambda message: message.text == text_set_goal)
async def handle_set_goal_button(message: types.Message, state: FSMContext):
    await set_goal_command(message, state)

@router.message(Command("set_goal"))
async def set_goal_command(message: types.Message, state: FSMContext):
    await message.answer("Укажите вашу цель по калориям (число):")
    await state.set_state(SetCalorieGoal.waiting_for_calorie_goal)

@router.message(SetCalorieGoal.waiting_for_calorie_goal)
async def process_calorie_goal(message: types.Message, state: FSMContext):
    try:
        calorie_goal = int(message.text)
        await state.update_data(calorie_goal=calorie_goal)
        await message.answer("Укажите вашу цель по белкам (число в граммах):")
        await state.set_state(SetCalorieGoal.waiting_for_proteins_goal)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()

@router.message(SetCalorieGoal.waiting_for_proteins_goal)
async def process_proteins_goal(message: types.Message, state: FSMContext):
    try:
        proteins_goal = int(message.text)
        await state.update_data(proteins_goal=proteins_goal)
        await message.answer("Укажите вашу цель по жирам (число в граммах):")
        await state.set_state(SetCalorieGoal.waiting_for_fats_goal)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()

@router.message(SetCalorieGoal.waiting_for_fats_goal)
async def process_fats_goal(message: types.Message, state: FSMContext):
    try:
        fats_goal = int(message.text)
        await state.update_data(fats_goal=fats_goal)
        await message.answer("Укажите вашу цель по углеводам (число в граммах):")
        await state.set_state(SetCalorieGoal.waiting_for_carbs_goal)
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
        await state.clear()

@router.message(SetCalorieGoal.waiting_for_carbs_goal)
async def process_carbs_goal(message: types.Message, state: FSMContext):
    try:
        carbs_goal = int(message.text)
        data = await state.get_data()

        db = next(get_db())
        telegram_id = message.from_user.id

        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if not user:
            await message.answer("Ошибка: пользователь не найден.")
            await state.clear()
            return

        user.calorie_goal = data["calorie_goal"]
        user.proteins_goal = data["proteins_goal"]
        user.fats_goal = data["fats_goal"]
        user.carbs_goal = carbs_goal
        db.commit()

        await message.answer(
            f"Ваши цели установлены:\n"
            f"Калории: {user.calorie_goal} ккал\n"
            f"Белки: {user.proteins_goal} г\n"
            f"Жиры: {user.fats_goal} г\n"
            f"Углеводы: {user.carbs_goal} г"
        )
    except ValueError:
        await message.answer("Ошибка: некорректное число.")
    finally:
        await state.clear()
