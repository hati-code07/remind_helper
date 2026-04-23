from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def schedule_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Расписание")],
            [KeyboardButton(text="➕ Добавить пару")]
        ],
        resize_keyboard=True
    )