import os

from aiogram import Router, types, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from kbds.inline import get_callback_btns
from strings import invite_string
from handlers.handlers import command_start

from database.orm_query import (
    orm_get_inv_templates,
    orm_prev_inv_template,
    orm_next_inv_template,
    orm_add_invitation_order,
    orm_add_user,
    orm_add_payment,
    orm_get_inv_orders
)


invite_router = Router()


class InviteOrder(StatesGroup):
    user_id=State()
    personal=State()
    finish_type=State()
    template_type=State()
    quantity=State()
    preliminary_price=State() 
    addressing=State()
    text_invitation=State()
    self_template_description=State()
    inv_template_id=State()
    contact_wish_addressing=State()
    wish_date=State()
    confirmed=State()
    final_price=State()
    payment=State()

    person_qty = 0
    created_order_id = 0

    user={}


class Payment(StatesGroup):
    amount=State()


class InvTemplate(StatesGroup):
    description=State()
    image=State()

    curr_template = None


class AskQuestion(StatesGroup):
    ask_question=State()


channel_id = os.getenv('CHANNEL_ADMIN_ID')
pay_to_phone_num = os.getenv('PAY_TO_PHONE_NUM')


@invite_router.callback_query(F.data == 'start_invites')
async def start_invites(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    inv_orders = await orm_get_inv_orders(session, callback.from_user.id)

    match len(inv_orders):
        case 0:
            await callback.message.answer(invite_string.INV_WELCOME + invite_string.INV_PERSONAL, reply_markup=get_callback_btns(
                        btns={
                            "Именные":"personal",
                            "Неименные":"no_personal",
                        },
                        sizes=(2, )
                    ))

        case _:
            await callback.message.answer(invite_string.INV_CHOOSE, reply_markup=get_callback_btns(
                        btns={
                            "Новый заказ":"new_inv_order",
                            "Оплатить":"pay_order",
                        },
                        sizes=(2, )
                    ))            


@invite_router.callback_query(F.data == 'pay_order')
async def pay_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    payment_text = (
        f'Номер вашего заказа: <strong>НОМЕР ЗАКАЗА</strong>\n'
        f'Вам нужно оплатить <strong>ХХХ рублей</strong>\n'
        f'переводом по номеру телефона <strong>{pay_to_phone_num}</strong> в один из банков:\n'
        '- Т-Банк\n'
        '- Сбер\n'
        '- АльфаБанк\n'
        'После того как оплата будет выполнена сохраните чек об оплате из приложения банка '
        'и отправьте его следующим сообщением'
    )

    await callback.message.answer(payment_text)
    await state.set_state(InviteOrder.payment)


@invite_router.callback_query(F.data == 'new_inv_order')
async def new_inv_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(invite_string.INV_WELCOME + invite_string.INV_PERSONAL, reply_markup=get_callback_btns(
                btns={
                    "Именные":"personal",
                    "Неименные":"no_personal",
                },
                sizes=(2, )
            ))
    await state.set_state(InviteOrder.personal)


@invite_router.callback_query(F.data == 'personal')
async def add_inv_personal(callback: types.callback_query, state: FSMContext):
    await state.update_data(personal='Именные')
    await callback.answer()
    await callback.message.answer(invite_string.INV_FINISH_TYPE, reply_markup=get_callback_btns(
                btns={
                    "Цифровые":"digital",
                    "Распечатанные":"printed",
                },
                sizes=(2, )
            ))    
    await state.set_state(InviteOrder.finish_type)


@invite_router.callback_query(F.data == 'no_personal')
async def add_inv_personal(callback: types.callback_query, state: FSMContext):
    await state.update_data(personal='Неименные')
    await callback.answer()
    await callback.message.answer(invite_string.INV_FINISH_TYPE, reply_markup=get_callback_btns(
                btns={
                    "Цифровые":"digital",
                    "Распечатанные":"printed",
                },
                sizes=(2, )
            ))    
    await state.set_state(InviteOrder.finish_type)


@invite_router.callback_query(F.data == 'digital')
async def add_inv_finish_type(callback: types.callback_query, state: FSMContext):
    await state.update_data(finish_type='Цифровые')
    await callback.answer()
    await callback.message.answer(invite_string.INV_TEMPLATE_TYPE, reply_markup=get_callback_btns(
                btns={
                    "Готовый":"template_ready",
                    "Свой":"template_self",
                },
                sizes=(2, )
            ))         
    await state.set_state(InviteOrder.template_type)


@invite_router.callback_query(F.data == 'printed')
async def add_inv_finish_type(callback: types.callback_query, state: FSMContext):
    await state.update_data(finish_type='Распечатанные')
    await callback.answer()
    await callback.message.answer(invite_string.INV_TEMPLATE_TYPE, reply_markup=get_callback_btns(
                btns={
                    "Готовый":"template_ready",
                    "Свой":"template_self",
                },
                sizes=(2, )
            ))      
    await state.set_state(InviteOrder.template_type)


@invite_router.callback_query(F.data == 'template_ready')
async def add_inv_template_type(callback: types.callback_query, state: FSMContext):
    await state.update_data(template_type='Готовый')
    await callback.answer()
    await callback.message.answer(invite_string.INV_QUANTITY)     
    await state.set_state(InviteOrder.quantity)


@invite_router.callback_query(F.data == 'template_self')
async def add_inv_template_type(callback: types.callback_query, state: FSMContext):
    await state.update_data(template_type='Свой')
    await state.update_data(inv_template_id=0)
    await callback.answer()
    await callback.message.answer(invite_string.INV_QUANTITY)     
    await state.set_state(InviteOrder.quantity)


@invite_router.message(InviteOrder.quantity, F.text)
async def add_inv_quantity(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.from_user.id)

    InviteOrder.user["user_id"]=message.from_user.id
    InviteOrder.user["first_name"]=message.from_user.first_name
    InviteOrder.user["last_name"]=message.from_user.last_name

    await state.update_data(quantity=message.text)
    await message.answer(invite_string.INV_NEXT_ACTIONS, reply_markup=get_callback_btns(
                btns={
                    "Предварительный расчет стоимости":"calc_price",
                    "Отмена":"cancel",
                },
                sizes=(1, )
            ))


@invite_router.callback_query(F.data == 'calc_price')
async def calc_price(callback: types.callback_query, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    InviteOrder.preliminary_price = calc_preliminary_price()
    preliminary_text = (
        'Вы выбрали:\n'
        f'Вариант приглашения: <strong>{str(data["personal"])}</strong>\n'
        f'Изготовление: <strong>{str(data["finish_type"])}</strong>\n'
        f'Вид шаблона: <strong>{str(data["template_type"])}</strong>\n'
        f'Количество: <strong>{str(data["quantity"])}</strong>\n'
        f'Предварительная стоимость: <strong>{float(InviteOrder.preliminary_price)}</strong>'
    )

    await callback.message.answer(preliminary_text, reply_markup=get_callback_btns(
                btns={
                    "Продолжить":"inv_next",
                    "Отмена":"cancel",
                },
                sizes=(1, )
            ))


@invite_router.callback_query(F.data == 'cancel')
async def cancel(callback: types.callback_query, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        ('Отменено\n'
         'Начните сначала, если хотите изменить параметры заказа'))


@invite_router.callback_query(F.data == 'inv_next')
async def inv_next(callback: types.callback_query, state: FSMContext, session: AsyncSession):
    await state.update_data(preliminary_price=InviteOrder.preliminary_price)
    data = await state.get_data()

    match data['template_type']:
        case 'Готовый':
            await callback.answer()
            await callback.message.answer(invite_string.INV_TEMPLATE)
            await invite_templates_show(callback.message, session)
            await state.set_state(InviteOrder.inv_template_id)
        case 'Свой':
            await callback.answer()
            await callback.message.answer(invite_string.INV_SELF_TEMPLATE)
            await state.set_state(InviteOrder.self_template_description)


async def invite_templates_show(message: types.Message, session: AsyncSession):
    inv_templates = await orm_get_inv_templates(session)

    if (InvTemplate.curr_template == None) and (len(inv_templates) > 0):
        InvTemplate.curr_template = inv_templates[0]

    match len(inv_templates):
        case 0:
            await message.answer('Загруженных шаблонов приглашений не найдено', reply_markup=get_callback_btns(
                    btns={
                        "Свой вариант":"self_template_type",
                        "Отмена":"cancel",
                    }
                ))
        case 1:
            try:
                await message.edit_media(media=types.InputMediaPhoto(media=InvTemplate.curr_template.image, caption=InvTemplate.curr_template.description), 
                                         reply_markup=get_callback_btns(
                    btns={
                        "Выбрать":"template_select",
                        "Отмена":"cancel",
                        "Свой вариант":"self_template_type",
                    }
                ))
            except:
                await message.answer_photo(InvTemplate.curr_template.image, InvTemplate.curr_template.description, reply_markup=get_callback_btns(
                    btns={
                        "Выбрать":"template_select",
                        "Отмена":"cancel",
                        "Свой вариант":"self_template_type",
                    }
                ))

        case _:
            try:
                await message.edit_media(media=types.InputMediaPhoto(media=InvTemplate.curr_template.image, caption=InvTemplate.curr_template.description), 
                                         reply_markup=get_callback_btns(
                    btns={
                        "Пред":"prev_template",
                        "След":"next_template",
                        "Выбрать":"template_select",
                        "Отмена":"cancel",
                        "Свой вариант":"self_template_type",                 
                    }
                ))
            except:
                await message.answer_photo(InvTemplate.curr_template.image, InvTemplate.curr_template.description, reply_markup=get_callback_btns(
                    btns={
                        "Пред":"prev_template",
                        "След":"next_template",
                        "Выбрать":"template_select",
                        "Отмена":"cancel",
                        "Свой вариант":"self_template_type",                    
                    }
                ))


# Предыдущий
@invite_router.callback_query(F.data == 'prev_template')
async def prev_template(callback: types.CallbackQuery, session: AsyncSession):
    InvTemplate.curr_template = await orm_prev_inv_template(session, InvTemplate.curr_template.id)
 
    # если мы на первой картинке - надо получить последнюю
    if InvTemplate.curr_template == None:
        inv_templates = await orm_get_inv_templates(session)
        if len(inv_templates) > 0:
            InvTemplate.curr_template = inv_templates[-1]

    await invite_templates_show(callback.message, session)


# Следующий
@invite_router.callback_query(F.data == 'next_template')
async def next_template(callback: types.CallbackQuery, session: AsyncSession):
    InvTemplate.curr_template = await orm_next_inv_template(session, InvTemplate.curr_template.id)

    # если мы на последней картинке - надо получить первую
    if InvTemplate.curr_template == None:
        inv_templates = await orm_get_inv_templates(session)
        if len(inv_templates) > 0:
            InvTemplate.curr_template = inv_templates[0]

    await invite_templates_show(callback.message, session)


@invite_router.callback_query(F.data == 'template_select')
async def add_template_id(callback: types.callback_query, state: FSMContext):
    await state.update_data(inv_template_id=InvTemplate.curr_template.id)
    await callback.answer()

    data = await state.get_data()

    match data['personal']:
        case 'Именные':
            await callback.message.answer(invite_string.INV_ADDRESSING_PERSONAL)
        case 'Неименные':
            await callback.message.answer(invite_string.INV_ADDRESSING_UNPERSONAL)

    await state.set_state(InviteOrder.addressing)


@invite_router.callback_query(F.data == 'self_template_type')
async def add_template_id(callback: types.callback_query, state: FSMContext):
    await state.update_data(template_type='Свой')
    await callback.answer()
    InviteOrder.price = calc_price()
    data = await state.get_data()
    
    change_condition_text = (
        'Внимание!\n'
        'Вы выбрали свой вариант вместо готового шаблона, а это параметр, влияющий на стоимость.\n\n'
        f'Вариант приглашения: <strong>{str(data["personal"])}</strong>\n'
        f'Изготовление: <strong>{str(data["finish_type"])}</strong>\n'
        f'Вид шаблона: <strong>{str(data["template_type"])}</strong>\n'
        f'Количество: <strong>{str(data["quantity"])}</strong>\n'
        f'Новая рассчитанная стоимость:: <strong>{float(InviteOrder.price)}</strong>'
    )

    await callback.message.answer(change_condition_text, reply_markup=get_callback_btns(
                btns={
                    "Продолжить":"inv_next",
                    "Отмена":"cancel",
                },
                sizes=(1, )
            ))



@invite_router.message(InviteOrder.self_template_description, F.text)
async def add_inv_self_template_description(message: types.Message, state: FSMContext):
    await state.update_data(self_template_description=message.text)
    
    data = await state.get_data()

    match data['personal']:
        case 'Именные':
            await message.answer(invite_string.INV_ADDRESSING_PERSONAL)
        case 'Неименные':
            await message.answer(invite_string.INV_ADDRESSING_UNPERSONAL)
    
    await state.set_state(InviteOrder.addressing)


@invite_router.message(InviteOrder.addressing, F.text)
async def add_inv_addressing(message: types.Message, state: FSMContext):
    await state.update_data(addressing=message.text)
    data = await state.get_data()

    if data['personal'] == 'Именные':
        personal_addressing = message.text

        person_qty = len(personal_addressing.split('~'))
        InviteOrder.person_qty = person_qty
        quantity = data['quantity']

        if person_qty != int(quantity):
            diff_qty_text = (
                'Внимание!\n'
                'Вы выбрали вариант с именными приглашениями. '
                f'Но количество приглашений, которое вы указали (<strong>{quantity}</strong>) '
                f'отличается от количества адресатов (<strong>{str(person_qty)}</strong>)\n\n'
                f'Выберите один из вариантов'
            )

            await message.answer(diff_qty_text, reply_markup=get_callback_btns(
                        btns={
                            "Количество приглашений = количеству адресатов":"quantity_eq_person",
                            "Изменить список адресатов":"change_person_list",
                            "Отмена":"cancel",
                        },
                        sizes=(1, )
                    ))  
        else:
            await message.answer(invite_string.INV_TEXT)
            await state.set_state(InviteOrder.text_invitation)
    else:
        await message.answer(invite_string.INV_TEXT)
        await state.set_state(InviteOrder.text_invitation)    


@invite_router.callback_query(F.data == 'quantity_eq_person')
async def quantity_eq_person(callback: types.callback_query, state: FSMContext):
    await state.update_data(quantity=InviteOrder.person_qty)
    await callback.answer()
    await callback.message.answer(f'Количество приглашений изменено на <strong>{int(InviteOrder.person_qty)}</strong>', reply_markup=get_callback_btns(
                btns={
                    "Продолжить":"confirm_quantity",
                    "Отмена":"cancel",
                },
                sizes=(2, )
            ))    


@invite_router.callback_query(F.data == 'change_person_list')
async def change_person_list(callback: types.callback_query, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    await callback.message.answer(
        f'Список получателей сейчас такой: {data["addressing"]}\n\n'
        'Вы хотите изменить его?', reply_markup=get_callback_btns(
                btns={
                    "Продолжить":"do_change_person",
                    "Отмена":"cancel",
                },
                sizes=(2, )
            )  
    )


@invite_router.callback_query(F.data == 'do_change_person')
async def do_change_person(callback: types.callback_query, state: FSMContext):
    await callback.answer()
    await callback.message.answer(invite_string.INV_ADDRESSING_PERSONAL)
    await state.set_state(InviteOrder.addressing) 


@invite_router.callback_query(F.data == 'confirm_quantity')
async def confirm_quantity(callback: types.callback_query, state: FSMContext):
    await callback.answer()
    await callback.message.answer(invite_string.INV_TEXT)
    await state.set_state(InviteOrder.text_invitation) 


@invite_router.message(InviteOrder.text_invitation, F.text)
async def add_inv_text_invitation(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(text_invitation=message.text)
    await message.answer(invite_string.INV_CONTACT_WISH_ADDRESSING)
    await state.set_state(InviteOrder.contact_wish_addressing)


@invite_router.message(InviteOrder.contact_wish_addressing, F.text)
async def add_contact_wish_addressing(message: types.Message, state: FSMContext):
    await state.update_data(contact_wish_addressing=message.text)
    await message.answer(invite_string.INV_WISH_DATE)
    await state.set_state(InviteOrder.wish_date)


@invite_router.message(InviteOrder.wish_date, F.text)
async def add_inv_wish_date(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(wish_date=message.text)
    await message.answer(invite_string.INV_NEXT_ACTIONS, reply_markup=get_callback_btns(
                btns={
                    "Продолжить заказ":"create_order",
                    "Рассчитать с другими параметрами":"new_calc",
                    "Задать вопрос":"ask_question",
                },
                sizes=(1, )
            ))
    await state.set_state(InviteOrder.confirmed)
   

@invite_router.callback_query(F.data == 'new_calc')
async def new_calc(callback: types.callback_query, state: FSMContext):
    await callback.answer()
    await state.clear()
    start_invites(callback.message, state)


@invite_router.callback_query(F.data == 'ask_question')
async def ask_question(callback: types.callback_query, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer('Задайте свой вопрос, он будет отправлен автору канала')
    await state.set_state(AskQuestion.ask_question)


@invite_router.message(AskQuestion.ask_question)
async def forward_question(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    print(f'АЙДИШНИК ХОЗЯИНА КАНАЛА - {channel_id}, АЙДИШНИК ОТ КОГО - {bot.id}, АЙДИ МЕССАГИ - {message.message_id}')

    # await bot.forward_message(channel_id, bot.id, message.message_id, message.forward_from_message_id)
    await bot.send_message(channel_id, message.text)
    await message.answer('Ваш вопрос отправлен')


@invite_router.callback_query(F.data == 'create_order')
async def create_order(callback: types.callback_query, state: FSMContext):
    final_price=calc_final_price()

    await state.update_data(final_price=final_price)
    
    data = await state.get_data()

    final_text = (
        'Вы выбрали:\n'
        f'Вариант приглашения: <strong>{str(data["personal"])}</strong>\n'
        f'Изготовление: <strong>{str(data["finish_type"])}</strong>\n'
        f'Вид шаблона: <strong>{str(data["template_type"])}</strong>\n'
        f'Количество: <strong>{int(data["quantity"])}</strong>\n'
        f'Предварительная стоимость: <strong>{float(data["final_price"])}</strong>'
    )

    await callback.message.answer(final_text, reply_markup=get_callback_btns(
                btns={
                    "Продолжить":"final_next",
                    "Отмена":"cancel",
                },
                sizes=(1, )
            ))


@invite_router.callback_query(F.data == 'final_next')
async def final_next(callback: types.callback_query, state: FSMContext, session: AsyncSession):
    await state.update_data(confirmed=True)
    await callback.answer()
    
    data = await state.get_data()
    order_id = await orm_add_invitation_order(session, data)
    await orm_add_user(session, InviteOrder.user)

    InviteOrder.created_order_id = order_id
    final_price = data['final_price']
    payment_text = (
        f'Номер вашего заказа: <strong>{order_id}</strong>\n'
        f'Вам нужно оплатить <strong>{final_price} рублей</strong>\n'
        f'переводом по номеру телефона <strong>{pay_to_phone_num}</strong> в один из банков:\n'
        '- Т-Банк\n'
        '- Сбер\n'
        '- АльфаБанк\n'
        'После того как оплата будет выполнена сохраните чек об оплате из приложения банка '
        'и отправьте его следующим сообщением'
    )

    await callback.message.answer(payment_text)
    await state.set_state(InviteOrder.payment)


@invite_router.message(InviteOrder.payment, F.photo)
async def send_payment_photo(message: types.Message, bot: Bot, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    data["order_id"] = InviteOrder.created_order_id
    data["amount"] = data["final_price"]
    data["check_image"] = message.photo[-1].file_id
    await orm_add_payment(session, data)
    await message.answer('Оплата по заказу принята! По готовности с вами свяжутся! Спасибо!')
    await state.clear()
    await command_start(message)


def calc_preliminary_price() -> float:
    return(555)


def calc_final_price() -> float:
    return(777)














@invite_router.message(F.text == 'test')
async def test(message: types.Message, state: FSMContext, session: AsyncSession):
    i: float
    k: float
    i = 10
    k = 5
    if i != k:
        message.answer('Ok')


@invite_router.message(F.text == 'Myid')
async def my_id(message: types.Message):
    await message.answer(str(message.from_user.id)) 