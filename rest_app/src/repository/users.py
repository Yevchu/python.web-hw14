from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel

async def get_user_by_email(email: str, db: Session) -> User:
    """
    Отримання певного юзера за електронною поштою.

    :param email: електрона пошта за якою проводится пошук
    :type email: str
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: повертає юзера
    :rtype: User
    """
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db: Session) -> User:
    """
    Створення нового юзера.

    :param body: інформація про нового юзера
    :type body: UserModel
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    :return: повертає юзера
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def update_token(user: User, token: str | None, db: Session):
    """
    Оновлення ключа доступу.

    :param user: Аутентифікований юзер 
    :type user: User
    :pram token: ключ доступу аутентифікованого юзера
    :type token: str | None
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session):
    """
    Підтвердження електронної пошти.
    
    :param email: електронна пошта для підтвердження
    :type email: str
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email: str, url: str, db: Session):
    """
    Оновлення зображення користувача.
    
    :param email: електронна пошта для отримання юзера
    :type email: str
    :param url: посилання на нове зображення юзера
    :type url: str
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user