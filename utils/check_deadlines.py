
from datetime import datetime
from sqlalchemy import select
from database.db import SessionLocal
from models.task import Task


async def check_missed_deadlines(bot):
    """Проверка просроченных задач при запуске бота"""
    async with SessionLocal() as session:
        result = await session.execute(
            select(Task).where(
                Task.deadline < datetime.now(),
                Task.status == "pending"
            )
        )
        missed_tasks = result.scalars().all()
        
        for task in missed_tasks:
            from utils.reminder import send_reminder
            await send_reminder(
                bot, 
                task.user_id, 
                f"⚠️ **ПРОСРОЧЕНА!**\n\n"
                f"Задача \"{task.title}\"\n"
                f"Дедлайн был: {task.deadline.strftime('%d.%m.%Y в %H:%M')}\n\n"
                f"Срочно заверши задачу!",
                task.id
            )
            # Отмечаем, что напоминание отправлено
            task.reminder_sent = True
            await session.commit()
