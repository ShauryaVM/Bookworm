import os
import gunicorn
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column
from flask import Flask, flash, redirect, render_template, request, session
from functools import wraps
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///bookworm.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Session(app)

db = SQLAlchemy(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    user = db.session.execute(text("SELECT * from 'users' where 'users'.id = ?"), params=[session["user_id"]])
    goal = user[0]["goal"]
    read = user[0]["#_of_books_read"]
    if goal is None:
        goal = 0
    elif read is None:
        read = 0
    away = goal - read
    books = db.session.execute(text("SELECT * from 'books' where title not in (SELECT 'books'.title from 'books' join reviews on reviews.title='books'.title join 'users' on 'users'.id=reviews.user where 'users'.id = ?)"), params=[session["user_id"]])
    reviews = db.session.execute(text("SELECT * from reviews where title not in (SELECT 'books'.title from 'books' join reviews on reviews.title='books'.title join 'users' on 'users'.id=reviews.user where 'users'.id = ?)"), params=[session["user_id"]])
    def find_reviews(title):
        book_reviews = []
        for review in reviews:
            if review["title"] == title:
                book_reviews.append(review["user_review"])
        return book_reviews
    return render_template("index.html", goal=goal,awayfromgoal=away,suggestions=books, reviews=reviews, find=find_reviews)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("apology.html", message="Must provide username")
        if not request.form.get("password"):
            return render_template("apology.html", message="Must provide password")
        user = db.session.execute(text("SELECT * from 'users' WHERE username = ?"), params=[request.form.get("username")])
        if len(user) != 1 or not check_password_hash(user[0]["hash"], request.form.get("password")):
            return render_template("apology.html", message="Invalid credentials given: please try again or click Forgot Password")
        session["user_id"] = user[0]["id"]

        if (user[0]["goal"] is None):
            return redirect("/goal")

        if request.form.get("password") == "bookworm":
            return render_template("change.html")
        else:
            return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("apology.html", message="Must provide username")

        usernamecheck = db.session.execute(text("SELECT * FROM 'users' WHERE username like ?"), params=[request.form.get("username")])
        if len(usernamecheck) == 1:
            return render_template("apology.html", message="Username already exists")

        elif not request.form.get("password"):
            return render_template("apology.html", message="Must provide password")

        elif not (request.form.get("password") == request.form.get("confirmation")):
            return render_template("apology.html", message="Passwords do not match")

        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=10)
        db.session.execute(text("INSERT INTO 'users'(username, hash) VALUES(?, ?)"),params=[username, password])

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        resetpass = generate_password_hash("bookworm", method='pbkdf2:sha256', salt_length=10)
        db.session.execute(text("UPDATE 'users' SET hash = ? where username = ?"), params=[resetpass, request.form.get("username")])

        return redirect("/")

    else:
        return render_template("forgot.html")

@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "POST":
        if(request.form.get("newpass") != request.form.get("confirmnew")):
            return render_template("apology.html", message="Passwords do not match")
        newpassword = request.form.get("newpass")
        newpasswordsecure = generate_password_hash(newpassword, method='pbkdf2:sha256', salt_length=10)
        db.session.execute(text("UPDATE 'users' SET hash = ? where id = ?"), params=[newpasswordsecure, session["user_id"]])

        return redirect("/")
    else:
        return render_template("change.html")

@app.route("/goal", methods=["GET", "POST"])
@login_required
def goal():
    if request.method == "POST":
        if(int(request.form.get("goal")) <= 0):
            return render_template("apology.html", message="Invalid number of books")
        db.session.execute(text("UPDATE 'users' SET 'goal' = ? where id = ?"), params=[int(request.form.get("goal")), session["user_id"]])
        return redirect("/")
    else:
        return render_template("goal.html")

@app.route("/form", methods=["GET","POST"])
@login_required
def form():
    if request.method == "POST":
        db.session.execute(text("INSERT INTO reviews VALUES(?,?,?)"),params=[request.form.get("review"), request.form.get("title"),session["user_id"]])
        user = db.session.execute(text("SELECT * from 'users' where id = ?"),params=[session["user_id"]])
        booksnum = user[0]["#_of_books_read"]
        if(booksnum is None):
            booksnum = 0
        db.session.execute(text("UPDATE 'users' SET '#_of_books_read' = ? where id = ?"), params=[(booksnum + 1),session["user_id"]])
        rows = db.session.execute(text("SELECT * from 'books' WHERE title = ? AND author = ?"),params=[request.form.get("title"), request.form.get("author")])
        if(len(rows) == 1):
            reviews = rows[0]["#_of_reviews"]
            db.session.execute(text("UPDATE 'books' SET '#_of_reviews' = ? where title = ? AND author = ?"),params=[(reviews+1),request.form.get("title"), request.form.get("author")])
        else:
            db.session.execute(text("INSERT INTO 'books' VALUES(?,?,?)"), params=[request.form.get("title"), request.form.get("author"), 1])

        return redirect("/")
    else:
        return render_template("form.html")

@app.route("/activity", methods=["GET","POST"])
@login_required
def activity():
    books = db.session.execute(text("SELECT * from 'books' where title in (SELECT 'books'.title from 'books' join reviews on reviews.title='books'.title join 'users' on 'users'.id=reviews.user where 'users'.id = ?)"), params=[session["user_id"]])
    reviews = db.session.execute(text("SELECT * from reviews where title in (SELECT 'books'.title from 'books' join reviews on reviews.title='books'.title join 'users' on 'users'.id=reviews.user where 'users'.id = ?)"), params=[session["user_id"]])
    def find_reviews(title):
        book_reviews = []
        for review in reviews:
            if review["title"] == title:
                book_reviews.append(review["user_review"])
        return book_reviews
    return render_template("activity.html", books=books, reviews=reviews, find=find_reviews)
