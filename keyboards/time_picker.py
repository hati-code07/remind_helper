# keyboards/time_picker.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

class TimePicker:
    """Класс для выбора времени с точностью до минуты"""
    
    @staticmethod
    def create_hour_keyboard(selected_hour=None):
        """Клавиатура выбора часа"""
        buttons = []
        row = []
        
        for hour in range(0, 24):
            # Выделяем выбранный час
            text = f"▶️ {hour:02d}" if selected_hour == hour else f"  {hour:02d}"
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
        buttons.append([
            InlineKeyboardButton(text="❌ Отмена", callback_data="time_cancel"),
            InlineKeyboardButton(text="✅ Готово" if selected_hour is not None else "➡️ Далее", 
                               callback_data="hour_done" if selected_hour is not None else "to_minutes")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def create_minute_keyboard(selected_minute=None):
        """Клавиатура выбора минут"""
        buttons = []
        row = []
        
        for minute in range(0, 60, 5):  # Шаг 5 минут
            # Выделяем выбранные минуты
            text = f"▶️ {minute:02d}" if selected_minute == minute else f"  {minute:02d}"
            row.append(InlineKeyboardButton(
                text=text,
                callback_data=f"minute_{minute}"
            ))
            
            # Каждые 6 кнопок новая строка (30 минут)
            if len(row) == 6:
                buttons.append(row)
                row = []
        
        if row:
            buttons.append(row)
        
        # Точная настройка минут (1 минута)
        fine_buttons = []
        for minute in [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 
                       21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34, 36, 37, 
                       38, 39, 41, 42, 43, 44, 46, 47, 48, 49, 51, 52, 53, 54, 
                       56, 57, 58, 59]:
            if minute % 5 != 0:  # Показываем только не кратные 5
                fine_buttons.append(InlineKeyboardButton(
                    text=f"{minute:02d}",
                    callback_data=f"minute_{minute}"
                ))
                if len(fine_buttons) == 6:
                    buttons.append(fine_buttons)
                    fine_buttons = []
        
        if fine_buttons:
            buttons.append(fine_buttons)
        
        # Кнопки управления
        nav_row = []
        if selected_minute is not None:
            nav_row.append(InlineKeyboardButton(text="⬅️ Назад к часам", callback_data="back_to_hours"))
        nav_row.append(InlineKeyboardButton(text="❌ Отмена", callback_data="time_cancel"))
        nav_row.append(InlineKeyboardButton(text="✅ Готово", callback_data="minute_done"))
        buttons.append(nav_row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    @staticmethod
    def create_time_display(hour, minute):
        """Показать выбранное время"""
        buttons = [
            [InlineKeyboardButton(text=f"🕐 {hour:02d}:{minute:02d}", callback_data="ignore")],
            [
                InlineKeyboardButton(text="✏️ Изменить час", callback_data="edit_hour"),
                InlineKeyboardButton(text="✏️ Изменить минуты", callback_data="edit_minute")
            ],
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="time_confirm"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="time_cancel")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)


class TimePickerCompact:
    """Компактный выбор времени (двойной слайдер)"""
    
    @staticmethod
    def create_slider(hour=12, minute=0):
        """Создать слайдер времени"""
        keyboard = []
        
        # Отображение текущего времени
        keyboard.append([
            InlineKeyboardButton(
                text=f"🕐 Текущее время: {hour:02d}:{minute:02d}",
                callback_data="ignore"
            )
        ])
        
        # Слайдер часов
        hour_row = []
        for h in [hour-2, hour-1, hour, hour+1, hour+2]:
            h = h % 24
            if h == hour:
                hour_row.append(InlineKeyboardButton(text=f"[{h:02d}]", callback_data=f"set_hour_{h}"))
            else:
                hour_row.append(InlineKeyboardButton(text=f"{h:02d}", callback_data=f"set_hour_{h}"))
        keyboard.append(hour_row)
        
        # Слайдер минут (с шагом 5 минут)
        minute_row = []
        for m in [minute-10, minute-5, minute, minute+5, minute+10]:
            m = m % 60
            if m == minute:
                minute_row.append(InlineKeyboardButton(text=f"[{m:02d}]", callback_data=f"set_minute_{m}"))
            else:
                minute_row.append(InlineKeyboardButton(text=f"{m:02d}", callback_data=f"set_minute_{m}"))
        keyboard.append(minute_row)
        
        # Тонкая настройка (+/- 1 минута)
        fine_row = [
            InlineKeyboardButton(text="-1", callback_data="minute_minus_1"),
            InlineKeyboardButton(text="+1", callback_data="minute_plus_1"),
            InlineKeyboardButton(text="-5", callback_data="minute_minus_5"),
            InlineKeyboardButton(text="+5", callback_data="minute_plus_5")
        ]
        keyboard.append(fine_row)
        
        # Кнопки действий
        keyboard.append([
            InlineKeyboardButton(text="🕐 Сейчас", callback_data="set_current_time"),
            InlineKeyboardButton(text="✅ Готово", callback_data="time_confirm"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="time_cancel")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)