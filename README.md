# simple-chat

A simple chat room application.

## Tech Stack

Python, Flask, Postgres, SQLAlchemy, Javascript, SocketIO, BCrypt, WTForms, HTML, CSS

## To run locally:
### Local dependencies: Python & Postgres

1. Initialize a new virtual environment in the working directory.
   1. `python -m venv venv`
   2. `source venv/bin/activate`
2. Install contents of requirements.txt.
   1. `pip install -r requirements.txt`
3. Create and seed database.
   1. `createdb simple-chat`
   2. `python seed.py`
4. Start application
   1. `flask run`
5. Open your browser and go to "http://127.0.0.1:5000/"

## Notes

- There are two test users you can use for demo purposes. Usernames: "admin" & "mod". Both passwords are "password".
- I recommend running this app in one normal browser, and one incognito browser side by side as different users, to see the full functionality.
