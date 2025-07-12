from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import IsAdmin
from kbds.inline import get_callback_btns, get_adminka_keyboard

from database.orm_query import (
    orm_get_inv_templates,
    orm_add_inv_template,
    orm_del_inv_template,
    orm_prev_inv_template,
    orm_next_inv_template,
    orm_get_poftfolio_all,
    orm_add_scetch,
    orm_del_scetch,
    orm_prev_scetch,
    orm_next_scetch
)


admin_router = Router()
admin_router.message.filter(IsAdmin())


class InvTemplate(StatesGroup):
    description=State()
    image=State()

    curr_template = None

class Portfolio(StatesGroup):
    description=State()
    image=State()

    curr_scetch = None


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


'''
    ############################################################################################################
    ########################   Заказы Мероприятий   ############################################################
    ############################################################################################################
'''










'''
    ############################################################################################################
    ########################   Приглашения - заказы   ##########################################################
    ############################################################################################################
'''

@admin_router.callback_query(F.data == 'admin_invite_orders')
async def admin_invite_orders(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    # 111




'''
    ############################################################################################################
    ########################   Приглашения - шаблоны   #########################################################
    ############################################################################################################
'''

# Просмотр в листалке шаблонов приглашений
@admin_router.callback_query(F.data == 'admin_invite_templates')
async def do_inv_templates(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    await admin_templates_show(callback.message, session)


# Кнопка - На главную
@admin_router.callback_query(F.data == 'admin_on_main')
async def admin_on_main(callback: types.CallbackQuery):
    await callback.answer()
    await start_admin(callback.message)


# Кнопка - Предыдущий шаблон
@admin_router.callback_query(F.data == 'admin_prev_template')
async def admin_prev_template(callback: types.CallbackQuery, session: AsyncSession):
    InvTemplate.curr_template = await orm_prev_inv_template(session, InvTemplate.curr_template.id)
 
    # если мы на первой картинке - надо получить последнюю
    if InvTemplate.curr_template == None:
        inv_templates = await orm_get_inv_templates(session)
        if len(inv_templates) > 0:
            InvTemplate.curr_template = inv_templates[-1]

    await admin_templates_show(callback.message, session)


# Кнопка - Следующий шаблон
@admin_router.callback_query(F.data == 'admin_next_template')
async def admin_next_template(callback: types.CallbackQuery, session: AsyncSession):
    InvTemplate.curr_template = await orm_next_inv_template(session, InvTemplate.curr_template.id)

    # если мы на последней картинке - надо получить первую
    if InvTemplate.curr_template == None:
        inv_templates = await orm_get_inv_templates(session)
        if len(inv_templates) > 0:
            InvTemplate.curr_template = inv_templates[0]

    await admin_templates_show(callback.message, session)


# Кнопка - Удалить шаблон
@admin_router.callback_query(F.data == 'admin_delete_template')
async def admin_delete_template(callback: types.CallbackQuery, session: AsyncSession):
    await orm_del_inv_template(session, InvTemplate.curr_template.id)
    await admin_prev_template(callback, session)
    await callback.answer()


# Кнопка - Добавить шаблон
@admin_router.callback_query(F.data == 'admin_add_template')
async def admin_add_template(callback: types.callback_query, session: AsyncSession, state: FSMContext): 
    await callback.message.answer('Добавьте картинку с описанием')
    await state.set_state(InvTemplate.image)


# Добавляем картинку шаблона
@admin_router.message(InvTemplate.image, F.photo)
async def admin_add_image(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.update_data(description=message.caption)
    
    data = await state.get_data()
    await orm_add_inv_template(session, data)

    await message.answer('Шаблон приглашения добавлен', reply_markup=get_adminka_keyboard())
    await state.clear()

    inv_templates = await orm_get_inv_templates(session)
    InvTemplate.curr_template = inv_templates[-1]
    await admin_templates_show(message, session)


# Процедура листалки шаблонов
async def admin_templates_show(message: types.Message, session: AsyncSession):
    inv_templates = await orm_get_inv_templates(session)

    if (InvTemplate.curr_template == None) and (len(inv_templates) > 0):
        InvTemplate.curr_template = inv_templates[0]

    match len(inv_templates):
        case 0:
            await message.answer('Здесь пока ничего нет', reply_markup=get_callback_btns(
                btns={
                    "Добавить":"admin_add_template",
                    "На главную":"admin_on_main",
                },
                sizes=(1, )
            ))

        case 1:
            try:
                await message.edit_media(media=types.InputMediaPhoto(media=InvTemplate.curr_template.image, caption=InvTemplate.curr_template.description), 
                                         reply_markup=get_callback_btns(
                    btns={
                        "Добавить":"admin_add_template",
                        "Удалить":"admin_delete_template",
                        "На главную":"admin_on_main",                    
                    }
                ))
            except:
                await message.answer_photo(InvTemplate.curr_template.image, InvTemplate.curr_template.description, reply_markup=get_callback_btns(
                    btns={
                        "Добавить":"admin_add_template",
                        "Удалить":"admin_delete_template",
                        "На главную":"admin_on_main",                    
                    }
                ))

        case _:
            try:
                await message.edit_media(media=types.InputMediaPhoto(media=InvTemplate.curr_template.image, caption=InvTemplate.curr_template.description), 
                                         reply_markup=get_callback_btns(
                    btns={
                        "Пред":"admin_prev_template",
                        "След":"admin_next_template",
                        "Добавить":"admin_add_template",
                        "Удалить":"admin_delete_template",
                        "На главную":"admin_on_main",                    
                    }
                ))
            except:
                await message.answer_photo(InvTemplate.curr_template.image, InvTemplate.curr_template.description, reply_markup=get_callback_btns(
                    btns={
                        "Пред":"admin_prev_template",
                        "След":"admin_next_template",
                        "Добавить":"admin_add_template",
                        "Удалить":"admin_delete_template",
                        "На главную":"admin_on_main",                    
                    }
                ))


'''
    ############################################################################################################
    ########################   Мое портфолио   #################################################################
    ############################################################################################################
'''                

# Просмотр в листалке портфолио
@admin_router.callback_query(F.data == 'admin_poftfolio')
async def admin_poftfolio(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    await admin_poftfolio_show(callback.message, session)


# Процедура листалки в портфолио
async def admin_poftfolio_show(message: types.Message, session: AsyncSession):
    poftfolios = await orm_get_poftfolio_all(session)

    if (Portfolio.curr_scetch == None) and (len(poftfolios) > 0):
        Portfolio.curr_scetch = poftfolios[0]

    match len(poftfolios):
        case 0:
            await message.answer('В портфолио пока ничего нет', reply_markup=get_callback_btns(
                btns={
                    "Добавить":"admin_add_scetch",
                    "На главную":"admin_on_main",
                },
                sizes=(1, )
            ))

        case 1:
            try:
                await message.edit_media(media=types.InputMediaPhoto(media=Portfolio.curr_scetch.image, caption=Portfolio.curr_scetch.description), 
                                         reply_markup=get_callback_btns(
                    btns={
                        "Добавить":"admin_add_scetch",
                        "Удалить":"admin_delete_scetch",
                        "На главную":"admin_on_main",                    
                    }
                ))
            except:
                await message.answer_photo(Portfolio.curr_scetch.image, Portfolio.curr_scetch.description, reply_markup=get_callback_btns(
                    btns={
                        "Добавить":"admin_add_scetch",
                        "Удалить":"admin_delete_scetch",
                        "На главную":"admin_on_main",                    
                    }
                ))

        case _:
            try:
                await message.edit_media(media=types.InputMediaPhoto(media=Portfolio.curr_scetch.image, caption=Portfolio.curr_scetch.description), 
                                         reply_markup=get_callback_btns(
                    btns={
                        "Пред":"admin_prev_scetch",
                        "След":"admin_next_scetch",
                        "Добавить":"admin_add_scetch",
                        "Удалить":"admin_delete_scetch",
                        "На главную":"admin_on_main",                    
                    }
                ))
            except:
                await message.answer_photo(Portfolio.curr_scetch.image, Portfolio.curr_scetch.description, reply_markup=get_callback_btns(
                    btns={
                        "Пред":"admin_prev_scetch",
                        "След":"admin_next_scetch",
                        "Добавить":"admin_add_scetch",
                        "Удалить":"admin_delete_scetch",
                        "На главную":"admin_on_main",                    
                    }
                ))


# Кнопка - Предыдущий скетч
@admin_router.callback_query(F.data == 'admin_prev_scetch')
async def admin_prev_scetch(callback: types.CallbackQuery, session: AsyncSession):
    Portfolio.curr_scetch = await orm_prev_scetch(session, Portfolio.curr_scetch.id)
 
    # если мы на первой картинке - надо получить последнюю
    if Portfolio.curr_scetch == None:
        poftfolios = await orm_get_poftfolio_all(session)
        if len(poftfolios) > 0:
            Portfolio.curr_scetch = poftfolios[-1]

    await admin_poftfolio_show(callback.message, session)


# Кнопка - Следующий шаблон
@admin_router.callback_query(F.data == 'admin_next_scetch')
async def admin_next_scetch(callback: types.CallbackQuery, session: AsyncSession):
    Portfolio.curr_scetch = await orm_next_scetch(session, Portfolio.curr_scetch.id)

    # если мы на последней картинке - надо получить первую
    if Portfolio.curr_scetch == None:
        poftfolios = await orm_get_poftfolio_all(session)
        if len(poftfolios) > 0:
            Portfolio.curr_scetch = poftfolios[0]

    await admin_poftfolio_show(callback.message, session) 


# Кнопка - Удалить скетч
@admin_router.callback_query(F.data == 'admin_delete_scetch')
async def admin_delete_scetch(callback: types.CallbackQuery, session: AsyncSession):
    await orm_del_scetch(session, Portfolio.curr_scetch.id)
    await admin_prev_scetch(callback, session)
    await callback.answer()


# Кнопка - Добавить скетч
@admin_router.callback_query(F.data == 'admin_add_scetch')
async def admin_add_scetch(callback: types.callback_query, session: AsyncSession, state: FSMContext): 
    await callback.message.answer('Добавьте картинку с описанием')
    await state.set_state(Portfolio.image)


# Добавляем скетч
@admin_router.message(Portfolio.image, F.photo)
async def admin_add_scetch_image(message: types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.update_data(description=message.caption)
    
    data = await state.get_data()
    await orm_add_scetch(session, data)

    await message.answer('Новый скетч добавлен в ваше портфолио', reply_markup=get_adminka_keyboard())
    await state.clear()

    poftfolios = await orm_get_poftfolio_all(session)
    Portfolio.curr_scetch = poftfolios[-1]
    await admin_poftfolio_show(message, session)    