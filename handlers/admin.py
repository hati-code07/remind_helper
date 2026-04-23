import asyncio
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from sqlalchemy import select, func, update

from database.db import SessionLocal
from models.user import User
from models.task import Task
from keyboards.admin import admin_menu, user_list_keyboard, user_actions_keyboard
from keyboards.menu import main_menu

router = Router()

# Состояния для рассылки
class MailingState(StatesGroup):
    waiting_for_message = State()

# Проверка на админа (замените на ваш Telegram ID)
ADMIN_IDS = [828358100]  # Добавьте сюда ваш Telegram ID

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Админ-панель"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ-панели!")
        return
    
    await message.answer(
        "👑 **Админ-панель**\n\n"
        "Выберите действие:",
        reply_markup=admin_menu(),
        parse_mode="Markdown"
    )

@router.message(lambda m: m.text == "📊 Статистика")
async def show_stats(message: Message):
    """Показать общую статистику"""
    if not is_admin(message.from_user.id):
        return
    
    async with SessionLocal() as session:
        # Общее количество пользователей
        total_users = await session.scalar(select(func.count()).select_from(User))
        
        # Пользователи за последние 7 дней
        week_ago = datetime.now() - timedelta(days=7)
        new_users_week = await session.scalar(
            select(func.count()).select_from(User).where(User.created_at >= week_ago)
        )
        
        # Активные за последние 24 часа
        day_ago = datetime.now() - timedelta(days=1)
        active_users = await session.scalar(
            select(func.count()).select_from(User).where(User.last_active >= day_ago)
        )
        
        # Общее количество задач
        total_tasks = await session.scalar(select(func.count()).select_from(Task))
        
        # Выполненные задачи
        completed_tasks = await session.scalar(
            select(func.count()).select_from(Task).where(Task.status == "done")
        )
        
        # Забаненные пользователи
        banned_users = await session.scalar(
            select(func.count()).select_from(User).where(User.is_banned == True)
        )
    
    stats_text = (
        "📊 **Статистика бота**\n\n"
        f"👥 **Всего пользователей:** {total_users}\n"
        f"🆕 **Новых за 7 дней:** {new_users_week}\n"
        f"🟢 **Активны за 24ч:** {active_users}\n"
        f"🚫 **Забанено:** {banned_users}\n\n"
        f"📝 **Всего задач:** {total_tasks}\n"
        f"✅ **Выполнено:** {completed_tasks}\n"
        f"📊 **Продуктивность:** {round(completed_tasks/total_tasks*100, 1) if total_tasks > 0 else 0}%"
    )
    
    await message.answer(stats_text, parse_mode="Markdown")

@router.message(lambda m: m.text == "👥 Список пользователей")
async def list_users(message: Message, page: int = 0):
    """Показать список пользователей"""
    if not is_admin(message.from_user.id):
        return
    
    items_per_page = 5
    
    async with SessionLocal() as session:
        # Получаем пользователей с пагинацией
        result = await session.execute(
            select(User)
            .order_by(User.created_at.desc())
            .offset(page * items_per_page)
            .limit(items_per_page)
        )
        users = result.scalars().all()
        
        # Общее количество
        total = await session.scalar(select(func.count()).select_from(User))
    
    if not users:
        await message.answer("📭 Пользователей не найдено")
        return
    
    text = f"👥 **Список пользователей** (стр. {page + 1}/{(total-1)//items_per_page + 1})\n\n"
    
    for i, user in enumerate(users, start=page*items_per_page + 1):
        status = "🚫" if user.is_banned else "🟢"
        text += f"{i}. {status} {user.first_name or 'No name'} - @{user.username or 'no_username'}\n"
        text += f"   ID: `{user.telegram_id}` | Задач: {user.tasks_count}\n\n"
    
    await message.answer(text, parse_mode="Markdown", reply_markup=user_list_keyboard(users, page))

@router.callback_query(lambda c: c.data.startswith("users_page_"))
async def users_page(callback: CallbackQuery):
    """Пагинация списка пользователей"""
    page = int(callback.data.split("_")[2])
    await list_users(callback.message, page)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("user_"))
