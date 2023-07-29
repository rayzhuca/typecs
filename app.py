from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

import os
from dotenv import load_dotenv

from argon2 import PasswordHasher

import random

load_dotenv()

app = Flask(
    __name__,
    template_folder="templates"
)
app.config["SQLALCHEMY_DATABASE_URI"] =  os.getenv("SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)
ph = PasswordHasher()

class User(db.Model):
    email = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(50))
    password_hash = db.Column(db.String(32))
    runs = db.relationship("Run", cascade="all,delete,delete-orphan", backref="user")

class Run(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order = db.Column(db.Integer)
    wpm = db.Column(db.ARRAY(30, db.Double()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.email'))

def hash_password(password):
    return ph.hash(password)

def login(user, password):
    hash = user.password_hash
    ph.verify(hash, password) # raises exception if wrong password!
    if ph.check_needs_rehash(hash):
        user.password_hash = ph.hash(password)

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
    user = db.get(User, email)
    return user

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
def hello():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
    with app.app_context():
        db.reflect()