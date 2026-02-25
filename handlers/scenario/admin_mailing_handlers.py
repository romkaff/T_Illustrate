import os
import time

from aiogram import Router, types, F, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_get_active_mailing_list,
    orm_add_mailing,
    orm_delete_mailing,
    orm_get_mailing,
    orm_update_mailing_name,
    orm_update_mailing_text,
    orm_update_mailing_file
)    

admin_mailing_router = Router()


class MailingStates(StatesGroup):
    waiting_for_new_name = State()
    waiting_for_new_text = State()
    waiting_for_new_file = State()


# Обработчики
@admin_mailing_router.callback_query(F.data == 'admin_mailing')
async def mailing_start(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailings = await orm_get_active_mailing_list(session)
    
    if mailings:
        text = "<b>Активные рассылки:</b>\n\n"
        for m in mailings:
            text += f"📧 {m.name} (ID: {m.id})\n"
    else:
        text = "Нет активных рассылок."

    # Кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать новую рассылку", callback_data="create_mailing")],
        [InlineKeyboardButton(text="Редактировать рассылку", callback_data="edit_mailing_choose")],
        [InlineKeyboardButton(text="Удалить рассылку", callback_data="delete_mailing_choose")],
        [InlineKeyboardButton(text="Тестовая отправка", callback_data="test_send_choose")],
        [InlineKeyboardButton(text="Боевая отправка", callback_data="send_mailing")],        
        [InlineKeyboardButton(text="Показать все рассылки", callback_data="show_all_mailings")]
    ])

    await callback.message.answer(text, reply_markup=keyboard)


@admin_mailing_router.callback_query(F.data == "create_mailing")
async def create_mailing(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    new_mailing = await orm_add_mailing(session)
    await callback.answer(f"Создана рассылка ID: {new_mailing.id}. Теперь отредактируйте её.")
    await mailing_start(callback, state, session)


@admin_mailing_router.callback_query(F.data == "edit_mailing_choose")
async def show_mailing_list_for_edit(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailings = await orm_get_active_mailing_list(session)

    if not mailings:
        await callback.answer("Нет рассылок для редактирования.")
        return

    # Формируем клавиатуру с кнопками для каждой рассылки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{m.name} (ID: {m.id})",
                callback_data=f"edit_mailing_{m.id}"
            )
        ] for m in mailings
    ])

    await callback.message.answer(
        "Выберите рассылку для редактирования:",
        reply_markup=keyboard
    )
    

@admin_mailing_router.callback_query(F.data.startswith("edit_mailing_"))
async def edit_selected_mailing(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailing_id = int(callback.data.split("_")[-1])
    mailing = await orm_get_mailing(session, mailing_id)

    if not mailing:
        await callback.answer("Рассылка не найдена.")
        return

    # Показываем меню редактирования выбранной рассылки
    text = (
        f"<b>Редактирование рассылки:</b> {mailing.name}\n"
        f"ID: {mailing_id}\n\n"
        f"<i>Текст:</i>\n{mailing.message_text or 'Нет текста'}\n\n"
        f"<i>Файл:</i> {mailing.file_local_path or 'Нет файла'}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить название", callback_data=f"change_name_{mailing_id}")],
        [InlineKeyboardButton(text="Изменить текст", callback_data=f"change_text_{mailing_id}")],
        [InlineKeyboardButton(text="Загрузить файл", callback_data=f"upload_file_{mailing_id}")],
        [InlineKeyboardButton(text="← Назад", callback_data="admin_mailing")]
    ])

    await callback.message.answer(text, reply_markup=keyboard)


@admin_mailing_router.callback_query(F.data.startswith("change_name_"))
async def prompt_for_new_name(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailing_id = int(callback.data.split("_")[-1])
    mailing = await orm_get_mailing(session, mailing_id)

    if not mailing:
        await callback.answer("Рассылка не найдена.")
        return
    
    # Сохраняем ID рассылки в состояние, чтобы потом знать, какую обновлять
    await state.update_data(mailing_id=mailing_id)
    
    # Просим пользователя ввести новое название
    await callback.message.answer(
        "Введите новое название рассылки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_rename")]
        ])
    )
    await state.set_state(MailingStates.waiting_for_new_name)   



@admin_mailing_router.message(MailingStates.waiting_for_new_name)
async def set_new_name(message: Message, state: FSMContext, session: AsyncSession):
    new_name = message.text.strip()
    
    if not new_name:
        await message.answer("Название не может быть пустым. Попробуйте ещё раз:")
        return
    
    # Получаем ID рассылки из состояния
    data = await state.get_data()
    mailing_id = data.get("mailing_id")
    
    if not mailing_id:
        await message.answer("Ошибка: не удалось определить рассылку.")
        await state.clear()
        return

    mailing = await orm_get_mailing(session, mailing_id)

    if not mailing:
        await message.answer("Рассылка не найдена.")
        await state.clear()
        return
        
    await orm_update_mailing_name(session, mailing_id, new_name)
    await message.answer(f"Название обновлено: <b>{new_name}</b>")
    await state.clear()     


