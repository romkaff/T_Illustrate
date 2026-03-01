import os

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup

from strings import acquaintance_string
from strings import general_string
from kbds.inline import get_start_keyboard
from database.orm_query import (
    orm_add_user,
    orm_get_user,
    orm_set_user_specified_name
)


acquaintance_router = Router()

bot_admins = os.getenv('BOT_ADMINS')


class AcquaintanceStates(StatesGroup):
    waiting_for_specified_name = State()
    is_admin: None


@acquaintance_router.message(F.text, AcquaintanceStates.waiting_for_specified_name)
async def handle_name(message: types.Message, state: FSMContext, session: AsyncSession):
    user = await orm_set_user_specified_name(session, message.from_user.id, message.text.strip())
    await state.clear()
    await message.answer(f"Привет, {user.specified_name}!\n\n{general_string.START_CMD}", reply_markup=get_start_keyboard(AcquaintanceStates.is_admin))


@acquaintance_router.message(Command("start"))
async def command_start(message: types.Message, state: FSMContext, session: AsyncSession, back_from: bool = False):
    await command_start_handle(message, state, session, back_from)


@acquaintance_router.message(CommandStart)
async def command_start(message: types.Message, state: FSMContext, session: AsyncSession, back_from: bool = False):
    await command_start_handle(message, state, session, back_from)


async def command_start_handle(message: types.Message, state: FSMContext, session: AsyncSession, back_from: bool = False):
    data = {}
    data["user_id"] = message.from_user.id
    data["user_first_name"] = message.from_user.first_name
    data["user_last_name"] = message.from_user.last_name
    data["name"] = message.from_user.full_name

    await orm_add_user(session, data)

    if back_from:
        is_admin = str(message.chat.id) in bot_admins
    else:
        is_admin = str(message.from_user.id) in bot_admins

    AcquaintanceStates.is_admin = is_admin
    user = await orm_get_user(session, message.from_user.id)

    if not user.specified_name:
        await state.set_state(AcquaintanceStates.waiting_for_specified_name)
        await message.answer(acquaintance_string.MEET_START)
    else:
        await message.answer(f"Привет, {user.specified_name}!\n\n{general_string.START_CMD}", reply_markup=get_start_keyboard(AcquaintanceStates.is_admin))
