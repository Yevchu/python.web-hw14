import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)

class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
        self.mock_user = MagicMock()

    async def test_get_user_by_email_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email='example@email.com', db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email='example@email.com', db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        body = UserModel(
            username='Jhon Doe',
            email='example@mail.com',
            password='password123'
        )
        self.session.add.return_value = None
        self.session.commit.return_value = None
        with unittest.mock.patch('src.repository.users.Gravatar', return_value=MagicMock(get_image=lambda: None)):
            result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.avatar, None)

    async def test_update_token(self):
        token = 'new_token'
        await update_token(user=self.user, token=token, db=self.session)
        self.assertEqual(self.user.refresh_token, token)
        self.session.commit.return_value = None
        self.session.commit.assert_called_once()
    
    async def test_confirmed_email(self):
        self.mock_user.confirmed = False
        async def mock_get_user_by_email(email, db):
            return self.mock_user
        self.session.commit.return_value = None
        with unittest.mock.patch('src.repository.users.get_user_by_email', side_effect=mock_get_user_by_email):
            await confirmed_email(email='example@mail.com', db=self.session)
        self.session.commit.assert_called_once()
        self.assertTrue(self.mock_user.confirmed)

    async def test_update_avatar(self):
        self.mock_user.avatar = None
        async def mock_get_user_by_email(email, db):
            return self.mock_user
        self.session.commit.return_value = None

        with unittest.mock.patch('src.repository.users.get_user_by_email', side_effect=mock_get_user_by_email):
            result = await update_avatar(email='example@mail.com', url='https://example.com/avatar.jpg', db=self.session)
               
        self.assertEqual(self.mock_user.avatar, 'https://example.com/avatar.jpg')
        self.assertEqual(result, self.mock_user)


if __name__ == '__main__':
    unittest.main()