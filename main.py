import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import WebhookInfo
from aiogram.types import BotCommand
from flask import Flask
import threading


load_dotenv()

flask_app = Flask(__name__)

@flask_app.route('/')
def health_check():
    return "Bot is running!", 200

def run_flask():
    port = int(os.getenv('PORT', 10000))
    flask_app.run(host='0.0.0.0', port=port)



from handlers.start import router as start_router
from handlers.tasks import router as tasks_router
from handlers.schedule import router as schedule_router
from handlers.admin import router as admin_router

from database.db import engine
from models.user import User
from models.task import Task
from models.schedule import Schedule
from database.base import Base


from utils.scheduler import scheduler
from utils.commands import set_commands
from utils.check_deadlines import check_missed_deadlines


bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())


async def main():
    await create_tables()
    scheduler.start()
    await set_commands(bot)
    await check_missed_deadlines(bot)

    dp.include_router(start_router)
    dp.include_router(tasks_router)
    dp.include_router(schedule_router)
    dp.include_router(admin_router)
    

    print("Бот запущен 🚀")
    await dp.start_polling(bot)
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())