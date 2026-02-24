from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from kbds.inline import get_callback_btns, get_services_keyboard
from strings import services_string


service_router = Router()


@service_router.callback_query(F.data == 'start_services')
async def start_services(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(services_string.S_WELCOME, reply_markup=get_services_keyboard())
