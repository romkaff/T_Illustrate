import os

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from filters import chat_types

from strings import general_string


#
#       Начальный экран
#
def get_start_keyboard(is_admin: bool):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Услуги',
                callback_data='start_services'))
    keyboard.add(InlineKeyboardButton(text='Перейти на сайт',
                url=general_string.WEB_SITE,
                callback_data='start_site'))
    keyboard.add(InlineKeyboardButton(text='Написать в личку',
                url=f'https://t.me/{os.getenv('MASHA_NICKNAME')}',
                callback_data='start_private'))
    keyboard.add(InlineKeyboardButton(text='Поделиться с другом',
                callback_data='start_share'))
    
    if is_admin:
        keyboard.add(InlineKeyboardButton(text='Админка',
                    callback_data='start_adminka'))
    
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


#
#       Админская клавиатура
#
def get_adminka_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Рассылки',
            callback_data='admin_mailing'))
        
    return keyboard.adjust(1).as_markup(resize_keyboard=True)


#
#       Экран Услуги
#
def get_services_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Скетчи',
                callback_data='service_scetches'))
    keyboard.add(InlineKeyboardButton(text='Арт-терапия',
                callback_data='service_art_therapy'))    
    keyboard.add(InlineKeyboardButton(text='Задать вопрос',
            url=f'https://t.me/{os.getenv('MASHA_NICKNAME')}',
            callback_data='scetches_private'))

    return keyboard.adjust(1).as_markup(resize_keyboard=True)


#
#       Скетчи
#
def get_scetches_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Тарифы',
                callback_data='scetches_price'))
    keyboard.add(InlineKeyboardButton(text='Примеры работ',
                callback_data='scetches_portfolio'))
    keyboard.add(InlineKeyboardButton(text='Заказать',
                callback_data='scetches_order')) 
    keyboard.add(InlineKeyboardButton(text='Задать вопрос',
            url=f'https://t.me/{os.getenv('MASHA_NICKNAME')}',
            callback_data='scetches_private'))
    keyboard.add(InlineKeyboardButton(text='К списку услуг',
                callback_data='start_services'))     

    return keyboard.adjust(1).as_markup(resize_keyboard=True)


#
#       Экран Скетчи - нажали Назад
#
def get_scetches_short_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Заказать',
                callback_data='scetches_order')) 
    keyboard.add(InlineKeyboardButton(text='Задать вопрос',
            url=f'https://t.me/{os.getenv('MASHA_NICKNAME')}',
            callback_data='scetches_private'))
    keyboard.add(InlineKeyboardButton(text='К списку услуг',
                callback_data='start_services'))     

    return keyboard.adjust(1).as_markup(resize_keyboard=True)

#
#       Скетчи
#
#       К списку услуг
#       Перейти на сайт
#       Написать в личку
#       Поделиться с другом
#       Админка
#
def get_scetches_after_order_keyboard(is_admin: bool):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='К списку услуг',
                callback_data='start_services'))
    keyboard.add(InlineKeyboardButton(text='Перейти на сайт',
                url=general_string.WEB_SITE,
                callback_data='start_site'))
    keyboard.add(InlineKeyboardButton(text='Написать в личку',
                url=f'https://t.me/{os.getenv('MASHA_NICKNAME')}',
                callback_data='start_private'))
    keyboard.add(InlineKeyboardButton(text='Поделиться с другом',
                callback_data='start_share'))
    
    if is_admin:
        keyboard.add(InlineKeyboardButton(text='Админка',
                    callback_data='start_adminka'))
    
    return keyboard.adjust(1).as_markup(resize_keyboard=True)

#
#       Арт-терапия
#
#       Групповая
#       Индивидуальная
#       Задать вопрос
#
def get_art_therapy_keyboard():
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Групповая',
            callback_data='art_therapy_group'))
    keyboard.add(InlineKeyboardButton(text='Индивидуальная',
            callback_data='art_therapy_individual')) 
    keyboard.add(InlineKeyboardButton(text='Задать вопрос',
            url=f'https://t.me/{os.getenv('MASHA_NICKNAME')}',
            callback_data='art_therapy_private'))  
             
    return keyboard.adjust(1).as_markup(resize_keyboard=True)





















class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Товары 🍕": "catalog",
        "Корзина 🛒": "cart",
        "О нас ℹ️": "about",
        "Оплата 💰": "payment",
        "Доставка ⛵": "shipping",
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))
            
    return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                callback_data=MenuCallBack(level=level-1, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                callback_data=MenuCallBack(level=3, menu_name='cart').pack()))
    
    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                callback_data=MenuCallBack(level=level+1, menu_name=c.name, category=c.id).pack()))

    return keyboard.adjust(*sizes).as_markup()


def get_products_btns(
    *,
    level: int,
    category: int,
    page: int,
    pagination_btns: dict,
    product_id: int,
    sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Назад',
                callback_data=MenuCallBack(level=level-1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='Корзина 🛒',
                callback_data=MenuCallBack(level=3, menu_name='cart').pack()))
    keyboard.add(InlineKeyboardButton(text='Купить 💵',
                callback_data=MenuCallBack(level=level, menu_name='add_to_cart', product_id=product_id).pack()))

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page + 1).pack()))
        
        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


def get_user_cart(
    *,
    level: int,
    page: int | None,
    pagination_btns: dict | None,
    product_id: int | None,
    sizes: tuple[int] = (3,)
):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.add(InlineKeyboardButton(text='Удалить',
                    callback_data=MenuCallBack(level=level, menu_name='delete', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='-1',
                    callback_data=MenuCallBack(level=level, menu_name='decrement', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='+1',
                    callback_data=MenuCallBack(level=level, menu_name='increment', product_id=product_id, page=page).pack()))

        keyboard.adjust(*sizes)

        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page + 1).pack()))
            elif menu_name == "previous":
                row.append(InlineKeyboardButton(text=text,
                        callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page - 1).pack()))

        keyboard.row(*row)

        row2 = [
        InlineKeyboardButton(text='На главную 🏠',
                    callback_data=MenuCallBack(level=0, menu_name='main').pack()),
        InlineKeyboardButton(text='Заказать',
                    callback_data=MenuCallBack(level=0, menu_name='order').pack()),
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(text='На главную 🏠',
                    callback_data=MenuCallBack(level=0, menu_name='main').pack()))
        
        return keyboard.adjust(*sizes).as_markup()


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()