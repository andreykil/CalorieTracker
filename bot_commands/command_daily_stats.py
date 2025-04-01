from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime

from database import get_db
from models import User
from states import DailyStats
from utils import get_daily_stats, text_daily_stats

router = Router()

@router.message(lambda message: message.text == text_daily_stats)
async def handle_set_goal_button(message: types.Message, state: FSMContext):
    await daily_stats_command(message, state)

@router.message(Command("daily_stats"))
async def daily_stats_command(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите дату в формате DD.MM.YYYY:")
    await state.set_state(DailyStats.waiting_for_date)

@router.message(DailyStats.waiting_for_date)
async def process_date(message: types.Message, state: FSMContext):
    try:
        date_str = message.text.strip()
        target_date = datetime.strptime(date_str, "%d.%m.%Y")

        db = next(get_db())
        telegram_id = message.from_user.id
        user = db.query(User).filter_by(telegram_id=telegram_id).first()

        if not user:
            await message.answer("Ошибка: пользователь не найден.")
            await state.clear()
            return

        stats = get_daily_stats(user, target_date)
        await message.answer(f"Статистика за {date_str}:\n{stats}")

    except ValueError:
        await message.answer("Ошибка: неверный формат даты. Используйте DD.MM.YYYY")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
    finally:
        await state.clear()
