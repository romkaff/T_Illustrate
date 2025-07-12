import math
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import InvTemplate, InvOrder, User, Payment, EventOrder, Portfolio


###############################################################################################################
################################   Админка   ##################################################################
###############################################################################################################

###############################################################################################################
################################   Заказы Мероприятий   #######################################################
###############################################################################################################

async def orm_add_event_order(session: AsyncSession, data: dict):
    order = EventOrder(
        event_date=data['event_date'],
        handing_type=data['handing_type'],
        execution_type=data['execution_type'],
        akva_brand=data['akva_brand'],
        what_to_hand_over=data['what_to_hand_over'],
        guests_qty=data['guests_qty'],
        hours_qty=data['hours_qty'],
        no_time_reaction=data['no_time_reaction'],
        event_place=data['event_place'],
        need_agreement=data['need_agreement'],
        amount=data['amount'],
        prepayment_made=data['prepayment_made'],
        user_id=data['user_id'],
    )
    session.add(order)
    await session.commit()

    query = select(EventOrder).order_by(desc(EventOrder.id))
    result = await session.execute(query)
    order = result.scalar()
    return order.id


###############################################################################################################
################################   Приглашения - заказы   #####################################################
###############################################################################################################

# Добавить заказ приглашения
async def orm_add_invitation_order(session: AsyncSession, data: dict):
    order = InvOrder(
        user_id=data['user_id'],
        personal=data['personal'],
        finish_type=data['finish_type'],
        template_type=data['template_type'],
        quantity=data['quantity'],
        preliminary_price=data['preliminary_price'],
        addressing=data['addressing'],
        text_invitation=data['text_invitation'],
        inv_template_id=data['inv_template_id'],
        contact_wish_addressing=data['contact_wish_addressing'],
        wish_date=data['wish_date'],
        final_price=data['final_price'],
        confirmed=data['confirmed']
    )
    session.add(order)
    await session.commit()

    query = select(InvOrder).order_by(desc(InvOrder.id))
    result = await session.execute(query)
    order = result.scalar()
    return order.id


async def orm_add_user(session: AsyncSession, data: dict):
    query = select(User).where(User.user_id == data['user_id'])
    result = await session.execute(query)
    if result.first():
        return 
       
    user = User(
        user_id=data['user_id'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    session.add(user)
    await session.commit()

async def orm_add_payment(session: AsyncSession, data: dict):
    payment = Payment(
        user_id=data['user_id'],
        order_id=data['order_id'],
        amount=data['amount'],
        check_image=data['check_image']
    ) 
    session.add(payment)
    await session.commit()


# Получить шаблоны пригласительных
async def orm_get_inv_orders(session: AsyncSession, user_id: int):
    print(f'USER ID = {user_id}')
    
    query = select(InvOrder).where(InvOrder.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()





###############################################################################################################
################################   Приглашения - шаблоны   ####################################################
###############################################################################################################

# Получить шаблоны пригласительных
async def orm_get_inv_templates(session: AsyncSession):
    query = select(InvTemplate)
    result = await session.execute(query)
    return result.scalars().all()

# Добавить шаблон
async def orm_add_inv_template(session: AsyncSession, data: dict):
    template = InvTemplate(
        description=data['description'],
        image=data['image'],
    )
    session.add(template)
    await session.commit()

# Удалить шаблон
async def orm_del_inv_template(session: AsyncSession, id: int):
    query = delete(InvTemplate).where(InvTemplate.id == id)
    await session.execute(query)
    await session.commit()

# Получить шаблон по его id
async def orm_get_inv_template(session: AsyncSession, id: int):
    query = select(InvTemplate).where(InvTemplate.id == id)
    result = await session.execute(query)
    return result.scalar()

# Следующий шаблон
async def orm_next_inv_template(session: AsyncSession, id: int):
    query = select(InvTemplate).where(InvTemplate.id > id).order_by(InvTemplate.id)
    result = await session.execute(query)
    return result.scalar()

# Предыдущий шаблон
async def orm_prev_inv_template(session: AsyncSession, id: int):
    query = select(InvTemplate).filter(InvTemplate.id < id).order_by(desc(InvTemplate.id))
    result = await session.execute(query)
    return result.scalar()


###############################################################################################################
################################   Мое портфолио   ############################################################
###############################################################################################################

# Получить портфолио (все скетчи)
async def orm_get_poftfolio_all(session: AsyncSession):
    query = select(Portfolio)
    result = await session.execute(query)
    return result.scalars().all()

# Добавить скетч
async def orm_add_scetch(session: AsyncSession, data: dict):
    scetch = Portfolio(
        description=data['description'],
        image=data['image'],
    )
    session.add(scetch)
    await session.commit()

# Удалить скетч
async def orm_del_scetch(session: AsyncSession, id: int):
    query = delete(Portfolio).where(Portfolio.id == id)
    await session.execute(query)
    await session.commit()

# Получить скетч по его id
async def orm_get_scetch(session: AsyncSession, id: int):
    query = select(Portfolio).where(Portfolio.id == id)
    result = await session.execute(query)
    return result.scalar()

# Следующий скетч
async def orm_next_scetch(session: AsyncSession, id: int):
    query = select(Portfolio).where(Portfolio.id > id).order_by(Portfolio.id)
    result = await session.execute(query)
    return result.scalar()

# Предыдущий скетч
async def orm_prev_scetch(session: AsyncSession, id: int):
    query = select(Portfolio).filter(Portfolio.id < id).order_by(desc(Portfolio.id))
    result = await session.execute(query)
    return result.scalar()












'''
############### Работа с баннерами (информационными страницами) ###############

async def orm_add_banner_description(session: AsyncSession, data: dict):
    #Добавляем новый или изменяем существующий по именам
    #пунктов меню: main, about, cart, shipping, payment, catalog
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description) for name, description in data.items()]) 
    await session.commit()


async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


############################ Категории ######################################

async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_create_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories]) 
    await session.commit()

############ Админка: добавить/изменить/удалить товар ########################

async def orm_add_product(session: AsyncSession, data: dict):
    obj = Product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
    )
    session.add(obj)
    await session.commit()


async def orm_get_products(session: AsyncSession, category_id):
    query = select(Product).where(Product.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = (
        update(Product)
        .where(Product.id == product_id)
        .values(
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            image=data["image"],
            category_id=int(data["category"]),
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()

##################### Добавляем юзера в БД #####################################

async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone)
        )
        await session.commit()


######################## Работа с корзинами #######################################

async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1))
        await session.commit()



async def orm_get_user_carts(session: AsyncSession, user_id):
    query = select(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id)
        await session.commit()
        return False

'''
