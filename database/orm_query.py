import math
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import ScetchRequest, Mailing, DummyRecipient, User


async def orm_add_user(session: AsyncSession, data: dict):
    try:
        user_id = int(data["user_id"])
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        existing_user = result.scalars().first()
        if existing_user is None:
            valid_keys = [col.name for col in User.__table__.columns]
            filtered_data = {
                key: value for key, value in data.items()
                if key in valid_keys
            }
            new_record = User(**filtered_data)
            session.add(new_record)
            await session.commit()

    except Exception as e:
        print(f"Ошибка orm_add_user: {e}")
        await session.rollback()
        
    finally:
        await session.close()


async def orm_get_user(session: AsyncSession, user_id: int):
    try:    
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        existing_user = result.scalars().first()
        return existing_user

    except Exception as e:
        await session.rollback()
        
    finally:
        await session.close()


async def orm_set_user_specified_name(session: AsyncSession, user_id: int, specified_name: str):
    try:
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalars().first()
        if not user:
            print(f"Пользователь с user_id={user_id} не найден")

        user.specified_name = specified_name
        await session.flush()  # отправляем изменения в БД
        await session.commit()  # фиксируем транзакцию

        await session.refresh(user)
        
        return user

    except Exception as e:
        await session.rollback()  # откатываем транзакцию при ошибке
        raise e


async def orm_add_scetch_request(session: AsyncSession, data: dict):
    try:
        valid_keys = [col.name for col in ScetchRequest.__table__.columns]
        filtered_data = {
            key: value for key, value in data.items()
            if key in valid_keys
        }
        new_record = ScetchRequest(**filtered_data)
        session.add(new_record)
        await session.commit()
        await session.refresh(new_record)
        
        return new_record

    except Exception as e:
        print(f"Ошибка: {e}")
        await session.rollback()

    finally:
        await session.close()


async def orm_get_active_mailing_list(session: AsyncSession):
    result = await session.execute(
        select(Mailing).where(Mailing.is_sent == False)
    )
    return result.scalars().all()

    
async def orm_add_mailing(session: AsyncSession):
    new_mailing = Mailing(name="Новая рассылка", message_text="")
    session.add(new_mailing)
    await session.commit()
    await session.refresh(new_mailing)
    return new_mailing


async def orm_get_mailing(session: AsyncSession, mailing_id: int):
    mailing = await session.get(Mailing, mailing_id)
    return mailing


async def orm_delete_mailing(session: AsyncSession, mailing_id: int):
    mailing = await session.get(Mailing, mailing_id)
    if mailing:
        await session.delete(mailing)
        await session.commit()
        return True


async def orm_update_mailing_name(session: AsyncSession, mailing_id: int, new_name: str):
    mailing = await orm_get_mailing(session, mailing_id)
    mailing.name = new_name
    await session.commit()


async def orm_update_mailing_text(session: AsyncSession, mailing_id: int, new_text: str):
    mailing = await orm_get_mailing(session, mailing_id)
    mailing.message_text = new_text
    await session.commit()


async def orm_update_mailing_file(session: AsyncSession, mailing_id: int, new_file_path: str, new_file_blob: bytes):
    mailing = await orm_get_mailing(session, mailing_id)
    mailing.file_local_path = new_file_path
    mailing.file_blob = new_file_blob
    await session.commit()
