# utils/reminder.py
from aiogram import Bot
from datetime import datetime, timedelta


async def send_reminder(bot: Bot, user_id: int, text: str, task_id: int = None):
    """Отправка напоминания о задаче"""
    message = f"⏰ **Напоминание!**\n\n{text}"
    
    if task_id:
        from keyboards.tasks import task_keyboard
        await bot.send_message(
            chat_id=user_id,
            text=message,
            reply_markup=task_keyboard(task_id),
            parse_mode="Markdown"
        )
    else:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )


async def send_day_before_reminder(bot: Bot, user_id: int, title: str, task_id: int, deadline: datetime):
    """Напоминание за день до дедлайна"""
    message = (
        f"⚠️ **ВНИМАНИЕ!**\n\n"
        f"Завтра дедлайн у задачи:\n"
        f"📝 *{title}*\n\n"
        f"⏰ Дедлайн: {deadline.strftime('%d.%m.%Y в %H:%M')}\n\n"
        f"Не забудь выполнить задачу вовремя!"
    )
    
    from keyboards.tasks import task_keyboard
    await bot.send_message(
        chat_id=user_id,
        text=message,
        reply_markup=task_keyboard(task_id),
        parse_mode="Markdown"
    )


async def send_hour_before_reminder(bot: Bot, user_id: int, title: str, task_id: int, deadline: datetime):
    """Напоминание за час до дедлайна"""
    message = (
        f"🔔 **Час до дедлайна!**\n\n"
        f"📝 *{title}*\n"
        f"⏰ Остался всего час!\n\n"
        f"Дедлайн: {deadline.strftime('%d.%m.%Y в %H:%M')}\n\n"
        f"Срочно завершай задачу!"
    )
    
    from keyboards.tasks import task_keyboard
    await bot.send_message(
        chat_id=user_id,
        text=message,
        reply_markup=task_keyboard(task_id),
        parse_mode="Markdown"
    )