from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from strings import scetch_string
from kbds.inline import get_callback_btns, get_scetches_keyboard, get_scetches_short_keyboard


scetch_router = Router()


def get_price():
    price_table = (
        '<strong>Услуги / Тарифы</strong>'
        '\n\n'
        
        '<strong>Digital с печатью ✦ 8 000</strong> руб/час\n'
        'Рисую на планшете. Печатаю на фотобумаге размера А6 (10х15). В час 6-7 человек'
        '\n\n'

        '<strong>Digital А5 ✦ 9 000</strong> руб/час\n'
        'Рисую на планшете. Печатаю на акварельной бумаге размера А5 (15х21). В час 6-7 человек'
        '\n\n'

        '<strong>Акварель портреты А5 ✦ 10 000</strong> р/ч\n'
        'Рисую акварелью на акварельной бумаге размера А5 (15х21). В час 5-6 человек'
        '\n\n'

        '<strong>Акварель фэшн А5 ✦ 10 000</strong> руб/ч\n'
        'Рисую линерами на акварельной бумаге размера А5 (15х21). В час 5-7 человек'
        '\n\n'

        'Дату бронирую по предоплате 10 000 для физ.лиц, и 50% для юр.лиц - эта сумма входит в стоимость, остаток вносится в день мероприятия.\n\n'
        'Дополнительно оплачивается выезд за МКАД - от 4 000 руб в зависимости от удаленности.'
    ) 

    return price_table


def get_price_conditions():
    price_conditions_table = (
        '<strong>Дополнительно</strong>'
        '\n\n'

        '<strong>Цветные конверты ✦ 1 000</strong> руб/час\n'
        'Возможно вручение не в стандартном крафтовом конверте, а в стильном цветном, подбираем под стиль вашего мероприятия - плюс 1000 рублей к стоимости часа'
        '\n\n'

        '<strong>Оформить в раму ✦ 1 000</strong> руб/час\n'
        'Возможно вручение в раме или пластиковом магнитном боксе - плюс 1 000 руб. к стоимости часа'
        '\n\n'

        'Минимальный заказ:\nдля Москвы и области от 3-х часов,\nдля Санкт-Петербурга от 6-х часов.\n'
        'Возможна доплата за дальний выезд'
    )

    return price_conditions_table


@scetch_router.callback_query(F.data == 'service_scetches')
async def scetch(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(scetch_string.SCETCH_START, reply_markup=get_scetches_keyboard())
    

@scetch_router.callback_query(F.data == 'scetches_price')
async def scetches_price(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await callback.message.answer(get_price())
    await callback.message.answer(get_price_conditions(), reply_markup=get_scetches_short_keyboard())


@scetch_router.callback_query(F.data == 'scetches_portfolio')
async def scetches_portfolio(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer() 
    await callback.message.answer(scetch_string.SCETCH_PORTFOLIO_START, reply_markup=get_callback_btns(
                btns={
                    "Цифровые":"portfolio_digital",
                    "Акварель портреты":"portfolio_akva_portrait",
                    "Акварель фэшн":"portfolio_akva_fashion",
                    "Другие стили":"portfolio_other",
                },
                sizes=(1, )
            ))