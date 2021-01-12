"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


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


class UserViewTestCase(TestCase):
    """Test views for users."""

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

    def test_see_followers_page_for_other_users(self):
        """Can you see the followers pages for any user?"""
        testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        uid2 = 1281231
        testuser2.id = uid2
        db.session.add(testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/users/1281231/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            u = User.query.get(1281231)
            self.assertIsNotNone(u)

    def test_see_following_page_for_other_users(self):
        """Can you see the following pages for any user?"""
        testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        uid2 = 1281231
        testuser2.id = uid2
        db.session.add(testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/users/1281231/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            u = User.query.get(1281231)
            self.assertIsNotNone(u)


    def test_see_followers_page_logged_out(self):
        """Can a logged out user see the follower pages?"""
        testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        uid2 = 1281231
        testuser2.id = uid2
        db.session.add(testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9812347528

            resp = c.get('/users/1281231/followers', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('Access unauthorized.', html)

    def test_see_following_page_logged_out(self):
        """Can a logged out user see the follower pages?"""

        testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        uid2 = 1281231
        testuser2.id = uid2
        db.session.add(testuser2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9812347528

            resp = c.get('/users/1281231/following', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('Access unauthorized.', html)

