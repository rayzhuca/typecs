from flask import Flask, render_template, request, request, send_file
from flask_sqlalchemy import SQLAlchemy

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
app.config["SQLALCHEMY_DATABASE_URI"] =  os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
ph = PasswordHasher()

class User(db.Model):
    email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(50))
    password_hash = db.Column(db.String(128)) 
    runs = db.relationship("Run", cascade="all,delete,delete-orphan", backref="user")

class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer)
    wpm = db.Column(db.ARRAY(db.Float))
    user_id = db.Column(db.String(100), db.ForeignKey('user.email'))


def hash_password(password):
    return ph.hash(password)

def login(user, password):
    hash = user.password_hash
    ph.verify(hash, password) # raises exception if wrong password!
    if ph.check_needs_rehash(hash):
        user.password_hash = ph.hash(password)
    
    return True

# return value = success 
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
    if user:
        return user
    else:
        return None

def user_delete(email):
    user = db.get_or_404(User, email)
    db.session.delete(user)
    db.session.commit()

def user_insert_run(user, wpm):
    for run in user.runs:
        run.order += 1
        if run.order > 10:
            db.session.delete(run)

    id = random.randint(-10**18, 10**18)
    while db.get(Run, id):
        id = random.randint(-10**18, 10**18)
    db.session.add(Run(id, 1, wpm, user))
    db.session.commit()


@app.route("/")
def page_index():
    return render_template("index.html")

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

@app.route("/login", methods=["GET", "POST"])
def page_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = user_get(email)
        if user and login(user, password):
            return "Login successful!"
        else:
            return "Invalid email or password. Please try again."

    return render_template("login.html")


@app.route("/logrun", methods=["POST"])
def process_log():
    timetable = request.get_json() # [t, {key: 'a', correct: True/False}]
    cps = [0] * 30 # characters per second
    for [t, stamp] in timetable:
        if stamp["correct"]:
            cps[min(int(t), 29)] += 1
    wpm = [(60 * x) / 4.7 for x in cps] #4.7 is the average length of a word
    print(wpm)
    # user_insert_run() # UNCOMMMENT WHEN READY
    return "Success"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
