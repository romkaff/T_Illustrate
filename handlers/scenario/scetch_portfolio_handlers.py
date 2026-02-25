from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
import json
from strings import scetch_string
from kbds.inline import get_callback_btns


scetch_portfolio_router = Router()


# Загрузка данных из JSON
def load_portfolio():
    with open('strings/portfolio.json', 'r', encoding='utf-8') as f:
        return json.load(f)

@scetch_portfolio_router.callback_query(F.data.startswith('gallery_'))
async def show_portfolio(callback: CallbackQuery):
    data = callback.data.split('_')
    category = data[1]  # 'portraits' или 'watercolors'
    index = int(data[2]) if len(data) > 2 else 0

    portfolio = load_portfolio()
    # Получаем категорию (объект с полями name и items)
    category_data = portfolio.get(category)
    if not category_data:
        await callback.answer("Категория не найдена")
        return

    # Берём массив работ из поля "items"
    items = category_data["items"]
    if not items:
        await callback.answer("Работы не найдены")
        return

    # Ограничиваем индекс допустимыми значениями
    index = max(0, min(index, len(items) - 1))
    item = items[index]

    # Формируем текст подписи
    title = category_data["main_title"]
    if item['title']:
        title += '\n' + item['title']

    caption = (
        f"<b>{title}</b>\n"
        f"{index + 1} из {len(items)}\n\n"
        f"{item.get('description', '')}"
    )

    back_data = category_data["back_data"]
    if not back_data:
        back_data = 'scetches_portfolio'

    # Создаём кнопки навигации
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"gallery_{category}_{index - 1}"
            ) if index > 0 else InlineKeyboardButton(text=" ", callback_data="ignore"),
            InlineKeyboardButton(
                text="➡️", 
                callback_data=f"gallery_{category}_{index + 1}"
            ) if index < len(items) - 1 else InlineKeyboardButton(text=" ", callback_data="ignore")
        ],
        [
            InlineKeyboardButton(text="Заказать", callback_data=f"scetches_order_{category_data['name']}_{index}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=back_data)
        ]
    ])

    await callback.message.edit_media(
        media=InputMediaPhoto(media=item["image_url"], caption=caption),
        reply_markup=keyboard
    )


async def portfolio_handler(message: Message, portfolio_type: str = None):
    portfolio = load_portfolio()

    category_data = portfolio.get(portfolio_type)
    if not category_data:
        await message.answer("Категория не найдена")
        return

    # Берём массив работ из поля "items"
    items = category_data["items"]
    if not items:
        await message.answer("Работы не найдены")
        return

    first_item = items[0]

    title = category_data["main_title"]
    if first_item['title']:
        title += '\n' + first_item['title']

    caption = (
        f"<b>{title}</b>\n"
        f"1 из {len(items)}\n\n"
        f"{first_item.get('description', '')}"
    )

    back_data = category_data["back_data"]
    if not back_data:
        back_data = 'scetches_portfolio'

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➡️", callback_data=f"gallery_{portfolio_type}_1"),
        ],
        [
            InlineKeyboardButton(text="Заказать", callback_data=f"scetches_order_{category_data['name']}_{0}")
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data=back_data)
        ]
    ])

    await message.answer_photo(
        photo=first_item["image_url"],
        caption=caption,
        reply_markup=keyboard
    )    


@scetch_portfolio_router.callback_query(F.data == 'portfolio_digital')
async def portfolio_digital(callback: CallbackQuery):
    await callback.answer()
    await portfolio_handler(callback.message, 'DigCommon')
    

@scetch_portfolio_router.callback_query(F.data == 'portfolio_akva_portrait')
async def portfolio_akva_portrait(callback: CallbackQuery):
    await callback.answer()
    await portfolio_handler(callback.message, 'AkvaPort')


@scetch_portfolio_router.callback_query(F.data == 'portfolio_akva_fashion')
async def portfolio_akva_fashion(callback: CallbackQuery):
    await callback.answer()
    await portfolio_handler(callback.message, 'AkvaFshn')    


@scetch_portfolio_router.callback_query(F.data == 'portfolio_other')
async def portfolio_other(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(scetch_string.PORTFOLIO_DIGITAL, reply_markup=get_callback_btns(
                btns={
                    "Черно-белые портреты":"portfolio_digital_bw",
                    "Линейные скетчи":"portfolio_digital_linear",
                    "Силуэтные скетчи":"portfolio_digital_siluet",
                    "Цифровые комиксы":"portfolio_digital_comics",
                    "Другое":"portfolio_digital_other",
                    "Назад":"scetches_portfolio",
                },
                sizes=(1, )
            ))
    

@scetch_portfolio_router.callback_query(F.data == 'portfolio_digital_bw')
async def portfolio_digital_bw(callback: CallbackQuery):
    await callback.answer()
    await portfolio_handler(callback.message, 'DigBW')    


@scetch_portfolio_router.callback_query(F.data == 'portfolio_digital_linear')
async def portfolio_digital_linear(callback: CallbackQuery):
    await callback.answer()
    await portfolio_handler(callback.message, 'DigLine')  


@scetch_portfolio_router.callback_query(F.data == 'portfolio_digital_siluet')
async def portfolio_digital_siluet(callback: CallbackQuery):
    await callback.answer()
    await portfolio_handler(callback.message, 'DigSilu')   


@scetch_portfolio_router.callback_query(F.data == 'portfolio_digital_comics')
async def portfolio_digital_comics(callback: CallbackQuery):
    await callback.answer()
    await portfolio_handler(callback.message, 'DigCom') 


@scetch_portfolio_router.callback_query(F.data == 'portfolio_digital_other')
async def portfolio_digital_other(callback: CallbackQuery):
    await callback.answer()
    await portfolio_handler(callback.message, 'DigOth')           