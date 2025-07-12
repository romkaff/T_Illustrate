from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, BigInteger, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


######################################################################################################
###############################   Приглашения   ######################################################
######################################################################################################

# Шаблоны
class InvTemplate(Base):
    __tablename__ = 'inv template'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(50), nullable=False)
    image: Mapped[str] = mapped_column(Text, nullable=True)


class Portfolio(Base):
    __tablename__ = 'portfolio'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(50), nullable=True)
    image: Mapped[str] = mapped_column(Text, nullable=False)    


# Заказ приглашения
class InvOrder(Base):
    __tablename__ = 'inv order'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    personal: Mapped[str] = mapped_column(String(30), nullable=False)
    finish_type: Mapped[str] = mapped_column(String(30), nullable=False)
    template_type: Mapped[str] = mapped_column(String(30), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    preliminary_price: Mapped[float] = mapped_column(Numeric(5,2), nullable=True)
    addressing: Mapped[str] = mapped_column(String(100), nullable=True)
    text_invitation: Mapped[str] = mapped_column(String(200), nullable=False)
    inv_template_id: Mapped[int] = mapped_column(nullable=True)
    self_template_description: Mapped[str] = mapped_column(String(200), nullable=True)
    contact_wish_addressing: Mapped[str] = mapped_column(String(100), nullable=True)
    wish_date: Mapped[str] = mapped_column(String(10), nullable=True)
    confirmed: Mapped[bool] = mapped_column(default=False)
    final_price: Mapped[float] = mapped_column(Numeric(5,2), nullable=True)


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str]  = mapped_column(String(150), nullable=True)
    phone: Mapped[str]  = mapped_column(String(13), nullable=True)


class Payment(Base):
    __tablename__ = 'payment'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    order_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(5,2), nullable=False)
    check_image: Mapped[str] = mapped_column(Text, nullable=True)


class EventOrder(Base):
    __tablename__ = 'event order'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    handing_type: Mapped[str] = mapped_column(String(20), nullable=False)
    execution_type: Mapped[str] = mapped_column(String(30), nullable=False)
    akva_brand: Mapped[bool] = mapped_column(default=False)
    what_to_hand_over: Mapped[str] = mapped_column(String(10), nullable=False)
    guests_qty: Mapped[int] = mapped_column(nullable=False)
    hours_qty: Mapped[float] = mapped_column(Numeric(5,2), nullable=False)
    no_time_reaction: Mapped[str] = mapped_column(String(15), nullable=False)
    event_place: Mapped[str] = mapped_column(String(150), nullable=False)
    need_agreement: Mapped[bool] = mapped_column(default=False)
    amount: Mapped[float] = mapped_column(Numeric(5,2), nullable=False)
    prepayment_made: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)