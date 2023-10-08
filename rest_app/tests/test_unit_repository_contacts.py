import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from datetime import date

from src.database.models import Contact, User
from src.schemas import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact_by_first_name,
    get_contact_by_last_name,
    get_contact_by_email,
    upcoming_birthday,
    update_contact,
    create_contact,
    delete_contact
)

class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_fn_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_first_name(contact_first_name='Vitaliy', user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contacts_by_fn_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_first_name(contact_first_name='Vitaliy', user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contacts_by_ln_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_last_name(contact_last_name='Yevchu', user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contacts_by_ln_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_last_name(contact_last_name='Yevchu', user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_contacts_by_email_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_email(contact_email='evciu97@gmail.com', user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contacts_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_email(contact_email='evciu97@gmail.com', user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_upcomin_birthday(self):
        contacts = [Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await upcoming_birthday(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactModel(first_name='Vitaliy', 
                            last_name='Yevchu', 
                            email='evciu97@gmail.com', 
                            birthday=date(1997,6,19), 
                            description='some text')
        self.session.add.return_value = None
        self.session.commit.return_value = None
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.description, body.description)      
        self.assertTrue(hasattr(result, 'id'))

    async def test_update_contact_found(self):
        body = ContactModel(first_name='Vitaliy', 
                    last_name='Yevchu', 
                    email='evciu97@gmail.com', 
                    birthday=date(1997,6,19), 
                    description='some text')
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)
    
    async def test_update_contact_not_found(self):
        body = ContactModel(first_name='Vitaliy', 
                    last_name='Yevchu', 
                    email='evciu97@gmail.com', 
                    birthday=date(1997,6,19), 
                    description='some text')
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.delete.return_value = None
        self.session.commit.return_value = None
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)
    
    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()