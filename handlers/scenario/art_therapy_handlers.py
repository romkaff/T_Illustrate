import os

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup

from strings import art_therapy_string
from kbds.inline import get_art_therapy_keyboard
from database.orm_query import (
    orm_add_user,
    orm_get_user,
    orm_set_user_specified_name
)


art_therapy_router = Router()

bot_admins = os.getenv('BOT_ADMINS')

@art_therapy_router.callback_query(F.data == 'service_art_therapy')
async def service_art_therapy(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(art_therapy_string.ART_THERAPY_START, reply_markup=get_art_therapy_keyboard())


@art_therapy_router.callback_query(F.data == 'art_therapy_group')
async def art_therapy_group(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer();
    await callback.message.answer('В разработке. Задайте вопрос если хотите узнать подробнее', reply_markup=get_art_therapy_keyboard())


@art_therapy_router.callback_query(F.data == 'art_therapy_individual')
async def art_therapy_individual(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer();
    await callback.message.answer('В разработке. Задайте вопрос если хотите узнать подробнее', reply_markup=get_art_therapy_keyboard()) 