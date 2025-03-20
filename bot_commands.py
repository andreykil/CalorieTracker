from aiogram import Router, types
from aiogram.filters.command import Command
from database import get_db
from models import User

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    db = next(get_db())

    user = db.query(User).filter_by(telegram_id=user_id).first()
    if not user:
        new_user = User(telegram_id=user_id, username=username)
        db.add(new_user)
        db.commit()
        await message.answer(f"Приветствую, {username or 'друг'}! Я помогу Вам учитывать калории.")
    else:
        await message.answer(f"C возвращением, {username or 'друг'}!")
