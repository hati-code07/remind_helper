import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import WebhookInfo
from fastapi import FastAPI, Request
import uvicorn


app = FastAPI()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

from handlers.start import router as start_router
from handlers.tasks import router as tasks_router
from handlers.schedule import router as schedule_router
from handlers.admin import router as admin_router


load_dotenv()
from database.db import engine
from models.user import User
from models.task import Task
from models.schedule import Schedule
from database.base import Base


from utils.scheduler import scheduler
from utils.commands import set_commands
from utils.check_deadlines import check_missed_deadlines


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


if __name__ == "__main__":
    asyncio.run(main())