import os

from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from kbds.inline import get_callback_btns
from strings import event_string
from handlers.handlers import command_start

from database.orm_query import (
    orm_add_event_order,
    orm_get_poftfolio_all,
    orm_prev_scetch,
    orm_next_scetch
)

event_router = Router()


pay_to_phone_num = os.getenv('PAY_TO_PHONE_NUM')
pay_to_name = os.getenv('PAY_TO_NAME')


class EventOrder(StatesGroup):
    event_date=State()
    handing_type=State()
    execution_type=State()
    akva_brand=State()
    what_to_hand_over=State()
    guests_qty=State()
    hours_qty=State()
    no_time_reaction=State()
    event_place=State()
    need_agreement=State()
    amount=State()
    prepayment_made=State()

    msg: types.Message

    curr_scetch = None


@event_router.callback_query(F.data == 'start_events')
async def start_events(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    EventOrder.msg=callback.message
    await callback.message.answer(event_string.EVENT_WELCOME, reply_markup=get_callback_btns(
                btns={
                    "Заказать":"events_order",
                    "Цены":"events_price",
                    "Примеры работ":"events_portfolio",
                },
                sizes=(1, )
            ))


@event_router.callback_query(F.data == 'events_price')
async def events_price(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await callback.message.answer(get_price(), reply_markup=get_callback_btns(
                btns={
                    "Заказать":"events_order",
                    "Примеры работ":"events_portfolio",
                    "Назад":"events_back",
                },
                sizes=(1, )
            ))


@event_router.callback_query(F.data == 'events_back')
async def events_back(callback: types.CallbackQuery, state: FSMContext):
    await command_start(EventOrder.msg, True)


@event_router.callback_query(F.data == 'events_portfolio')
async def events_portfolio(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    await portfolio_show(callback.message, session)


async def portfolio_show(message: types.Message, session: AsyncSession):
    portfolios = await orm_get_poftfolio_all(session)

    if (EventOrder.curr_scetch == None) and (len(portfolios) > 0):
        EventOrder.curr_scetch = portfolios[0]

    match len(portfolios):
        case 0:
            await message.answer('Портфолио не заполнено', reply_markup=get_callback_btns(
                    btns={
                        "Назад":"events_back",
                    }
                ))
        case 1:
            try:
                await message.edit_media(media=types.InputMediaPhoto(media=EventOrder.curr_scetch.image, caption=EventOrder.curr_scetch.description), 
                                         reply_markup=get_callback_btns(
                    btns={
                        "Назад":"events_back",
                    }
                ))
            except:
                await message.answer_photo(EventOrder.curr_scetch.image, EventOrder.curr_scetch.description, reply_markup=get_callback_btns(
                    btns={
                        "Назад":"events_back",
                    }
                ))

        case _:
            try:
                await message.edit_media(media=types.InputMediaPhoto(media=EventOrder.curr_scetch.image, caption=EventOrder.curr_scetch.description), 
                                         reply_markup=get_callback_btns(
                    btns={
                        "Пред":"prev_scetch",
                        "След":"next_scetch",
                        "Назад":"events_back",                 
                    }
                ))
            except:
                await message.answer_photo(EventOrder.curr_scetch.image, EventOrder.curr_scetch.description, reply_markup=get_callback_btns(
                    btns={
                        "Пред":"prev_scetch",
                        "След":"next_scetch",
                        "Назад":"events_back",                      
                    }
                ))


# Предыдущий
@event_router.callback_query(F.data == 'prev_scetch')
async def prev_scetch(callback: types.CallbackQuery, session: AsyncSession):
    EventOrder.curr_scetch = await orm_prev_scetch(session, EventOrder.curr_scetch.id)
 
    # если мы на первой картинке - надо получить последнюю
    if EventOrder.curr_scetch == None:
        portfolios = await orm_get_poftfolio_all(session)
        if len(portfolios) > 0:
            EventOrder.curr_scetch = portfolios[-1]

    await portfolio_show(callback.message, session)


# Следующий
@event_router.callback_query(F.data == 'next_scetch')
async def next_scetch(callback: types.CallbackQuery, session: AsyncSession):
    EventOrder.curr_scetch = await orm_next_scetch(session, EventOrder.curr_scetch.id)

    # если мы на последней картинке - надо получить первую
    if EventOrder.curr_scetch == None:
        portfolios = await orm_get_poftfolio_all(session)
        if len(portfolios) > 0:
            EventOrder.curr_scetch = portfolios[0]

    await portfolio_show(callback.message, session)


@event_router.callback_query(F.data == 'events_order')
async def events_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()    
    await callback.message.answer(event_string.EVENT_DATE)
    await state.set_state(EventOrder.event_date)


@event_router.message(EventOrder.event_date)
async def event_date(message: types.Message, state: FSMContext):
    try:
        date = datetime.strptime(message.text, '%d.%m.%Y')
        await state.update_data(event_date=message.text)
        await message.answer(event_string.EVENT_HANDING_TYPE, reply_markup=get_callback_btns(
                    btns={
                        "На мероприятии":"on_event",
                        "Заранее к дате":"to_date",
                    },
                    sizes=(2, )
                ))
        await state.set_state(EventOrder.handing_type)
    except ValueError:
        await message.answer("Введите дату в формате ДД.ММ.ГГГГ")
        await state.set_state(EventOrder.event_date)


@event_router.callback_query(F.data == 'on_event')
async def events_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(handing_type='На мероприятии')   
    await callback.message.answer(event_string.EVENT_EXECUTION_TYPE, reply_markup=get_callback_btns(
                btns={
                    "Цифровые с печатью на А5":"a5",
                    "Акварель фэшн":"akva_fashion",
                    "Цифровые с печатью на А6":"a6",
                    "Акварель портреты":"akva_portrait",
                },
                sizes=(2, )
            ))
    await state.set_state(EventOrder.execution_type)


@event_router.callback_query(F.data == 'to_date')
async def events_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(handing_type='Заранее к дате')   
    await callback.message.answer(event_string.EVENT_EXECUTION_TYPE, reply_markup=get_callback_btns(
                btns={
                    "А5 Цифра с печатью":"a5",
                    "Акварель фэшн":"akva_fashion",
                    "А6 Цифра с печатью":"a6",
                    "Акварель портреты":"akva_portrait",
                },
                sizes=(2, )
            ))
    await state.set_state(EventOrder.execution_type)


@event_router.callback_query(F.data == 'a5')
async def a5(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(execution_type='А5 Цифра с печатью')     
    await callback.message.answer(event_string.EVENT_WHAT_TO_HAND_OVER, reply_markup=get_callback_btns(
                btns={
                    "Цветные конверты":"color_envelope",
                    "Крафтовые конверты":"craft",
                },
                sizes=(1, )
            ))
    await state.set_state(EventOrder.what_to_hand_over)    


@event_router.callback_query(F.data == 'a6')
async def a6(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(execution_type='А6 Цифра с печатью')     
    await callback.message.answer(event_string.EVENT_WHAT_TO_HAND_OVER_A6, reply_markup=get_callback_btns(
                btns={
                    "Цв. конверты":"color_envelope",
                    "Магн. рамки":"magnet_frame",
                    "Крафт":"craft",
                },
                sizes=(1, )
            ))
    await state.set_state(EventOrder.what_to_hand_over)


@event_router.callback_query(F.data == 'akva_fashion')
async def aakva_fashion(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(execution_type='Акварель фэшн')  
    await callback.message.answer(event_string.EVENT_AKVA_BRAND, reply_markup=get_callback_btns(
                btns={
                    "С брендированием":"with_brand",
                    "Без":"without_brand",
                },
                sizes=(1, )
            ))
    await state.set_state(EventOrder.akva_brand)     


@event_router.callback_query(F.data == 'akva_portrait')
async def akva_portrait(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(execution_type='Акварель портреты')  
    await callback.message.answer(event_string.EVENT_AKVA_BRAND, reply_markup=get_callback_btns(
                btns={
                    "С брендированием":"with_brand",
                    "Без":"without_brand",
                },
                sizes=(1, )
            ))
    await state.set_state(EventOrder.akva_brand) 


@event_router.callback_query(F.data == 'with_brand')
async def with_brand(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(akva_brand=True)  
    await callback.message.answer(event_string.EVENT_WHAT_TO_HAND_OVER, reply_markup=get_callback_btns(
                btns={
                    "Цветные конверты":"color_envelope",
                    "Крафтовые конверты":"craft",
                },
                sizes=(1, )
            ))
    await state.set_state(EventOrder.what_to_hand_over)     


@event_router.callback_query(F.data == 'without_brand')
async def with_brand(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(akva_brand=False)  
    await callback.message.answer(event_string.EVENT_WHAT_TO_HAND_OVER, reply_markup=get_callback_btns(
                btns={
                    "Цветные конверты":"color_envelope",
                    "Крафтовые конверты":"craft",
                },
                sizes=(1, )
            ))
    await state.set_state(EventOrder.what_to_hand_over)


@event_router.callback_query(F.data == 'color_envelope')
async def color_envelope(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(what_to_hand_over='Цветные конверты')  
    await callback.message.answer(event_string.EVENT_GUESTS_QTY)
    await state.set_state(EventOrder.guests_qty)         


@event_router.callback_query(F.data == 'craft')
async def craft(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(what_to_hand_over='Крафтовые конверты')  
    await callback.message.answer(event_string.EVENT_GUESTS_QTY)
    await state.set_state(EventOrder.guests_qty)      


@event_router.callback_query(F.data == 'magnet_frame')
async def craft(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(what_to_hand_over='Магнитная рамка')  
    await callback.message.answer(event_string.EVENT_GUESTS_QTY)
    await state.set_state(EventOrder.guests_qty)      


@event_router.message(EventOrder.guests_qty)
async def guests_qty(message: types.Message, state: FSMContext):
    await state.update_data(guests_qty=message.text)
    await message.answer(event_string.EVENT_HOURS_QTY)
    await state.set_state(EventOrder.hours_qty)


@event_router.message(EventOrder.hours_qty)
async def hours_qty(message: types.Message, state: FSMContext):
    await state.update_data(hours_qty=message.text)
    await message.answer(event_string.EVENT_NO_TIME_REACTION, reply_markup=get_callback_btns(
                btns={
                    "Продлеваем":"prolongate",
                    "Не рисуем":"no_prolongate",
                },
                sizes=(1, )
            ))
    await state.set_state(EventOrder.no_time_reaction)


@event_router.callback_query(F.data == 'prolongate')
async def prolongate(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(no_time_reaction='Продлеваем')  
    await callback.message.answer(event_string.EVENT_PLACE)
    await state.set_state(EventOrder.event_place)      


@event_router.callback_query(F.data == 'no_prolongate')
async def no_prolongate(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(no_time_reaction='Не рисуем')  
    await callback.message.answer(event_string.EVENT_PLACE)
    await state.set_state(EventOrder.event_place) 


@event_router.message(EventOrder.event_place)
async def event_place(message: types.Message, state: FSMContext):
    await state.update_data(event_place=message.text)
    await message.answer(event_string.EVENT_NEED_AGREEMENT, reply_markup=get_callback_btns(
                btns={
                    "Да":"need_agreement",
                    "Нет":"no_need_agreement",
                },
                sizes=(2, )
            ))
    await state.set_state(EventOrder.need_agreement)  


@event_router.callback_query(F.data == 'no_need_agreement')
async def no_need_agreement(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(need_agreement=False) 

    data = await state.get_data()
    amount = 999.99
    
    await callback.message.answer(get_final_text(data, amount), reply_markup=get_callback_btns(
                btns={
                    "Забронировать дату":"reserve_date",
                    "Изменить и перерасчитать":"recalc",
                    "Задать вопрос":"event_asc_question",
                },
                sizes=(1, )
            ))


@event_router.callback_query(F.data == 'need_agreement')
async def no_need_agreement(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await state.update_data(need_agreement=True) 

    data = await state.get_data()
    amount = 999.99
    
    await callback.message.answer(get_final_text(data, amount), reply_markup=get_callback_btns(
                btns={
                    "Забронировать дату":"reserve_date",
                    "Изменить и перерасчитать":"recalc",
                    "Задать вопрос":"event_asc_question",
                },
                sizes=(1, )
            ))


def get_final_text(data: dict, amount: float):
    final_text = (
        'Вы выбрали:\n'
        f'Дата мероприятия: <strong>{str(data['event_date'])}</strong>\n'
        f'Место: <strong>{str(data['event_place'])}</strong>\n'
        f'Вариант вручения: <strong>{str(data['handing_type'])}</strong>\n'
        f'Вид скетча: <strong>{str(data['execution_type'])}</strong>\n'
    )

    if data['execution_type'] in ['Акварель фэшн','Акварель портреты']:
        match bool(data['akva_brand']):
            case True: 
                final_text = f'{final_text}Дополнительно: <strong>С брендированием</strong>\n'
            case False:
                final_text = f'{final_text}Дополнительно: <strong>Без брендирования</strong>\n'

    final_text = (
        f'{final_text}В чем вручаем: <strong>{str(data['what_to_hand_over'])}</strong>\n'
        f'Желаемое количество часов: <strong>{str(data['hours_qty'])}</strong>\n'
        f'Если не успеваем всех нарисовать: <strong>{str(data['no_time_reaction'])}</strong>\n\n'
    )  

    final_text = (
        f'{final_text}Сумма заказа составит: <strong>{str(amount)}</strong> рублей\n\n'
    )

    final_text = (
        f'{final_text}Для брони даты необходимо внести предоплату 5000 рублей '
        f'по номеру {pay_to_phone_num} в один из банков:\n'
        '- Т-Банк\n'
        '- Сбер\n'
        '- АльфаБанк\n'
        f'(получатель <strong>{pay_to_name}</strong>)'
    )

    return final_text


def get_price():
    price_table = (
        '<strong>Услуги / Тарифы</strong>\n\n'
        'Минимальный заказ для Москвы и области от 2х часов, для Санкт-Петербурга от 4х часов\n'
        'Бронь даты 5000 рублей, входит в указанную стоимость\n'
        'В подарок индивидуальный дизайн-макет скетчей\n'
        'Возможна доплата за дальний выезд\n\n'

        '<strong>DIGITAL С ПЕЧАТЬЮ А6</strong>\n'
        '<strong>8 000</strong> руб\n'
        'Рисую на планшете. Распечатываю на фото-бумаге в формате А6. Дополнительно передаю скетч в цифровом виде. Вручаю в конверте. В час получается 6-8 человек'
        
        '\n\n'

        '<strong>DIGITAL С ПЕЧАТЬЮ А5</strong>\n'
        '<strong>9 000</strong> руб\n'
        'Рисую на планшете. Распечатываю на акварельной бумаге в формате А5. Дополнительно передаю скетч в цифровом виде. Вручаю в конверте. В час получается 6-8 человек'
    
        '\n\n'

        '<strong>ТРАДИЦИОННЫМИ МАТЕРИАЛАМИ А5</strong>\n'
        '<strong>10 000</strong> руб\n'
        'Рисую линерами и акварелью на акварельной бумаге в формате А5. Вручаю в конверте. В час получается 5-7 человек'
            
        '\n\n'

        '<strong>ЦВЕТНЫЕ КОНВЕРТЫ</strong>\n'
        '<strong>1 000</strong> руб\n'
        'Возможно вручение не в стандартном крафтовом конверте, а в стильном цветном, подбираем под стиль вашего мероприятия - плюс 1000 рублей к стоимости часа'

        '\n\n'

        '<strong>ОФОРМИТЬ В РАМУ</strong>\n'
        '<strong>1 000</strong> руб\n'
        'Возможно вручение в раме или пластиковом магнитном боксе - плюс 1000 рублей к стоимости часа'
    ) 

    return price_table