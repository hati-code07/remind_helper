from aiogram.types import BotCommand


async def set_commands(bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="add_task", description="Добавить задачу"),
        BotCommand(command="tasks", description="Список задач"),
    ]

    await bot.set_my_commands(commands)