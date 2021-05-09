from flask import Flask, render_template, session, g, flash, redirect
from models import db, connect_db, User, Room
from forms import LoginForm, SignupForm, NewRoomForm, RoomForm
from flask_socketio import SocketIO, join_room, leave_room
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///simple-chat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "this-is-secret"

connect_db(app)
socketio = SocketIO(app)

CURR_USER = "curr_user"
CURR_ROOM = "curr_room"

if __name__ == "__main__":
    socketio.run(app)


@app.before_request
def add_user_to_g():
    """Before each request, check if we are logged in. If we are, add curr user to Flask global."""

    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])

    else:
        g.user = None


@app.route("/")
def home():
    """Show a list of all available chat rooms."""

    # If no one is logged in, show the anon home page.
    if not g.user:
        return render_template("home-anon.html")

    rooms = Room.query.all()

    return render_template("home.html", rooms=rooms)


@app.route("/room/new", methods=["GET", "POST"])
def new_room():
    """Show the new room form. On submit, create and go to the new room."""

    # If no one is logged in, show the anon home page.
    if not g.user:
        return render_template("home-anon.html")

    form = NewRoomForm()

    # If conditional will return true when the form submits a response
    if form.validate_on_submit():
        try:
            if form.password.data:
                room = Room.create(
                    form.id.data,
                    form.password.data,
                    is_private=True
                )
            else:
                room = Room.create(
                    form.id.data
                )
            db.session.commit()
            return redirect(f"/room/{room.id}")

        except IntegrityError:
            flash("Room Name already taken", "danger")
            return render_template("/room/new-room.html", form=form)

        except:
            flash("Something went wrong. Try again!", "danger")
            return render_template("/room/new-room.html", form=form)

    return render_template("/room/new-room.html", form=form)


@app.route("/room/<room_id>")
def room(room_id):
    """Show the room with name of room_id."""

    # If no one is logged in, show the anon home page.
    if not g.user:
        return render_template("home-anon.html")

    room = Room.query.filter_by(id=f"{room_id}").first()

    return render_template("/room/room.html", user=g.user, room=room)


@app.route("/room/<room_id>/password", methods=["GET", "POST"])
def room_password(room_id):
    """Show the password form. Authenticate the password for the room with id of room_id."""

    # If no one is logged in, show the anon home page.
    if not g.user:
        return render_template("home-anon.html")

    form = RoomForm()

    # If conditional will return true when the form submits a response
    if form.validate_on_submit():
        room = Room.authenticate(id=room_id, password=form.password.data)
        if room:
            return redirect(f"/room/{room.id}")

        flash("Invalid credentials.", 'danger')

    return render_template("/room/password.html", form=form)


############### LOGIN/LOGOUT/SIGNUP ###############


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    # If conditional will return true when the form submits a response
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('/user/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Goodbye!", "success")
    return redirect("/")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user login."""

    form = SignupForm()

    # If conditional will return true when the form submits a response
    if form.validate_on_submit():
        try:
            user = User.signup(form.username.data,
                               form.password.data)
            db.session.commit()
            do_login(user)
            flash(f"Welcome to WatchParty!", "success")
            return redirect("/")

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("/user/signup.html", form=form)

        except:
            flash("Something went wrong. Try again!", "danger")
            return render_template("/room/new-room.html", form=form)

    return render_template("/user/signup.html", form=form)


############### SOCKET EVENTS ###############


@socketio.on("join")
def handle_room_join(data):
    """Handle the socket connection event."""

    # Assign the passed room to the session, and join the socket room.
    session[CURR_ROOM] = data["room"]
    join_room(session[CURR_ROOM])

    # Change the room's population in the database.
    room = Room.query.filter_by(id=session[CURR_ROOM]).first()
    room.population += 1
    db.session.commit()

    # Emit a connection message to the room's chat.
    socketio.emit("renderMessage", {
        "username": "[SYSTEM]",
        "message": f"{session[CURR_USER]} has connected."
    }, to=session[CURR_ROOM])


@socketio.on("disconnect")
def handle_disconnection():
    """Handle the socket disconnection event."""

    # Emit a disconnection message to the user's current room chat.
    socketio.emit("renderMessage", {
        "username": "[SYSTEM]",
        "message": f"{session[CURR_USER]} has disconnected."
    }, to=session[CURR_ROOM])

    # Change the room's population in the database.
    room = Room.query.filter_by(id=session[CURR_ROOM]).first()
    room.population -= 1
    if room.population == 0 and room.id != "general":
        db.session.delete(room)
    db.session.commit()

    # Remove the socket from the room, and remove the room from the session.
    leave_room(session[CURR_ROOM])
    if CURR_ROOM in session:
        del session[CURR_ROOM]


@socketio.on("send_chat")
def handle_send_chat(data):
    """Handle the socket send_chat event."""

    # Call the client-side renderMessage socket event. Will relay the message data.
    socketio.emit("renderMessage", data, to=session[CURR_ROOM])


############### HELPERS ###############


def do_login(user):
    """Log in user."""

    # Add user to session
    session[CURR_USER] = user.username


def do_logout():
    """Logout user."""

    # Remove user from session
    if CURR_USER in session:
        del session[CURR_USER]
