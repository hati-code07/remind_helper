# keyboards/calendar.py - упрощенная версия без aiogram-calendar
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

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

def time_keyboard():
    """Клавиатура для выбора времени"""
    buttons = [
        [
            InlineKeyboardButton(text="00:00", callback_data="hour_0"),
            InlineKeyboardButton(text="03:00", callback_data="hour_3"),
            InlineKeyboardButton(text="06:00", callback_data="hour_6"),
            InlineKeyboardButton(text="09:00", callback_data="hour_9")
        ],
        [
            InlineKeyboardButton(text="12:00", callback_data="hour_12"),
            InlineKeyboardButton(text="15:00", callback_data="hour_15"),
            InlineKeyboardButton(text="18:00", callback_data="hour_18"),
            InlineKeyboardButton(text="21:00", callback_data="hour_21")
        ],
        [
            InlineKeyboardButton(text=":00", callback_data="minute_0"),
            InlineKeyboardButton(text=":15", callback_data="minute_15"),
            InlineKeyboardButton(text=":30", callback_data="minute_30"),
            InlineKeyboardButton(text=":45", callback_data="minute_45")
        ],
        [
            InlineKeyboardButton(text="🕐 Сейчас", callback_data="time_now"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="time_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def confirm_keyboard():
    """Клавиатура подтверждения"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
            InlineKeyboardButton(text="📅 Изменить дату", callback_data="confirm_change_date")
        ],
        [
            InlineKeyboardButton(text="⏰ Изменить время", callback_data="confirm_change_time"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_cancel")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)