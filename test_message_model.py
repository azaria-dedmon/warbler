"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        msg = Message(text='hello world!', user_id=u1.id)
        msg_id = 1121
        msg.id = msg_id

        db.session.add(msg)
        db.session.commit()

        u1 = User.query.get(uid1)
        msg = Message.query.get(msg_id)

        self.u1 = u1
        self.uid1 = uid1
        self.msg = msg
        self.msg_id = msg_id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_add_message(self):
        """Does the model work for adding a user message?"""
        self.assertEqual(len(self.u1.messages), 1)
        db.session.commit()

        msg = Message(text='hello worlddd!', user_id=self.uid1)
        self.u1.messages.append(msg)
        db.session.commit()
        self.assertEqual(len(self.u1.messages), 2)


    def test_no_message_text(self):
        """Does the model work for when there is no message text?"""
        test_message = Message(text=None)
        test_msg_id = 4444
        test_message.id = test_msg_id

        self.u1.messages.append(test_message)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_user_message_likes(self):
        user = User.signup('test', 'test@aol.com', 'password', None)
        user_id = 00000
        user.id = user_id


        msg = Message(text='hello world!', user_id=user.id)
        msg_id = 342
        msg.id = msg_id
        db.session.add(msg)
        db.session.commit()
        like = Likes(user_id=user.id, message_id=msg.id)
        db.session.add(like)
        db.session.commit()

        self.assertEqual(len(user.likes), 1)



       
