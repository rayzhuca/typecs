from flask import Flask, render_template, request, send_file, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

import analytics
import os
from dotenv import load_dotenv

from argon2 import PasswordHasher

import random


load_dotenv()

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="statics"
)
app.debug = True

app.config["SQLALCHEMY_DATABASE_URI"] =  os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
ph = PasswordHasher()

app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "abcdefgheijklmnop"
Session(app)

class User(db.Model):
    email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(50))
    password_hash = db.Column(db.String(128)) 
    runs = db.relationship("Run", cascade="all,delete,delete-orphan", backref="user")

class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer)
    wpm = db.Column(db.ARRAY(db.Float))
    plot = db.Column(db.String(256))

    user_id = db.Column(db.String(100), db.ForeignKey('user.email'))


def hash_password(password):
    return ph.hash(password)

def login(user, password):
    hash = user.password_hash
    try:
        ph.verify(hash, password) 
    except:
        return False
    
    if ph.check_needs_rehash(hash):
        user.password_hash = ph.hash(password)
    
    return True

def user_create(name, email, password):
    if user_get(email):
        return False
    
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
    )

    db.session.add(user)
    db.session.commit()
    return True

def user_get(email):

    user = User.query.filter_by(email=email).first()
    return user

def user_delete(email):
    user = db.get_or_404(User, email)
    db.session.delete(user)
    db.session.commit()

def user_insert_run(user, wpm, plot):
    signed_in = session.get("signed_in", False)

    if signed_in:
        for run in user.runs:
            run.order += 1
            if run.order > 10:
                db.session.delete(run)

        id = random.randint(-10**4, 10**4)
        while Run.query.filter_by(id=id).first():
            id = random.randint(-10**4, 10**4)

        db.session.add(Run(id=id, order=1, wpm=wpm, user=user, plot=plot))
        db.session.commit()

        return True 

    return False


@app.route("/")
def page_index():
    signed_in = session.get("signed_in", False)

    return render_template("index.html", signed_in = signed_in)

@app.route("/doc")
def get_doc():
    lang = request.args.get('lang')
    n = random.randint(1, 10)
    if lang not in {"cpp", "java", "python"}:
        return "invalid language"
    return send_file(f"./statics/docs/{lang}/{n}.txt")

@app.route("/register", methods=["GET", "POST"])
def page_register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        success = user_create(name, email, password)
        if success:
            return "Registration successful!"
        else:
            return "Email already exists. Please use a different email."

    return render_template("registration.html")

@app.route("/stats")
def page_stats():
    user_email = session.get("email")
    user = user_get(user_email)
    return render_template("stats.html", user_email = user_email, user_runs = user.runs)

@app.route("/plot/<filename>")
def serve_plot(filename):
    return send_file(f"./temp/{filename}.png")


@app.route("/login", methods=["GET", "POST"])
def page_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = user_get(email)
        if user and login(user, password):
            session["signed_in"] = True
            session["email"] = email

            return redirect(url_for("page_index"))
        else:
            return "Invalid email or password. Please try again."

    return render_template("login.html")

@app.route("/logrun", methods=["POST"])
def process_log():
    timetable = request.get_json() # [t, {key: 'a', correct: True/False}]
    wpm = analytics.get_wpm(timetable)
    # print(wpm)
    plot = analytics.get_keyboard_plot(timetable)

    user = user_get(session.get("email"))
    user_insert_run(user, wpm, plot) # UNCOMMMENT WHEN READY
    return "Success"

@app.route("/logout")
def page_logout():
    session.pop("signed_in", None)
    session.pop("email", None)
    return redirect(url_for("page_index"))

if __name__ == "__main__":
    # Initializes database
    with app.app_context():
        db.create_all()

    app.run(debug=True)
