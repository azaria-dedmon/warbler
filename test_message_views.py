"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.uid = 1111
        self.testuser.id = self.uid
        
        self.message = Message(text='I am a test message', user_id=self.testuser.id)
        self.mid = 2222
        self.message.id = self.mid

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_delete_message(self):
        """Can user delete a message?"""
        msg = Message(id=1234, text="Hello world", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/messages/1234/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)


            msg = Message.query.get(1234)
            self.assertIsNone(msg)

    def test_logged_out_message_add(self):
        """Can user add a message if logged out?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9812347528

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('Access unauthorized.', html)
            

    def test_logged_out_message_delete(self):
        """Can user delete a message if logged out?"""
        msg = Message(id=1234, text="Hello world", user_id=self.testuser.id)
        db.session.add(msg)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 10010293

            resp = c.post('/messages/1234/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('Access unauthorized.', html)

    def test_prevent_other_user_message_add(self):
        """Can you prohibit another user from adding a message?"""
        testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        uid2 = 1281231
        testuser2.id = uid2
        msg = Message(id=1234, text="Hello world", user_id=testuser2.id)
        db.session.add_all([testuser2, msg])
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 8567

            resp = c.post("/messages/new", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('Access unauthorized.', html)



    





