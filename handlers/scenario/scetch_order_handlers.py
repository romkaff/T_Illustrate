import os
import re
from datetime import datetime

from aiogram import Router, types, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from kbds.inline import get_scetches_after_order_keyboard, get_callback_btns
from handlers.scenario import scetch_handlers
from strings import scetch_questionnaire, scetch_string
from database.models import ScetchRequest
from database.orm_query import (
    orm_add_scetch_request,
    orm_get_user,
    orm_set_user_specified_name
)


scetch_order_router = Router()

bot_admins = os.getenv('BOT_ADMINS')
bot_name = os.getenv('BOT_NAME')


#
# Загрузка опросника
#
def load_questionnaire(category_filter: str = None) -> dict:
    full_questionnaire = scetch_questionnaire.scetch_quest_json

    # Без фильтра возвращаем весь опросник
    if not category_filter:
        return full_questionnaire  

    # Фильтруем категории
    filtered_categories = [
        cat for cat in full_questionnaire["categories"]
        if cat["name"] == category_filter
    ]

    return {"categories": filtered_categories}


#
# Валидаторы
#
def validate_email(text: str) -> bool:
    return re.match(r"^[^@]+@[^@]+\.[^@]+$", text) is not None

def validate_phone(text: str) -> bool:
    return len(re.sub(r"\D", "", text)) == 10 # Простой чек: 10 цифр

def validate_date(text: str) -> bool:
    try:
        datetime.strptime(text, "%d.%m.%Y")
        return True
    except ValueError:
        return False

def validate_time(text: str) -> bool:
    try:
        datetime.strptime(text, "%H:%M")
        return True
    except ValueError:
        return False


# Состояния FSM
class SurveyStates(StatesGroup):
    ask_name = State()
    ask_phone = State()
    ask_nickname = State()
    ask_email = State()
    ask_date = State()
    ask_variant = State()
    ask_hours_qty = State()
    ask_time = State()
    ask_address = State()
    ask_new_name = State()


class ReplyState(StatesGroup):
    waiting_for_reply = State() 


#
# Класс опросника
#
class SurveyManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.questionnaire = load_questionnaire("Заказ скетча")
        self.questions = []
        self.db_data = {}
        self._flatten_questions()

    def _flatten_questions(self):
        # Преобразуем иерархию категорий → список вопросов с метаданными
        for category in self.questionnaire["categories"]:
            for q in category["questions"]:
                self.questions.append(
                    {
                        "type": "question",
                        "category": category["name"],
                        "text": q["text"],
                        "expected_type": q["type"],
                        "required": q["required"],
                        "placeholder": q["placeholder"],
                        "db_field": q["db_field"],
                        "state": q["state"]
                    }
                )

    async def start_survey(self, callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
        # Запуск опроса
        self.db_data["user_id"] = callback.from_user.id
        self.db_data["user_first_name"] = callback.from_user.first_name
        self.db_data["user_last_name"] = callback.from_user.last_name

        data = await state.get_data()
        self.selected_scetch_variant = data.get("selected_scetch_variant", None)

        await state.update_data(survey_index=0)
        await state.set_state(f'SurveyStates:{self.questions[0]["state"]}')
        await self._ask_next_question(callback.message, state, session)

    async def _ask_next_question(self, message: types.Message, state: FSMContext, session: AsyncSession):
        # Вывод следующего вопроса
        data = await state.get_data()
        index = data["survey_index"]

        #
        # Опрос окончен. Сохранение результата в БД + отбойник автору
        #
        if index >= len(self.questions):
            scetch_order = await orm_add_scetch_request(session, self.db_data)
            await self.notify_about_new_scetch_request()
            is_admin = str(message.chat.id) in bot_admins
            await message.answer(get_scetch_order_info(scetch_order), parse_mode="HTML")
            await message.answer(scetch_handlers.get_price_conditions(), reply_markup=get_scetches_after_order_keyboard(is_admin))
            await state.clear()
            return

        # Получаем очередной вопрос
        current = self.questions[index]
        
        # В следующем вопросе (если он есть) подсматриваем следующее состояние. В него и переведем FSM
        if index + 1 < len(self.questions):
            next = self.questions[index + 1]

            if next["state"]:
                state_name = f"SurveyStates:{next['state']}" 
                await state.set_state(state_name)

        # Текст вопроса. Если есть подсказка в "placeholder" покажем ее со смайликом
        text_answer = current["text"]
        if current["placeholder"]:
            text_answer = f"{current['text']}\n\n<i>👉 {current['placeholder']}</i>"

        # Если пользователь указал имя надо будет либо подтвердить его, либо дать возможность изменить
        if current["db_field"] == 'name':
            user = await orm_get_user(session, message.chat.id)
            if user.specified_name:
                text_answer = f"При знакомстве вы указали имя {user.specified_name}. Продолжить?"
                await message.answer(text_answer, reply_markup=get_callback_btns(
                    btns={
                        "Все верно":"confirmed_name",
                        "Изменить имя":"need_change_name",
                    },
                    sizes=(1, )
                )) 

        # Здесь обработка уникальных условий для вопроса
        match current["expected_type"]:
            case "boolean": 
                # Формируем клавиатуру для boolean
                keyboard = ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                await message.answer(text_answer, parse_mode="HTML", reply_markup=keyboard)

            case "scetch_variant":
                if "Digital" in self.selected_scetch_variant:
                    keyboard = ReplyKeyboardMarkup(
                        keyboard=[
                            [KeyboardButton(text="А5"), KeyboardButton(text="А6")]
                        ],
                        resize_keyboard=True,
                        one_time_keyboard=True
                    )
                    await message.answer(text_answer, parse_mode="HTML", reply_markup=keyboard)
                else:
                    # ПРОПУСК ВОПРОСА: автоматически сохраняем selected_scetch_variant
                    self.db_data["scetch_variant"] = self.selected_scetch_variant
                    await state.update_data(survey_index=index + 1)
                    await self._ask_next_question(message, state, session)
            case _:
                # Для остальных случаев — поле ввода
                if current["db_field"] != 'name':
                    await message.answer(text_answer, parse_mode="HTML") 

    async def handle_answer(self, message: types.Message, state: FSMContext, session: AsyncSession):
        data = await state.get_data()
        index = data["survey_index"] # - 1  # Индекс текущего вопроса

        if index < 0 or index >= len(self.questions):
            return

        current = self.questions[index]
        if current["type"] != "question":
            await self._ask_next_question(message, state, session)
            return

        is_valid = True
        answer = message.text.strip()
        
        match current["db_field"]:
            case 'name':
                if data.get("name_for_order"):
                    answer = data["name_for_order"]
                else:
                    if not answer:
                        is_valid = False
                        await message.answer("Пожалуйста, укажите имя.")
            case 'scetch_variant':
                answer = f"{self.selected_scetch_variant}"

        # Валидация по типу
        if current["expected_type"] == "number":
            if not answer.isdigit():
                is_valid = False
                await message.answer("Введите число!")
        elif current["expected_type"] == "email":
            if not validate_email(answer):
                is_valid = False
                await message.answer("Некорректный email.\nНеобходим email в формате: xxx@yyy.zz")
        elif current["expected_type"] == "phone":
            if not validate_phone(answer):
                is_valid = False
                await message.answer("Некорректный телефон!")
        elif current["expected_type"] == "date":
            if not validate_date(answer):
                is_valid = False
                await message.answer("Дата в формате ДД.ММ.ГГГГ!")
        elif current["expected_type"] == "time":
            if not validate_time(answer):
                is_valid = False
                await message.answer("Время в формате ЧЧ:ММ!")
        elif current["expected_type"] == "boolean":
            if answer.lower() not in ["да", "нет"]:
                is_valid = False
                await message.answer("Выберите «Да» или «Нет»!")
            else:
                answer = answer.lower() == "да"

        if is_valid:
            self.db_data[current["db_field"]] = answer # Сохраняем ответ
            await state.update_data(survey_index=index + 1)
            await self._ask_next_question(message, state, session)
        else:
            # Если ошибка — остаёмся на том же вопросе
            await self._ask_next_question(message, state, session)

    async def notify_about_new_scetch_request(self):
        try:
            # Формируем текст сообщения
            text_notify = (
                "<b>Новый заказ на скетч!</b>\n\n"
                f"<b>Имя клиента:</b> {self.db_data['name']}\n"
                f"<b>Ник в телеграм:</b> {self.db_data['tg_nick']}\n"
                f"<b>Телефон:</b> {self.db_data['phone']}\n"
                f"<b>Email:</b> {self.db_data['email']}\n"
                f"<b>Дата мероприятия:</b> {self.db_data['event_date']}\n"
                f"<b>Время начала:</b> {self.db_data['start_time']}\n"
                f"<b>Адрес:</b> {self.db_data['address']}\n"
                f"<b>Вариант скетча:</b> {self.db_data['scetch_variant']}\n"
                f"<b>Длительность:</b> {self.db_data['hours_qty']} часов\n\n"
                f"<i>Заказ создан: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</i>"
            )
            
            # Отправляем сообщение
            await self.bot.send_message(
                chat_id=int(os.getenv('MASHA_ID')),
                text=text_notify,
                parse_mode="HTML", reply_markup=get_callback_btns(
                    btns={
                        "Ответить":f"reply_to_customer_{self.db_data['user_id']}", 
                    },
                    sizes=(1, )
                )) 
            
            # TODO убрать потом
            await self.bot.send_message(
                chat_id=int(os.getenv('ROMADJON_ID')),
                text=text_notify,
                parse_mode="HTML", reply_markup=get_callback_btns(
                    btns={
                        "Ответить":f"reply_to_customer_{self.db_data['user_id']}", 
                    },
                    sizes=(1, )
                )) 

        except Exception as e:
            print(f"Ошибка отправки уведомления: {e}")


def get_scetch_order_info(scetch_order: ScetchRequest) -> str:
    order_text = (
        "Спасибо, ваш запрос успешно отправлен!\n" 
        "Вы заказали:\n\n"
        f"Выбранный стиль: {scetch_order.scetch_variant}\n"
        f"Дата мероприятия: {scetch_order.event_date}\n"
        f"Время начала: {scetch_order.start_time}\n"
        f"Количество часов: {scetch_order.hours_qty}\n"
        f"Адрес: {scetch_order.address}\n\n"
        "Мария свяжется с вами в ближайшее время!"
    )

    return order_text

# Обработчики
@scetch_order_router.callback_query(F.data == 'scetches_order')
async def cmd_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    await callback.message.answer(scetch_string.SCETCH_ORDER, reply_markup=get_callback_btns(
                btns={
                    "Примеры работ":"scetches_portfolio",
                },
                sizes=(1, )
            )) 


@scetch_order_router.message(F.text, StateFilter(SurveyStates.ask_new_name))
async def change_name(message: types.Message, state: FSMContext, session: AsyncSession):
    new_name = message.text.strip()
    
    if not new_name:
        await message.answer("Имя не может быть пустым. Пожалуйста, введите имя.")
        return
    
    # 1. Сохраняем имя в базу данных (ваш код)
    await orm_set_user_specified_name(session, message.chat.id, new_name)
    
    # 2. Сохраняем в FSM и db_data
    await state.update_data(name_for_order=new_name)
    survey_manager = scetch_order_router.survey_manager
    survey_manager.db_data["name"] = new_name
    
    # 3. Получаем индекс вопроса, к которому нужно вернуться
    data = await state.get_data()
    return_index = data.get("return_index", 0)
    
    # 4. Возвращаемся в основной сценарий к следующему вопросу
    await state.update_data(survey_index=return_index + 1)
    await state.set_state(f'SurveyStates:{survey_manager.questions[return_index + 1]["state"]}')
    
    # 5. Выводим следующий вопрос (телефон)
    await survey_manager._ask_next_question(message, state, session)


@scetch_order_router.message(StateFilter(SurveyStates))
async def process_answer(message: types.Message, state: FSMContext, session: AsyncSession):
    survey_manager = scetch_order_router.survey_manager
    await survey_manager.handle_answer(message, state, session)
  

#
# Кнопка Заказать в галерее
#
@scetch_order_router.callback_query(F.data.startswith("scetches_order_"))
async def process_portfolio_variant(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    
    parts = callback.data.split("_")
    scetch_variant = f"{parts[2]}"
    
    await state.update_data(selected_scetch_variant=scetch_variant)
    survey_manager = scetch_order_router.survey_manager
    await survey_manager.start_survey(callback, state, session)


#
# Отправить ссылку на бота другу
#
@scetch_order_router.callback_query(F.data == "start_share")
async def start_share(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Отправить другу",
            switch_inline_query=scetch_string.SHARE_BOT
        )]
    ])

    await callback.message.answer("Нажмите, чтобы отправить ссылку на бота другу:", reply_markup=keyboard)   