@admin_mailing_router.callback_query(F.data.startswith("change_text_"))
async def prompt_for_new_text(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailing_id = int(callback.data.split("_")[-1])
    mailing = await orm_get_mailing(session, mailing_id)

    if not mailing:
        await callback.answer("Рассылка не найдена.")
        return
    
    # Сохраняем ID рассылки в состояние, чтобы потом знать, какую обновлять
    await state.update_data(mailing_id=mailing_id)
    
    # Просим пользователя ввести новое название
    await callback.message.answer(
        "Введите новый сопроводительный текст для рассылки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_rename")]
        ])
    )
    await state.set_state(MailingStates.waiting_for_new_text)   


@admin_mailing_router.message(MailingStates.waiting_for_new_text)
async def set_new_text(message: Message, state: FSMContext, session: AsyncSession):
    new_text = message.text.strip()
    
    if not new_text:
        await message.answer("Сопроводительный текст не может быть пустым. Попробуйте ещё раз:")
        return
    
    # Получаем ID рассылки из состояния
    data = await state.get_data()
    mailing_id = data.get("mailing_id")
    
    if not mailing_id:
        await message.answer("Ошибка: не удалось определить рассылку.")
        await state.clear()
        return

    mailing = await orm_get_mailing(session, mailing_id)

    if not mailing:
        await message.answer("Рассылка не найдена.")
        await state.clear()
        return
        
    await orm_update_mailing_text(session, mailing_id, new_text)
    await message.answer(f"Сопроводительный текст обновлен: <b>{new_text}</b>")
    await state.clear()   


@admin_mailing_router.callback_query(F.data.startswith("upload_file_"))
async def prompt_upload_file(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailing_id = int(callback.data.split("_")[-1])
    mailing = await orm_get_mailing(session, mailing_id)

    if not mailing:
        await callback.answer("Рассылка не найдена.")
        return
    
    # Сохраняем ID рассылки в состояние, чтобы потом знать, какую обновлять
    await state.update_data(mailing_id=mailing_id)

    await callback.message.answer(
        "Отправьте файл, который нужно прикрепить к рассылке:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Отменить", callback_data="cancel_upload")]
        ])
    )
    await state.set_state(MailingStates.waiting_for_new_file)


@admin_mailing_router.message(MailingStates.waiting_for_new_file, F.content_type.in_({"document", "photo", "video", "audio"}))
async def handle_uploaded_file(message: Message, state: FSMContext, session: AsyncSession):
    from core.bot import bot

    data = await state.get_data()
    mailing_id = data.get("mailing_id")

    if not mailing_id:
        await message.answer("Ошибка: не удалось определить рассылку.")
        await state.clear()
        return

    # Определяем тип файла и получаем объект
    if message.document:
        file = message.document
        file_name = file.file_name
    elif message.photo:
        file = message.photo[-1]  # самое качественное фото
        file_name = f"photo_{message.message_id}.jpg"
    elif message.video:
        file = message.video
        file_name = file.file_name or f"video_{message.message_id}.mp4"
    elif message.audio:
        file = message.audio
        file_name = file.file_name or f"audio_{message.message_id}.mp3"
    else:
        await message.answer("Неподдерживаемый тип файла. Отправьте документ, фото, видео или аудио.")
        return

    # Получаем file_id (можно использовать для повторной отправки)
    file_id = file.file_id


    # Скачиваем файл на сервер
    try:
        file_object = await bot.get_file(file_id)
        file_path = f"./uploads/{file_name}"  # папка для загруженных файлов
        await bot.download_file(file_object.file_path, file_path)
    except Exception as e:
        await message.answer(f"Ошибка при загрузке файла: {e}")
        return

    # Читаем содержимое файла в байты
    try:
        with open(file_path, "rb") as f:
            file_blob = f.read()
    except Exception as e:
        await message.answer(f"Ошибка при чтении файла: {e}")
        return

    # Сохраняем в БД
    await orm_update_mailing_file(session, mailing_id, file_path, file_blob)

    await message.answer(f"Файл сохранён:\n- Путь: {file_path}\n- Имя: {file_name}")
    await state.clear()


