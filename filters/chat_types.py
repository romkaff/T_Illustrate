import os

from aiogram.filters import Filter, BaseFilter
from aiogram import Bot, types
from aiogram.types import Message

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


class ChatTypeFilter(Filter):
    
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types
    

class IsAdmin(Filter):

    def __init__(self) -> None:
        pass
    
    admins_id = os.getenv('BOT_ADMINS')

    async def __call__(self, message: Message) -> bool:
        return str(message.from_user.id) in self.admins_id