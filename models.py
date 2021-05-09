from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect the database to the given Flask app"""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User model"""

    __tablename__ = "users"

    username = db.Column(
        db.String(20),
        primary_key=True
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    @classmethod
    def signup(cls, username, password):
        """Sign up user. Hashes password and adds user to database."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Check for valid username & password combo"""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Room(db.Model):
    """Chat Room model"""

    __tablename__ = "rooms"

    id = db.Column(
        db.String(20),
        primary_key=True
    )

    password = db.Column(
        db.Text
    )

    population = db.Column(
        db.Integer,
        default=0
    )

    is_private = db.Column(
        db.Boolean,
        nullable=False
    )

    @classmethod
    def create(cls, id, password=None, is_private=False):
        """Creates a Room. If there's a password, hashes password."""

        if password is not None:
            hashed_pwd = bcrypt.generate_password_hash(
                password).decode('UTF-8')
            room = Room(
                id=id.lower(),
                password=hashed_pwd,
                is_private=is_private
            )
        else:
            room = Room(
                id=id.lower(),
                is_private=is_private
            )

        db.session.add(room)
        return room

    @classmethod
    def authenticate(cls, id, password):
        """Check for valid room id & password combo"""

        room = cls.query.filter_by(id=id).first()

        if room:
            is_auth = bcrypt.check_password_hash(room.password, password)
            if is_auth:
                return room

        return False
