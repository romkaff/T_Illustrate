from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import IsAdmin
from kbds.inline import get_callback_btns, get_adminka_keyboard


admin_router = Router()
admin_router.message.filter(IsAdmin())


@admin_router.callback_query(F.data == 'start_adminka')
async def start_adminka(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'Привет, админ {callback.from_user.first_name}', reply_markup=get_adminka_keyboard())


@admin_router.message(Command('admin'))
async def start_admin(message: types.Message):
    await message.answer(f'Привет, админ {message.from_user.first_name}', reply_markup=get_adminka_keyboard())


@admin_router.message(F.text.lower() == 'admin' )
async def start_admin(message: types.Message):
    await message.answer(f'Привет, админ {message.from_user.first_name}', reply_markup=get_adminka_keyboard())