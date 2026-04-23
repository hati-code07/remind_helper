from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database.db import SessionLocal
from models.schedule import Schedule
from states.schedule_state import ScheduleState

router = Router()

@router.message(lambda m: m.text == "➕ Добавить пару")
async def add_schedule_start(message: Message, state: FSMContext):
    await message.answer("📅 Введи день (например: Monday):")
    await state.set_state(ScheduleState.waiting_for_day)


@router.message(ScheduleState.waiting_for_day)
async def get_day(message: Message, state: FSMContext):
    await state.update_data(day=message.text)
    await message.answer("📘 Предмет:")
    await state.set_state(ScheduleState.waiting_for_subject)


@router.message(ScheduleState.waiting_for_subject)
async def get_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("⏰ Время (например 10:00-11:30):")
    await state.set_state(ScheduleState.waiting_for_time)


@router.message(ScheduleState.waiting_for_time)
async def get_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("👨‍🏫 Преподаватель:")
    await state.set_state(ScheduleState.waiting_for_teacher)


@router.message(ScheduleState.waiting_for_teacher)
async def save_schedule(message: Message, state: FSMContext):
    data = await state.get_data()

    async with SessionLocal() as session:
        lesson = Schedule(
            user_id=message.from_user.id,
            day=data["day"],
            subject=data["subject"],
            time=data["time"],
            teacher=message.text
        )
        session.add(lesson)
        await session.commit()

    await message.answer("✅ Пара добавлена")
    await state.clear()
    
    # 📅 ПРОСМОТР РАСПИСАНИЯ
@router.message(lambda m: m.text == "📅 Расписание")
async def show_schedule(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Schedule).where(Schedule.user_id == message.from_user.id)
        )
        lessons = result.scalars().all()

    if not lessons:
        await message.answer("Расписание пустое 📭")
        return

    # группировка по дням
    schedule_map = {}

    for lesson in lessons:
        schedule_map.setdefault(lesson.day, []).append(lesson)

    text = "📒 Твоё расписание:\n\n"

    for day, items in schedule_map.items():
        text += f"📅 {day}\n"
        for l in items:
            text += f"  • {l.time} — {l.subject} ({l.teacher})\n"
        text += "\n"

    await message.answer(text)