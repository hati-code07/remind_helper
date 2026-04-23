# keyboards/tasks.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_keyboard(task_id: int):
    """Клавиатура для задачи (выполнено, редактировать, удалить)"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Выполнено", callback_data=f"done_{task_id}"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{task_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete_{task_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def edit_task_keyboard(task_id: int):
    """Клавиатура для выбора что редактировать"""
    buttons = [
        [
            InlineKeyboardButton(text="📝 Название", callback_data=f"edit_title_{task_id}"),
            InlineKeyboardButton(text="⏰ Дедлайн", callback_data=f"edit_deadline_{task_id}")
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"cancel_edit_{task_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)