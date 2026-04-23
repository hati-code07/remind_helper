# keyboards/admin.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def admin_menu():
    """Главное меню админа"""
    buttons = [
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="👥 Список пользователей")],
        [KeyboardButton(text="📨 Рассылка")],
        [KeyboardButton(text="📈 Активность за день")],
        [KeyboardButton(text="⬅️ Назад в меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def user_list_keyboard(users, page=0):
    """Клавиатура для списка пользователей (с пагинацией)"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    # Добавляем кнопки для каждого пользователя на странице
    for user in users:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"👤 {user.username or user.first_name or str(user.telegram_id)}",
                callback_data=f"user_{user.telegram_id}"
            )
        ])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"users_page_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(text=f"Стр. {page+1}", callback_data="ignore"))
    nav_buttons.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"users_page_{page+1}"))
    keyboard.inline_keyboard.append(nav_buttons)
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="❌ Закрыть", callback_data="close_users")
    ])
    
    return keyboard

def user_actions_keyboard(user_id, is_banned):
    """Клавиатура для действий с пользователем"""
    ban_text = "🔓 Разбанить" if is_banned else "🔒 Забанить"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data=f"user_stats_{user_id}"),
            InlineKeyboardButton(text=ban_text, callback_data=f"ban_{user_id}")
        ],
        [
            InlineKeyboardButton(text="📨 Отправить сообщение", callback_data=f"msg_{user_id}"),
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_users")
        ]
    ])
    return keyboard