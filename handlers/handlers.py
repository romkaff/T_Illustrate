import os

from aiogram import Router, types, F
from aiogram.filters import CommandStart

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from strings import general_string
from kbds.inline import get_start_keyboard


handlers_router = Router()

bot_admins = os.getenv('BOT_ADMIN')


@handlers_router.message(CommandStart)
async def command_start(message: types.Message, back_from: bool = False):
    if back_from:
        is_admin = str(message.chat.id) in bot_admins
    else:
        is_admin = str(message.from_user.id) in bot_admins

    await message.answer(general_string.START_CMD, reply_markup=get_start_keyboard(is_admin))


@handlers_router.message(F.text)
async def any(message: types.Message):
    await message.answer('Прошу прощения, я не разговариваю на отвлеченные темы')  


@handlers_router.message(F.photo)
async def any(message: types.Message):
    await message.answer('Я не знаю, что делать с присланным фото. Но оно мне нравится!')     