@admin_mailing_router.callback_query(F.data == "delete_mailing_choose")
async def show_mailing_list_for_delete(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailings = await orm_get_active_mailing_list(session)

    if not mailings:
        await callback.answer("Нет рассылок для удаления.")
        return

    # Формируем клавиатуру с кнопками для каждой рассылки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{m.name} (ID: {m.id})",
                callback_data=f"delete_mailing_{m.id}"
            )
        ] for m in mailings
    ])

    await callback.message.answer(
        "Выберите рассылку для удаления:",
        reply_markup=keyboard
    )


@admin_mailing_router.callback_query(F.data.startswith("delete_mailing_"))
async def delete_mailing(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailing_id = int(callback.data.split("_")[-1])
    deleted = await orm_delete_mailing(session, mailing_id)

    if deleted:
        await callback.message.answer("Рассылка удалена.")
    else:
        await callback.message.answer("Рассылка не найдена.")


@admin_mailing_router.callback_query(F.data == "test_send_choose")
async def show_mailing_list_for_test_send(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailings = await orm_get_active_mailing_list(session)

    if not mailings:
        await callback.answer("Нет рассылок для тестовой отправки.")
        return

    # Формируем клавиатуру с кнопками для каждой рассылки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"{m.name} (ID: {m.id})",
                callback_data=f"test_send_mailing_{m.id}"
            )
        ] for m in mailings
    ])

    await callback.message.answer(
        "Выберите рассылку для тестовой отправки:",
        reply_markup=keyboard
    )


@admin_mailing_router.callback_query(F.data.startswith("test_send_mailing_"))
async def test_send_mailing(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.answer()
    mailing_id = int(callback.data.split("_")[-1])
    mailing = await orm_get_mailing(session, mailing_id)

    if not mailing:
        await callback.message.answer(f"Рассылка с ID {mailing_id} не найдена.")
        return

    # Сохраняем ID рассылки в состояние
    await state.update_data(mailing_id=mailing_id)

    # Отправляем клавиатуру с контактами пользователя
    await send_contact_choice(callback.message, state)


async def send_contact_choice(message: Message, state: FSMContext):
    # Получаем контакты пользователя (пример: берём первые 10)
    # В реальном боте можно подключить Telegram Contacts API или использовать сохранённые контакты
    contacts = [
        {"id": 1678352011, "name": "Рома Оленин"},
        {"id": 1678352011, "name": "Оленин Рома"},
        # ... другие контакты
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for contact in contacts:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=contact["name"],
                callback_data=f"choose_contact_{contact["id"]}"
            )
        ])

    await message.answer(
        "Выберите контакт для тестовой отправки:",
        reply_markup=keyboard
    )


@admin_mailing_router.callback_query(F.data.startswith("choose_contact_"))
async def handle_contact_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    from core.bot import bot

    await callback.answer()
    contact_id = int(callback.data.split("_")[-1])
    temp_dir: str = "./temp_mailing_uploads"
    chat_id = contact_id

    # Достаём ID рассылки из состояния
    data = await state.get_data()
    mailing_id = data.get("mailing_id")

    if not mailing_id:
        await callback.answer("Ошибка: ID рассылки не найден.")
        return

    # Получаем содержимое рассылки
    mailing = await orm_get_mailing(session, mailing_id)
    if not mailing:
        await callback.answer(f"Рассылка {mailing_id} не найдена.")
        return

    # 1. Формируем текст сообщения
    text = mailing.message_text or ""  # Если текст пустой — отправляем только файл

    # 2. Проверяем, есть ли файл
    if not mailing.file_blob:
        # Отправляем только текст
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")
        return

    # 3. Создаём временный файл из blob
    try:
        # Создаём папку, если её нет
        os.makedirs(temp_dir, exist_ok=True)

        # Генерируем уникальное имя файла
        ext = mailing.file_local_path.split("/")[-1]
        temp_filename = f"temp_file_{mailing.id}_{int(time.time())}{ext}"
        temp_filepath = os.path.join(temp_dir, temp_filename)

        print(f"temp_filename = {temp_filename}, temp_filepath = {temp_filepath}")

        # Сохраняем blob в файл
        with open(temp_filepath, "wb") as f:
            f.write(mailing.file_blob)

        # 4. Отправляем сообщение с файлом
        document = FSInputFile(temp_filepath)
        await bot.send_document(
            chat_id=chat_id,
            document=document,
            caption=text,  # Текст будет под файлом (как caption)
            parse_mode="HTML"
        )

    except Exception as e:
        # Если ошибка — отправляем хотя бы текст
        if text:
            await bot.send_message(chat_id=chat_id, text=f"{text}\n\n⚠️ Ошибка при отправке файла: {e}", parse_mode="HTML")
        else:
            await bot.send_message(chat_id=chat_id, text=f"⚠️ Ошибка при отправке рассылки: {e}")

    finally:
        # 5. Удаляем временный файл
        try:
            if temp_filepath and os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        except:
            pass 
