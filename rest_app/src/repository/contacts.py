from typing import List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import Contact, User
from src.schemas import ContactModel

async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Поветрає список контактів з бази даних, маємо можливіть пагінації списку

    :param skip: Скільки контактів пропустити з початку бази даних 
    :type skip: int
    :param limit: Кількість контактів на одній сторінці пагінації 
    :type limit: int
    :param user: Аутентифікований юзер 
    :type user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: Повертає списов контактів
    :rtype: List[Contacts]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()

async def get_contact_by_first_name(contact_first_name: str, user: User, db: Session) -> Contact:
    """
    Повертає певний контакт за ім'ям. 

    :param contact_first_name: Ім'я для пошуку
    :type contact_first_name: str
    :param user: Аутентифікований юзер 
    :type user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: Повертає контакт за ім'ям
    :rtype: Contact
    """
    return db.query(Contact).filter(and_(Contact.first_name == contact_first_name, Contact.user_id == user.id)).first()

async def get_contact_by_last_name(contact_last_name: str, user: User, db: Session) -> Contact:
    """
    Повертає певний контакт за прізвищем. 

    :param contact_last_name: Прізвище для пошуку
    :type contact_last_name: str
    :param user: Аутентифікований юзер 
    :type user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: Повертаж контакт за прізвищем
    :rtype: Contact
    """
    return db.query(Contact).filter(and_(Contact.last_name == contact_last_name, Contact.user_id == user.id)).first()

async def get_contact_by_email(contact_email: str, user: User, db: Session) -> Contact:
    """
    Повертає певний контакт за електроною поштою. 

    :param contact_email: Електрона пошта для пошуку
    :type contact_email: str
    :param user: Аутентифікований юзер 
    :type user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: Повертаж контакт за електроною поштою
    :rtype: Contact
    """
    return db.query(Contact).filter(and_(Contact.email == contact_email, Contact.user_id == user.id)).first()

async def upcoming_birthday(user: User, db: Session) -> List[Contact]:
    """
    Повертає список контактів в яких день народженя в межах тижня від поточної дати. 

    :param user: Аутентифікований юзер 
    :type user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: Повертає список контактів в яких день народженя в межах тижня від поточної дати.
    :rtype: List[Contacts]
    """
    today = datetime.today().date()
    end_date = today + timedelta(days=7)
    return db.query(Contact).filter(and_(Contact.birthday >= today, Contact.birthday <= end_date, Contact.user_id == user.id)).all()

async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Створення нового контакту.

    :param body: Інформація про контакт який треба створити
    :type body: ContactModel
    :param user: Аутентифікований юзер 
    :type user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: Повертає створений контакт 
    :rtype: Contact
    """
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        birthday=body.birthday,
        description=body.description,
        user_id=user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:
    """
    Редагування інформації про певний контакт. 

    :param contact_id: ID контакта інформацію якого треба змінити
    :type contact_id: int
    :param body: Інформація надана користувачем про певний контакт
    :type body: ContactModel
    :param user: Аутентифікований юзер 
    :type user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: Повертає відредагований контакт або None
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.birthday = body.birthday
        contact.description = body.description
        db.commit()
    return contact

async def delete_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Видалення певного контакту з бази данних.

    :param contact_id: ID контакта який треба видалити
    :type contact_id: int
    :param user: Аутентифікований юзер 
    :type user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: Повертає видалений контакт або None
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact