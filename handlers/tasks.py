# handlers/tasks.py
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.task_state import TaskState
from datetime import datetime, timedelta
from sqlalchemy import select, update

from database.db import SessionLocal
from models.task import Task
from models.user import User
from utils.scheduler import scheduler
from utils.reminder import send_reminder, send_day_before_reminder, send_hour_before_reminder
from keyboards.tasks import task_keyboard, edit_task_keyboard

router = Router()

# ========== ПРОСТОЙ КАЛЕНДАРЬ ==========

def create_calendar(year: int = None, month: int = None):
    """Создание простого календаря"""
    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month
    
    months_ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    
    keyboard = [
        [InlineKeyboardButton(
            text=f"{months_ru[month-1]} {year}",
            callback_data="ignore"
        )],
        [InlineKeyboardButton(text="Пн", callback_data="ignore"),
         InlineKeyboardButton(text="Вт", callback_data="ignore"),
         InlineKeyboardButton(text="Ср", callback_data="ignore"),
         InlineKeyboardButton(text="Чт", callback_data="ignore"),
         InlineKeyboardButton(text="Пт", callback_data="ignore"),
         InlineKeyboardButton(text="Сб", callback_data="ignore"),
         InlineKeyboardButton(text="Вс", callback_data="ignore")]
    ]
    
    first_day = datetime(year, month, 1)
    start_weekday = first_day.weekday()
    
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    days_in_month = (next_month - first_day).days
    
    week = []
    for _ in range(start_weekday):
        week.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
    
    for day in range(1, days_in_month + 1):
        week.append(InlineKeyboardButton(
            text=str(day),
            callback_data=f"date_{year}_{month}_{day}"
        ))
        
        if len(week) == 7:
            keyboard.append(week)
            week = []
    
    if week:
        while len(week) < 7:
            week.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
        keyboard.append(week)
    
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    keyboard.append([
        InlineKeyboardButton(text="◀️", callback_data=f"month_{prev_year}_{prev_month}"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_calendar"),
        InlineKeyboardButton(text="▶️", callback_data=f"month_{next_year}_{next_month}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ========== ВЫБОР ВРЕМЕНИ (КЛАССИЧЕСКИЙ) ==========

def create_hour_keyboard(selected_hour=None):
    """Клавиатура выбора часа"""
    buttons = []
    row = []
    
    for hour in range(0, 24):
        # Выделяем выбранный час
        if selected_hour == hour:
            text = f"▶️ {hour:02d}"
        else:
            text = f"  {hour:02d}"
        
        row.append(InlineKeyboardButton(
            text=text,
            callback_data=f"hour_{hour}"
        ))
        
        # Каждые 4 часа новая строка
        if len(row) == 4:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    # Кнопки навигации
    nav_buttons = []
    if selected_hour is not None:
        nav_buttons.append(InlineKeyboardButton(text="✅ Готово", callback_data="hour_done"))
    nav_buttons.append(InlineKeyboardButton(text="❌ Отмена", callback_data="time_cancel"))
    buttons.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def create_minute_keyboard(selected_minute=None):
    """Клавиатура выбора минут (с шагом 5 минут + точная настройка)"""
    buttons = []
    
    # Основные минуты (шаг 5 минут)
    row = []
    for minute in range(0, 60, 5):
        if selected_minute == minute:
            text = f"▶️ {minute:02d}"
        else:
            text = f"  {minute:02d}"
        
        row.append(InlineKeyboardButton(
            text=text,
            callback_data=f"minute_{minute}"
        ))
        
        if len(row) == 6:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    # Точная настройка (остальные минуты)
    fine_row = []
    for minute in range(1, 60):
        if minute % 5 != 0:  # Показываем только не кратные 5
            if selected_minute == minute:
                text = f"▶️ {minute:02d}"
            else:
                text = f"  {minute:02d}"
            
            fine_row.append(InlineKeyboardButton(
                text=text,
                callback_data=f"minute_{minute}"
            ))
            
            if len(fine_row) == 6:
                buttons.append(fine_row)
                fine_row = []
    
    if fine_row:
        buttons.append(fine_row)
    
    # Кнопки управления
    nav_buttons = [
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_hours"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="time_cancel"),
        InlineKeyboardButton(text="✅ Готово", callback_data="minute_done")
    ]
    buttons.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_time_keyboard():
    """Клавиатура подтверждения времени"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
            InlineKeyboardButton(text="✏️ Изменить час", callback_data="edit_hour")
        ],
        [
            InlineKeyboardButton(text="✏️ Изменить минуты", callback_data="edit_minute"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ========== ДОБАВЛЕНИЕ ЗАДАЧИ ==========

@router.message(lambda message: message.text == "➕ Добавить задачу")
async def menu_add(message: Message, state: FSMContext):
    await message.answer("📝 Введи текст задачи:")
    await state.set_state(TaskState.waiting_for_title)

@router.message(TaskState.waiting_for_title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    
    await message.answer(
        "📅 Выбери дату дедлайна:",
        reply_markup=create_calendar()
    )
    await state.set_state(TaskState.waiting_for_deadline_date)

@router.callback_query(lambda c: c.data.startswith(("date_", "month_", "cancel_calendar")))
async def process_calendar(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    
    if data == "cancel_calendar":
        await state.clear()
        await callback.message.edit_text("❌ Добавление задачи отменено")
        await callback.answer()
        return
    
    if data.startswith("month_"):
        _, year, month = data.split("_")
        await callback.message.edit_text(
            "📅 Выбери дату дедлайна:",
            reply_markup=create_calendar(int(year), int(month))
        )
        await callback.answer()
        return
    
    if data.startswith("date_"):
        _, year, month, day = data.split("_")
        selected_date = datetime(int(year), int(month), int(day))
        await state.update_data(selected_date=selected_date)
        
        # Показываем выбор часа
        await callback.message.edit_text(
            f"📅 Выбрана дата: {selected_date.strftime('%d.%m.%Y')}\n\n"
            f"⏰ Выбери час:",
            reply_markup=create_hour_keyboard()
        )
        await state.set_state(TaskState.waiting_for_deadline_time_hour)
        await callback.answer()

# Выбор часа
@router.callback_query(lambda c: c.data.startswith("hour_") and c.data != "hour_done")
async def process_hour_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора часа"""
    hour = int(callback.data.split("_")[1])
    await state.update_data(selected_hour=hour)
    
    # Обновляем клавиатуру с подсветкой выбранного часа
    await callback.message.edit_text(
        f"📅 Дата: {callback.message.text.split('Дата:')[1].split('⏰')[0] if 'Дата:' in callback.message.text else ''}\n\n"
        f"⏰ Выбран час: {hour:02d}\n\n"
        f"Выбери час (можно изменить):",
        reply_markup=create_hour_keyboard(selected_hour=hour)
    )
    await callback.answer(f"Выбран час: {hour:02d}")

@router.callback_query(lambda c: c.data == "hour_done")
async def hour_done(callback: CallbackQuery, state: FSMContext):
    """Завершение выбора часа, переход к минутам"""
    user_data = await state.get_data()
    selected_hour = user_data.get("selected_hour")
    selected_date = user_data.get("selected_date")
    
    if selected_hour is None:
        await callback.answer("❌ Сначала выбери час!")
        return
    
    await callback.message.edit_text(
        f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}\n"
        f"⏰ Выбран час: {selected_hour:02d}\n\n"
        f"Теперь выбери минуты:",
        reply_markup=create_minute_keyboard()
    )
    await state.set_state(TaskState.waiting_for_deadline_time_minute)
    await callback.answer()

# Выбор минут
@router.callback_query(lambda c: c.data.startswith("minute_") and c.data != "minute_done")
async def process_minute_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора минут"""
    minute = int(callback.data.split("_")[1])
    await state.update_data(selected_minute=minute)
    
    user_data = await state.get_data()
    selected_date = user_data.get("selected_date")
    selected_hour = user_data.get("selected_hour")
    
    # Обновляем клавиатуру с подсветкой выбранных минут
    await callback.message.edit_text(
        f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}\n"
        f"⏰ Время: {selected_hour:02d}:{minute:02d}\n\n"
        f"Выбери минуты (можно изменить):",
        reply_markup=create_minute_keyboard(selected_minute=minute)
    )
    await callback.answer(f"Выбрано минут: {minute:02d}")

@router.callback_query(lambda c: c.data == "back_to_hours")
async def back_to_hours(callback: CallbackQuery, state: FSMContext):
    """Вернуться к выбору часа"""
    user_data = await state.get_data()
    selected_date = user_data.get("selected_date")
    selected_hour = user_data.get("selected_hour")
    
    await callback.message.edit_text(
        f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}\n\n"
        f"⏰ Выбери час:",
        reply_markup=create_hour_keyboard(selected_hour=selected_hour)
    )
    await state.set_state(TaskState.waiting_for_deadline_time_hour)
    await callback.answer()

@router.callback_query(lambda c: c.data == "minute_done")
async def minute_done(callback: CallbackQuery, state: FSMContext):
    """Завершение выбора времени, показываем подтверждение"""
    user_data = await state.get_data()
    selected_date = user_data.get("selected_date")
    selected_hour = user_data.get("selected_hour")
    selected_minute = user_data.get("selected_minute", 0)
    
    if selected_minute is None:
        await callback.answer("❌ Сначала выбери минуты!")
        return
    
    deadline = selected_date.replace(hour=selected_hour, minute=selected_minute)
    
    await callback.message.edit_text(
        f"📅 Дата: {deadline.strftime('%d.%m.%Y')}\n"
        f"⏰ Время: {deadline.strftime('%H:%M')}\n\n"
        f"✅ Всё верно?",
        reply_markup=confirm_time_keyboard()
    )
    await state.set_state(TaskState.waiting_for_deadline_time_confirm)
    await callback.answer()

@router.callback_query(lambda c: c.data in ["edit_hour", "edit_minute"])
async def edit_time(callback: CallbackQuery, state: FSMContext):
    """Редактирование времени"""
    if callback.data == "edit_hour":
        user_data = await state.get_data()
        selected_date = user_data.get("selected_date")
        selected_hour = user_data.get("selected_hour")
        
        await callback.message.edit_text(
            f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}\n\n"
            f"⏰ Выбери новый час:",
            reply_markup=create_hour_keyboard(selected_hour=selected_hour)
        )
        await state.set_state(TaskState.waiting_for_deadline_time_hour)
    else:  # edit_minute
        user_data = await state.get_data()
        selected_date = user_data.get("selected_date")
        selected_hour = user_data.get("selected_hour")
        selected_minute = user_data.get("selected_minute", 0)
        
        await callback.message.edit_text(
            f"📅 Дата: {selected_date.strftime('%d.%m.%Y')}\n"
            f"⏰ Текущее время: {selected_hour:02d}:{selected_minute:02d}\n\n"
            f"Выбери новые минуты:",
            reply_markup=create_minute_keyboard(selected_minute=selected_minute)
        )
        await state.set_state(TaskState.waiting_for_deadline_time_minute)
    
    await callback.answer()

@router.callback_query(lambda c: c.data == "confirm_yes")
async def confirm_deadline(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Подтверждение создания задачи с планированием напоминаний"""
    user_data = await state.get_data()
    title = user_data.get("title")
    selected_date = user_data.get("selected_date")
    selected_hour = user_data.get("selected_hour")
    selected_minute = user_data.get("selected_minute", 0)
    
    deadline = selected_date.replace(hour=selected_hour, minute=selected_minute)
    
    if deadline < datetime.now():
        await callback.answer("❌ Дедлайн не может быть в прошлом!", show_alert=True)
        return
    
    async with SessionLocal() as session:
        task = Task(
            user_id=callback.from_user.id,
            title=title,
            deadline=deadline,
            reminder_sent=False,
            reminder_hour_sent=False
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        
        # Обновляем счетчик задач пользователя
        await session.execute(
            update(User)
            .where(User.telegram_id == callback.from_user.id)
            .values(tasks_count=User.tasks_count + 1)
        )
        await session.commit()
    
    # Планируем напоминание за день до дедлайна
    day_before = deadline - timedelta(days=1)
    if day_before > datetime.now():
        scheduler.add_job(
            send_day_before_reminder,
            "date",
            run_date=day_before,
            args=[bot, callback.from_user.id, title, task.id, deadline],
            id=f"day_before_{task.id}",
            replace_existing=True
        )
    
    # Планируем напоминание за час до дедлайна
    hour_before = deadline - timedelta(hours=1)
    if hour_before > datetime.now():
        scheduler.add_job(
            send_hour_before_reminder,
            "date",
            run_date=hour_before,
            args=[bot, callback.from_user.id, title, task.id, deadline],
            id=f"hour_before_{task.id}",
            replace_existing=True
        )
    
    # Планируем напоминание в момент дедлайна
    scheduler.add_job(
        send_reminder,
        "date",
        run_date=deadline,
        args=[bot, callback.from_user.id, f"⏰ Дедлайн задачи \"{title}\" настал! 🚨"],
        id=f"task_{task.id}",
        kwargs={"task_id": task.id}
    )
    
    await callback.message.edit_text(
        f"✅ Задача создана!\n\n"
        f"📝 {title}\n"
        f"⏰ {deadline.strftime('%d.%m.%Y в %H:%M')}\n\n"
        f"🔔 Напоминания:\n"
        f"• За день до дедлайна\n"
        f"• За час до дедлайна\n"
        f"• В момент дедлайна"
    )
    await state.clear()
    await callback.answer()

@router.callback_query(lambda c: c.data == "confirm_cancel")
async def confirm_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена создания задачи"""
    await state.clear()
    await callback.message.edit_text("❌ Создание задачи отменено")
    await callback.answer()

@router.callback_query(lambda c: c.data == "time_cancel")
async def time_cancel(callback: CallbackQuery, state: FSMContext):
    """Отмена выбора времени"""
    await state.clear()
    await callback.message.edit_text("❌ Добавление задачи отменено")
    await callback.answer()

# ========== ПРОСМОТР ЗАДАЧ ==========

@router.message(Command("tasks"))
@router.message(lambda message: message.text == "📋 Мои задачи")
async def get_tasks(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Task).where(Task.user_id == message.from_user.id)
        )
        tasks = result.scalars().all()

    if not tasks:
        await message.answer("У тебя пока нет задач 📭")
        return

    for task in tasks:
        status = "✅" if task.status == "done" else "⏳"
        deadline_text = f"\n⏰ {task.deadline.strftime('%d.%m.%Y %H:%M')}" if task.deadline else ""
        
        await message.answer(
            f"{'✅' if task.status == 'done' else '⏳'} *{task.title}*{deadline_text}",
            reply_markup=task_keyboard(task.id) if task.status != "done" else None,
            parse_mode="Markdown"
        )

# ========== ВЫПОЛНЕНИЕ, РЕДАКТИРОВАНИЕ, УДАЛЕНИЕ ==========

@router.callback_query(lambda c: c.data.startswith("done_"))
async def mark_done(callback: CallbackQuery):
    """Отметить задачу выполненной и удалить напоминания"""
    task_id = int(callback.data.split("_")[1])
    
    async with SessionLocal() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if task:
            task.status = "done"
            await session.commit()
            
            # Обновляем счетчик выполненных задач
            await session.execute(
                update(User)
                .where(User.telegram_id == task.user_id)
                .values(completed_tasks=User.completed_tasks + 1)
            )
            await session.commit()
            
            # Удаляем все напоминания
            jobs = scheduler.get_jobs()
            for job in jobs:
                if job.id in [f"task_{task_id}", f"day_before_{task_id}", f"hour_before_{task_id}"]:
                    job.remove()
    
    await callback.message.edit_text(f"✅ Задача выполнена!")
    await callback.answer("🎉 Отлично!")

@router.callback_query(lambda c: c.data.startswith("edit_") and not c.data.startswith("edit_title_") and not c.data.startswith("edit_deadline_"))
async def choose_edit_field(callback: CallbackQuery):
    """Выбор поля для редактирования"""
    task_id = int(callback.data.split("_")[1])
    
    async with SessionLocal() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            await callback.answer("Задача не найдена!")
            return
    
    await callback.message.edit_text(
        f"✏️ Редактируем задачу:\n\n"
        f"📝 {task.title}\n"
        f"⏰ {task.deadline.strftime('%d.%m.%Y %H:%M') if task.deadline else 'Без дедлайна'}\n\n"
        f"Что хотите изменить?",
        reply_markup=edit_task_keyboard(task_id)
    )
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_task(callback: CallbackQuery):
    """Удалить задачу и все напоминания"""
    task_id = int(callback.data.split("_")[1])
    
    async with SessionLocal() as session:
        result = await session.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if task:
            # Удаляем все напоминания
            jobs = scheduler.get_jobs()
            for job in jobs:
                if job.id in [f"task_{task_id}", f"day_before_{task_id}", f"hour_before_{task_id}"]:
                    job.remove()
            
            await session.delete(task)
            await session.commit()
            
            await callback.message.edit_text("🗑 Задача удалена!")
            await callback.answer("Удалено")
        else:
            await callback.answer("Задача не найдена!")

@router.callback_query(lambda c: c.data.startswith("cancel_edit_"))
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    """Отмена редактирования"""
    await state.clear()
    await callback.message.delete()
    await callback.answer("Редактирование отменено")

@router.message(Command("add_task"))
async def add_task_old(message: Message, state: FSMContext):
    """Старый обработчик /add_task"""
    await menu_add(message, state)