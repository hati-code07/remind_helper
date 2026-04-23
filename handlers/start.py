from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime

from database.db import SessionLocal
from models.user import User
from keyboards.menu import main_menu

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    async with SessionLocal() as session:
        # Проверяем, есть ли пользователь
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Создаем нового пользователя
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                created_at=datetime.now(),
                last_active=datetime.now()
            )
            session.add(user)
            await session.commit()
        else:
            # Обновляем время последней активности
            user.last_active = datetime.now()
            await session.commit()
    
    await message.answer(
        "Привет! Я HElPER 📚\n\n"
        "Твой помощник для учёбы!\n\n"
        "📝 Веди задачи\n"
        "📅 Планируй расписание\n"
        "⏰ Получай напоминания\n\n"
        "Выбери действие👇",
        reply_markup=main_menu()
    )