#
# Подтвердить/Изменить ФИО
#
@scetch_order_router.callback_query(F.data == "confirmed_name")
async def confirmed_name(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    data = await state.get_data()
    current_index = data["survey_index"]

    user = await orm_get_user(session, callback.from_user.id)
    name_for_order = user.specified_name
    await state.update_data(name_for_order=name_for_order)
    
    survey_manager = scetch_order_router.survey_manager
    survey_manager.db_data["name"] = name_for_order

    await state.update_data(survey_index=current_index + 1)
    await survey_manager._ask_next_question(callback.message, state, session)


@scetch_order_router.callback_query(F.data == "need_change_name")
async def need_change_name(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()

    # Сохраняем текущий индекс вопроса (чтобы вернуться после ввода имени)
    data = await state.get_data()
    current_index = data["survey_index"]
    await state.update_data(return_index=current_index)  # сохраняем для возврата
    
    # Переходим в состояние ввода нового имени
    await state.set_state(SurveyStates.ask_new_name)
    
    await callback.message.answer(
        "Пожалуйста, введите ваше новое имя:",
        reply_markup=types.ReplyKeyboardRemove()
    )  


#
# Диалог заказчика с художником
#
@scetch_order_router.message(ReplyState.waiting_for_reply)
async def handle_reply(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    
    author_id = data.get('author_id')
    customer_id = data.get('customer_id')
    to_author = data.get('to_author')

    # Проверка: есть ли нужные данные?
    if not author_id or not customer_id:
        await message.answer("Ошибка: не удалось определить адресата.")
        await state.clear()
        return

    try:
        if to_author:
            forwarded_msg = (
                f"<b>Сообщение от заказчика:</b>\n\n"
                f"{message.text}\n\n"
                f"<i>Отправлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>"
            )

            await bot.send_message(
                chat_id=int(author_id),
                text=forwarded_msg,
                parse_mode="HTML",
                reply_markup=get_callback_btns(
                    btns={
                        "Ответить заказчику": f"reply_to_customer_{customer_id}",
                    },
                    sizes=(1,)
                )
            )

            await message.answer("✅ Ваше сообщение отправлено художнику!")
        
        else:
            forwarded_msg = (
                f"<b>Сообщение от художника:</b>\n\n"
                f"{message.text}\n\n"
                f"<i>Отправлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>"
            )

            await bot.send_message(
                chat_id=int(customer_id),
                text=forwarded_msg,
                parse_mode="HTML",
                reply_markup=get_callback_btns(
                    btns={
                        "Ответить художнику": f"reply_to_author_{author_id}",
                    },
                    sizes=(1,)
                )
            )

            await message.answer("✅ Ваше сообщение отправлено заказчику!")

    except Exception as e:
        await message.answer(f"❌ Ошибка отправки: {e}")

    finally:
        await state.clear()


@scetch_order_router.callback_query(F.data.startswith('reply_to_customer_'))
async def reply_to_customer(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    customer_id = callback.data.split('_')[-1]
    
    await state.update_data(
        customer_id=customer_id,
        author_id=callback.from_user.id,
        to_author=False
    )
    await state.set_state(ReplyState.waiting_for_reply)
    await callback.message.answer(
        "Напишите ответ заказчику — он получит его напрямую.\n\n"
        f"Чтобы отменить — отправьте /cancel"
    )


@scetch_order_router.callback_query(F.data.startswith('reply_to_author_'))
async def reply_to_author(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    author_id = callback.data.split('_')[-1]  # ← должно быть ID художника!

    await state.update_data(
        author_id=author_id,
        customer_id=callback.from_user.id,
        to_author=True
    )
    await state.set_state(ReplyState.waiting_for_reply)
    await callback.message.answer(
        "Напишите ответ художнику. Он получит его напрямую.\n"
        "Чтобы отменить — отправьте /cancel"
    )