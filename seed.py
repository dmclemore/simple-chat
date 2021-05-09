from models import db, User, Room
from app import app

# Create tables
db.drop_all()
db.create_all()

# Empty tables, just in case
User.query.delete()

# Default User values
user1 = User.signup(username="Admin", password="password")
user2 = User.signup(username="Moderator", password="password")

# General Chat
room1 = Room.create(id="general")

for i in (user1, user2, room1):
    db.session.add(i)

db.session.commit()
