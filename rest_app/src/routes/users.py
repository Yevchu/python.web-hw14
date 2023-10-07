from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb

router = APIRouter(prefix='/users', tags=['users'])

@router.get('/me/', response_model=UserDb)
async def read_user_me(current_user: UserDb = Depends(auth_service.get_current_user)):
    """
    Отримання поточного юзера.
    :param current_user: поточний автентифікований юзер
    :type current_user: UserDb
    :return: поточний автентифікований юзер
    :rtype: UserDb
    """
    return current_user

@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    Оновлення зображення юзера.

    :param file: файл для нового зображення юзера.
    :type file: UploadFile
    :param current_user: Аутентифікований юзер 
    :type current_user: User
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'RestApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'RestApp/{current_user.username}')\
                        .build_url(width=250, heigth=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user