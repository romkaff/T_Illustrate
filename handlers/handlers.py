import os

from aiogram import Router, types, F

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from strings import general_string
from kbds.inline import get_start_keyboard


handlers_router = Router()

bot_admins = os.getenv('BOT_ADMINS')


@handlers_router.message(F.text)
async def any(message: types.Message):
    await message.answer('Прошу прощения, я не разговариваю на отвлеченные темы')  


@handlers_router.message(F.photo)
async def any(message: types.Message):
    await message.answer('Я не знаю, что делать с присланным фото. Но оно мне нравится!') 