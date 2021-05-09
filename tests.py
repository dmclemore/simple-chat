from unittest import TestCase
from app import app, do_login, do_logout
from models import db, User, Room

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///simple-chat_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['WTF_CSRF_ENABLED'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()


USER = {
    "username": "test",
    "password": "password",
}

USER_2 = {
    "username": "test_2",
    "password": "password",
}

ROOM = {
    "id": "test_room",
    "password": "test",
    "is_private": True
}

ROOM_2 = {
    "id": "test_room-2",
    "password": "test",
    "is_private": True
}


class AppRouteTests(TestCase):
    """Tests for routes of app."""

    def setUp(self):
        """Make demo data."""

        User.query.delete()
        Room.query.delete()

        user = User.signup(**USER)
        room = Room.create(**ROOM)
        db.session.add_all([user, room])
        db.session.commit()

        self.user = user
        self.room_id = room.id

    def tearDown(self):
        """Clean up tests."""

        db.session.rollback()

    def test_home_anon(self):
        """Test not logged in home route."""

        with app.test_client() as client:
            res = client.get("/")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<span class="display-3">Welcome to Chat Rooms</span>', html)

    def test_home(self):
        """Test logged in home route."""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['curr_user'] = self.user.username

            res = client.get("/")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<span class="col">{self.room_id.capitalize()}</span>', html)
            self.assertIn(
                f'<button class="btn btn-success w-50">Create A Room</button>', html)

    def test_new_room_get(self):
        """Test new room get request."""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['curr_user'] = self.user.username

            res = client.get("/room/new")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<h2>New Room</h2>', html)
            self.assertIn(
                f'<input class="form-control my-3" id="id" name="id" placeholder="Room Name" required type="text" value="">', html)
            self.assertIn(
                f'<button class="btn btn-danger btn-block w-50 m-auto">Create Room</button>', html)

    def test_new_room_post(self):
        """Test new room post request."""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['curr_user'] = self.user.username

            res = client.post("/room/new", data=ROOM_2, follow_redirects=True)
            room = Room.query.filter_by(id=ROOM_2["id"]).first()
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<h2>{ROOM_2["id"].capitalize()}</h2>', html)
            self.assertIn(
                f'<button class="btn btn-danger" type="button" id="chat-submit">Send</button>', html)

    def test_room(self):
        """Test individual room route."""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['curr_user'] = self.user.username

            res = client.get(f"/room/{self.room_id}")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<h2>{self.room_id.capitalize()}</h2>', html)
            self.assertIn(
                f'<input type="hidden" id="chat-user" value="{self.user.username}">', html)

    def test_room_password_get(self):
        """Test private room password get request."""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['curr_user'] = self.user.username

            res = client.get(f"/room/{self.room_id}/password")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<h2>Enter Password:</h2>', html)
            self.assertIn(
                f'<input class="form-control my-3" id="password" name="password" placeholder="Password" required type="password" value="">', html)
            self.assertIn(
                f'<button class="btn btn-danger btn-block w-50 m-auto">Join Room</button>', html)

    def test_room_password_post(self):
        """Test private room password post request."""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['curr_user'] = self.user.username

            data = {"password": "test"}
            res = client.post(
                f"/room/{self.room_id}/password", data=data, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<h2>{self.room_id.capitalize()}</h2>', html)
            self.assertIn(
                f'<button class="btn btn-danger" type="button" id="chat-submit">Send</button>', html)

    def test_user_login_get(self):
        """Test user login get request."""

        with app.test_client() as client:

            res = client.post(
                f"/login")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<h2>Welcome back</h2>', html)
            self.assertIn(
                f'<input class="form-control my-3" id="username" name="username" placeholder="Username" required type="text" value="">', html)
            self.assertIn(
                f'<button class="btn btn-danger btn-block w-50 m-auto">Log in</button>', html)

    def test_user_login_post(self):
        """Test user login post request."""

        with app.test_client() as client:

            data = {"username": "test", "password": "password"}
            res = client.post(
                f"/login", data=data, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<span class="col">{self.room_id.capitalize()}</span>', html)
            self.assertIn(
                f'<button class="btn btn-success w-50">Create A Room</button>', html)

    def test_user_signup_get(self):
        """Test user signup get request."""

        with app.test_client() as client:

            res = client.post(
                f"/signup")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<h2>Create an Account</h2>', html)
            self.assertIn(
                f'<input class="form-control my-3" id="password" name="password" placeholder="Password" required type="password" value="">', html)
            self.assertIn(
                f'<button class="btn btn-danger btn-block w-50 m-auto">Sign Up</button>', html)

    def test_user_signup_post(self):
        """Test user login post request."""

        with app.test_client() as client:

            res = client.post(
                f"/signup", data=USER_2, follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(
                f'<span class="col">{self.room_id.capitalize()}</span>', html)
            self.assertIn(
                f'<button class="btn btn-success w-50">Create A Room</button>', html)
