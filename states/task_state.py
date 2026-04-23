# states/task_state.py
from aiogram.fsm.state import State, StatesGroup

class TaskState(StatesGroup):
    waiting_for_title = State()
    waiting_for_deadline_date = State()
    waiting_for_deadline_time_hour = State()     # Выбор часа
    waiting_for_deadline_time_minute = State()   # Выбор минут
    waiting_for_deadline_time_confirm = State()  # Подтверждение
    editing_title = State()
    editing_deadline_date = State()
    editing_deadline_time = State()