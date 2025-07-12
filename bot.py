import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from middlewares.db import DataBaseSession
from database.engine import create_db, drop_db, session_maker

from handlers.handlers import handlers_router
from handlers.scenario.admin_handlers import admin_router
from handlers.scenario.invite_handlers import invite_router
from handlers.scenario.event_handlers import event_router


# Инициализируем бота и подключаем роутеры
bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(admin_router)
dp.include_router(invite_router)
dp.include_router(event_router)
dp.include_router(handlers_router)


async def on_startup(bot):
    # await drop_db()
    await create_db()


async def on_shutdown(bot):
    print('бот лег')


# Старт бота и программное формирование меню
async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())