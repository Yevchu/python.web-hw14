from typing import Optional

from jose import JWSError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    """
    Клас для роботи з автентифікацією юзера.
    :param pwd_context: управління налаштуваннями та методами шифрування паролів
    :param SECRET_KEY: секретний ключ
    :param ALGORITHM: алгорист шифрування
    :param oauth2_scheme: це клас з бібліотеки FastAPI, який використовується для створення аутентифікаційної схеми OAuth2 для захисту API-маршрутів
    """
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')

    def verify_password(self, plain_password, hashed_password):
        """
        Первірка паролю
        :param self: посилання на поточний об'єкт класу
        :param plain_password: поточний пароль
        :param hashed_password: хешований(закодований) пароль
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str):
        """
        Отримання хешу пароля.

        :param self: посилання на поточний об'єкт класу
        :param password: пароль для якого треба отримати хеш
        """
        return self.pwd_context.hash(password)
    
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Створення ключа доступу

        :param self: посилання на поточний об'єкт класу
        :param data: інформація надана користувачем\програмою
        :type data: dict
        :param expires_delta: термін(час) інсування(життя) поточного ключа доступу
        :type expires_delta: Optional[float] = None
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Створення ключа оновлення доступу

        :param self: посилання на поточний об'єкт класу
        :param data: інформація надана користувачем\програмою
        :type data: dict
        :param expires_delta: термін(час) інсування(життя) поточного ключа оновлення доступу
        :type expires_delta: Optional[float] = None
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token
    
    async def decode_refresh_token(self, refresh_token: str):
        """
        Розшифрування ключа оновлення доступу

        :param self: посилання на поточний об'єкт класу
        :param refresh_token: ключ оновлення доступу
        :type refresh_token: str
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWSError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
        
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Отримання поточного юзера.

        :param self: посилання на поточний об'єкт класу
        :param token: ключ доступу користувача
        :type token: str
        :param db: База даниз з яких отримуємо данні
        :type db: Session
        """
        credentials_exeption = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'}
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exeption
            else:
                raise credentials_exeption
        except JWSError as e:
            raise credentials_exeption
        
        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exeption
        return user 
    
    def create_email_token(self, data: dict):
        """
        Створення ключа доступу для електронної пошти

        :param self: посилання на поточний об'єкт класу
        :param data: інформація надана користувачем\програмою
        :type data: dict
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    async def get_email_from_token(self, token: str):
        """
        Отримання електронної пошти за ключем доступу

        :param self: посилання на поточний об'єкт класу
        :param token: ключ доступу
        :type data: str
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload['sub']
            return email
        except JWSError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Invalid token for email verification')
        
auth_service = Auth()
