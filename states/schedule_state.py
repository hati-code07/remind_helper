from aiogram.fsm.state import StatesGroup, State


class ScheduleState(StatesGroup):
    waiting_for_day = State()
    waiting_for_subject = State()
    waiting_for_time = State()
    waiting_for_teacher = State()