from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()

@router.post('/signup',response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_task: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Регістрація новогою юзера.

    :param body: Інформація про нового користувача
    :type boby: UserModel
    :param background_task: фонове відправлення повідомлення для підтверження юзера
    :type background_task: BackgroundTasks
    :param request: Http запит
    :type request: Request
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user: 
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_task.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {'user': new_user, 'detail': 'User successfully created'}

@router.post('/login', response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Авторизація юзера.

    :param body: Інформація для авторизації юзера
    :type boby: OAuth2PasswordRequestForm = Depends()
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email')
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')
    
    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Оновлення ключа доступу для юзера

    :param credentials: Інформація про певного юзера
    :type credentials: HTTPAuthorizationCredentials = Security(security)
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Підтвердження електронної пошти користувача за ключем доступу.

    :param token: ключ доступу користувача
    :type credentials: str
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification failed/error')
    if user.confirmed:
        return {'message': 'Your email already confirmed'}
    await repository_users.confirmed_email(email, db)
    return {'message': 'Email confirmed'}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_task: BackgroundTasks, request: Request, db: Session=Depends(get_db)):
    """
    Надсилання листа для користувача.

    :param body: електронна пошта
    :type boby: RequestEmail
    :param background_task: фонове відправлення повідомлення для підтверження юзера
    :type background_task: BackgroundTasks
    :param request: Http запит
    :type request: Request
    :param db: База даниз з яких отримуємо данні
    :type db: Session
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {'message': 'Your email already confirmed'}
    if user: 
        background_task.add_task(send_email, user.email, user.username, request.base_url)
    return {'message': 'Check your email for confirmation.'}