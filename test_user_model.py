"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test__repr__(self):
        """Does method work as expected?"""
        self.assertEquals(self.u1.__repr__(), f"<User #{self.u1.id}: {self.u1.username}, {self.u1.email}>")

    def test_is_following(self):
        """Does method detect when user1 is following/not following user2?"""
        self.assertEquals(len(self.u1.following), 0)
        self.u1.following.append(self.u2)
        db.session.commit()
        self.assertEquals(len(self.u1.following), 1)
        self.assertEquals(len(self.u1.following), 1)
        self.u1.following.remove(self.u2)
        db.session.commit()
        self.assertEquals(len(self.u1.following), 0)
    
    def test_is_followed_by(self):
        """Does method detect when user1 is followed/not followed by user2?"""
        self.assertEquals(len(self.u1.followers), 0)
        self.u2.following.append(self.u1)
        db.session.commit()
        self.assertEquals(len(self.u1.followers), 1)
        self.assertEquals(len(self.u1.followers), 1)
        self.u2.following.remove(self.u1)
        db.session.commit()
        self.assertEquals(len(self.u2.following), 0)

    def test_signup(self):
        user = User.signup('me', 'me@aol.com', 'password', None)
        user_id = 99999
        user.id = user_id
        db.session.commit()

        u_test = User.query.get(user.id)
        self.assertEquals(u_test.username, 'me')

    def test_invalid_email_signup(self):
        user = User.signup('me', None, 'password', None)
        user_id = 991010
        user.id = user_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


    def test_authentication(self):
        user = User.signup('me', 'me@aol.com', 'password', None)
        user_id = 99999
        user.id = user_id
        db.session.commit()

        user = User.authenticate('me', 'password')
        db.session.commit()
        self.assertEquals(user.username, 'me')

    def test_invalid_username_authentication(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_invalid_password_authentication(self):
        self.assertFalse(User.authenticate(f"{self.u1.username}", "passwordddd"))



    

