from sqlalchemy import DateTime, Date, ForeignKey, Numeric, String, Text, BigInteger, Integer, Boolean, LargeBinary, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    user_first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    specified_name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[int] = mapped_column(Integer, nullable=True)


class ScetchRequest(Base):
    __tablename__ = 'scetch request'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    user_first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[int] = mapped_column(Integer, nullable=False)
    tg_nick: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=True)
    event_date: Mapped[str] = mapped_column(String(30), nullable=False)
    scetch_variant: Mapped[str] = mapped_column(String(50), nullable=False)
    hours_qty: Mapped[float] = mapped_column(Numeric(5,2), nullable=False)
    start_time: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(String(150), nullable=False)


class Mailing(Base):
    __tablename__ = 'mailings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_local_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_blob: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return (f"<Mailing(id={self.id}, name='{self.name}', "
                f"is_sent={self.is_sent})>")
    

class DummyRecipient(Base):
    __tablename__ = 'dummy recipients'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(100))
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    
    # Статус для отслеживания доставки
    is_delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    delivered_at: Mapped[datetime | None] = mapped_column(TIMESTAMP)
    error_message: Mapped[str | None] = mapped_column(Text)