async def user_details(callback: CallbackQuery):
    """Детальная информация о пользователе"""
    user_id = int(callback.data.split("_")[1])
    
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            await callback.answer("Пользователь не найден")
            return
    
    text = (
        f"👤 **Информация о пользователе**\n\n"
        f"**ID:** `{user.telegram_id}`\n"
        f"**Имя:** {user.first_name or 'Не указано'}\n"
        f"**Фамилия:** {user.last_name or 'Не указано'}\n"
        f"**Юзернейм:** @{user.username or 'Не указан'}\n"
        f"**Статус:** {'🚫 Забанен' if user.is_banned else '🟢 Активен'}\n"
        f"**Админ:** {'✅ Да' if user.is_admin else '❌ Нет'}\n\n"
        f"**📅 Регистрация:** {user.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"**🕐 Последняя активность:** {user.last_active.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"**📝 Создано задач:** {user.tasks_count}\n"
        f"**✅ Выполнено:** {user.completed_tasks}\n"
        f"**📊 Продуктивность:** {round(user.completed_tasks/user.tasks_count*100, 1) if user.tasks_count > 0 else 0}%"
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=user_actions_keyboard(user.telegram_id, user.is_banned))
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("ban_"))
async def ban_user(callback: CallbackQuery):
    """Забаннить/разбаннить пользователя"""
    user_id = int(callback.data.split("_")[1])
    
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.is_banned = not user.is_banned
            await session.commit()
            status = "забанен" if user.is_banned else "разбанен"
            await callback.answer(f"✅ Пользователь {status}")
    
    # Обновляем информацию
    await user_details(callback)

@router.callback_query(lambda c: c.data == "back_to_users")
async def back_to_users(callback: CallbackQuery):
    """Вернуться к списку пользователей"""
    await list_users(callback.message, 0)
    await callback.answer()

@router.callback_query(lambda c: c.data == "close_users")
async def close_users(callback: CallbackQuery):
    """Закрыть список пользователей"""
    await callback.message.delete()
    await callback.answer()

@router.message(lambda m: m.text == "📈 Активность за день")
async def daily_activity(message: Message):
    """Показать активность за день"""
    if not is_admin(message.from_user.id):
        return
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    async with SessionLocal() as session:
        # Новые пользователи сегодня
        new_users = await session.scalar(
            select(func.count()).select_from(User).where(User.created_at >= today)
        )
        
        # Активные сегодня
        active_users = await session.scalar(
            select(func.count()).select_from(User).where(User.last_active >= today)
        )
        
        # Задачи созданные сегодня
        new_tasks = await session.scalar(
            select(func.count()).select_from(Task).where(Task.deadline >= today)
        )
        
        # Выполненные сегодня
        completed_today = await session.scalar(
            select(func.count()).select_from(Task).where(
                Task.status == "done",
                Task.deadline >= today
            )
        )
    
    text = (
        f"📈 **Активность за сегодня** ({today.strftime('%d.%m.%Y')})\n\n"
        f"👤 **Новых пользователей:** {new_users}\n"
        f"🟢 **Активных пользователей:** {active_users}\n"
        f"📝 **Создано задач:** {new_tasks}\n"
        f"✅ **Выполнено задач:** {completed_today}\n"
        f"📊 **Продуктивность:** {round(completed_today/new_tasks*100, 1) if new_tasks > 0 else 0}%"
    )
    
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda m: m.text == "📨 Рассылка")
async def start_mailing(message: Message, state: FSMContext):
    """Начать рассылку"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "📨 **Рассылка**\n\n"
        "Отправьте сообщение для рассылки всем пользователям.\n"
        "Можно отправлять текст, фото, видео.\n\n"
        "❌ Для отмены отправьте /cancel",
        parse_mode="Markdown"
    )
    await state.set_state(MailingState.waiting_for_message)

@router.message(MailingState.waiting_for_message)
async def send_mailing(message: Message, state: FSMContext, bot: Bot):
    """Отправить рассылку"""
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.is_banned == False))
        users = result.scalars().all()
    
    success = 0
    failed = 0
    
    status_msg = await message.answer("🔄 Начинаю рассылку...")
    
    for user in users:
        try:
            if message.text:
                await bot.send_message(user.telegram_id, message.text)
            elif message.photo:
                await bot.send_photo(user.telegram_id, message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                await bot.send_video(user.telegram_id, message.video.file_id, caption=message.caption)
            
            success += 1
        except:
            failed += 1
        
        # Небольшая задержка, чтобы не заблокировали
        await asyncio.sleep(0.05)
    
    await status_msg.edit_text(
        f"✅ **Рассылка завершена!**\n\n"
        f"📨 Отправлено: {success}\n"
        f"❌ Не доставлено: {failed}\n"
        f"👥 Всего пользователей: {len(users)}",
        parse_mode="Markdown"
    )
    
    await state.clear()

@router.message(lambda m: m.text == "⬅️ Назад в меню")
async def back_to_main(message: Message):
    """Вернуться в главное меню"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🏠 Возвращаемся в главное меню",
        reply_markup=main_menu()
    )