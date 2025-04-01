from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from database import get_db
from models import User
from bot_commands.command_set_goal import set_goal_command
from utils import (
    text_daily_stats,
    text_add_favorite_from_image,
    text_set_goal,
    text_search_global,
    text_search_favorite,
    text_create_favorite
)

router = Router()

# Команда /start нужна для начала работы с ботом. Если пользователь не зарегистрирован, он вносится в таблицу users,
# также в чат выводится краткая инструкция и создается Reply-клавиатура с командами бота. Если пользователь еще не
# указывал цель по КБЖУ, бот просит его это сделать.

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=text_add_favorite_from_image), KeyboardButton(text=text_search_favorite)],
            [KeyboardButton(text=text_search_global), KeyboardButton(text=text_create_favorite)],
            [KeyboardButton(text=text_set_goal), KeyboardButton(text=text_daily_stats)],
        ],
        resize_keyboard=True,
        # one_time_keyboard=True
    )

    telegram_id = message.from_user.id
    username = message.from_user.username

    db = next(get_db())

    user = db.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        new_user = User(telegram_id=telegram_id, username=username)
        db.add(new_user)
        db.commit()
        await message.answer(f"Приветствую, {username or 'друг'}! Я помогу вам учитывать калории.",
                             reply_markup=keyboard)
    else:
        await message.answer(f"C возвращением, {username or 'друг'}!",
                             reply_markup=keyboard)

    await message.answer(
        f"Краткая инструкция:\n\n"
        f"В боте есть список базовых блюд, содержащий основные популярные продукты питания, и список ваших "
        f"собственных блюд для более удобного доступа.\n\n"
        f"Вы можете сделать любое базовое блюдо своим, указав вес порции, либо создать свое блюдо вручную, указав "
        f"его характеристики.\n\n"
        f"При создании своего блюда вы можете добавить его изображение. В дальнейшем ваши блюда, "
        f"к которым добавлено изображение, можно будет добавлять в съеденные, отправив фото."
    )

    # optional goal request
    if not user or user.calorie_goal is None:
        await set_goal_command(message, state)
