import os
import requests
import hashlib

from flask import Flask, session, render_template, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
db = SQLAlchemy()
db.init_app(app)

Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods = ["GET", "POST"])
def index():
    try:
        session['logged_in']
    except:
        session['logged_in'] = False
    return render_template('index.html')

@app.route("/test")
def test():
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "FNNcHf070O64hLKODokItA", "isbns": "9781632168146"})
    session['logged_in'] = False
    return str(session.get('logged_in'))

@app.route("/booksearch")
def booksearch():
    try:
        # books = Booklist.query.all()
        books = db.session.execute("SELECT * FROM books").fetchall()
    except:
        return render_template('error.html', message = "Error in accessing books database")
    return render_template('booksearch.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return render_template('index.html')

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
        # check db
        try:
            user_id = db.session.execute("SELECT id FROM users WHERE username = :username AND password_hash = :password_hash", {'username' : username, 'password_hash' : password_hash}).fetchone()[0]
            session['logged_in'] = user_id
            return render_template('booksearch.html')
        except:
            return render_template('error.html', message = "Incorrect username or password")
    else:
        if not session['logged_in']:
            return render_template('login.html')
        else:
            return render_template('booksearch.html')

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        password_retype = request.form.get('password_retype')
        if not password == password_retype:
            return render_template('error.html', message = "Check retyping password")
        password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
        # adding user to DATABASE
        try:
            db.session.execute("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)", {'username' : username, 'password_hash' : password_hash})
            db.session.commit()
            user_id = db.session.execute("SELECT id FROM users WHERE username = :username", {'username' : username}).fetchone()[0]
            session['logged_in'] = user_id
        except:
            return render_template("error.html", message = "User registration error")
    return render_template("register.html")