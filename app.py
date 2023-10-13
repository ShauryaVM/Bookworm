import os

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, flash, redirect, render_template, request, session
from functools import wraps
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQLAlchemy("sqlite:///bookworm.db")

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
    user = db.execute("SELECT * from 'users' where 'users'.id = ?", session["user_id"])
    goal = user[0]["goal"]
    read = user[0]["#_of_books_read"]
    if goal is None:
        goal = 0
    elif read is None:
        read = 0
    away = goal - read
    books = db.execute("SELECT * from 'books' where title not in (SELECT 'books'.title from 'books' join reviews on reviews.title='books'.title join 'users' on 'users'.id=reviews.user where 'users'.id = ?)", session["user_id"])
    reviews = db.execute("SELECT * from reviews where title not in (SELECT 'books'.title from 'books' join reviews on reviews.title='books'.title join 'users' on 'users'.id=reviews.user where 'users'.id = ?)", session["user_id"])
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
        user = db.execute("SELECT * from 'users' WHERE username = ?", request.form.get("username"))
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

        usernamecheck = db.execute("SELECT * FROM 'users' WHERE username like ?", request.form.get("username"))
        if len(usernamecheck) == 1:
            return render_template("apology.html", message="Username already exists")

        elif not request.form.get("password"):
            return render_template("apology.html", message="Must provide password")

        elif not (request.form.get("password") == request.form.get("confirmation")):
            return render_template("apology.html", message="Passwords do not match")

        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=10)
        db.execute("INSERT INTO 'users'(username, hash) VALUES(?, ?)",username,password)

        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        resetpass = generate_password_hash("bookworm", method='pbkdf2:sha256', salt_length=10)
        db.execute("UPDATE 'users' SET hash = ? where username = ?", resetpass, request.form.get("username"))

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
        db.execute("UPDATE 'users' SET hash = ? where id = ?", newpasswordsecure, session["user_id"])

        return redirect("/")
    else:
        return render_template("change.html")

@app.route("/goal", methods=["GET", "POST"])
@login_required
def goal():
    if request.method == "POST":
        if(int(request.form.get("goal")) <= 0):
            return render_template("apology.html", message="Invalid number of books")
        db.execute("UPDATE 'users' SET 'goal' = ? where id = ?", int(request.form.get("goal")), session["user_id"])
        return redirect("/")
    else:
        return render_template("goal.html")

@app.route("/form", methods=["GET","POST"])
@login_required
def form():
    if request.method == "POST":
        db.execute("INSERT INTO reviews VALUES(?,?,?)",request.form.get("review"), request.form.get("title"),session["user_id"])
        user = db.execute("SELECT * from 'users' where id = ?",session["user_id"])
        booksnum = user[0]["#_of_books_read"]
        if(booksnum is None):
            booksnum = 0
        db.execute("UPDATE 'users' SET '#_of_books_read' = ? where id = ?", (booksnum + 1),session["user_id"])
        rows = db.execute("SELECT * from 'books' WHERE title = ? AND author = ?",request.form.get("title"), request.form.get("author"))
        if(len(rows) == 1):
            reviews = rows[0]["#_of_reviews"]
            db.execute("UPDATE 'books' SET '#_of_reviews' = ? where title = ? AND author = ?",(reviews+1),request.form.get("title"), request.form.get("author"))
        else:
            db.execute("INSERT INTO 'books' VALUES(?,?,?)", request.form.get("title"), request.form.get("author"), 1)

        return redirect("/")
    else:
        return render_template("form.html")

@app.route("/activity", methods=["GET","POST"])
@login_required
def activity():
    books = db.execute("SELECT * from 'books' where title in (SELECT 'books'.title from 'books' join reviews on reviews.title='books'.title join 'users' on 'users'.id=reviews.user where 'users'.id = ?)", session["user_id"])
    reviews = db.execute("SELECT * from reviews where title in (SELECT 'books'.title from 'books' join reviews on reviews.title='books'.title join 'users' on 'users'.id=reviews.user where 'users'.id = ?)", session["user_id"])
    def find_reviews(title):
        book_reviews = []
        for review in reviews:
            if review["title"] == title:
                book_reviews.append(review["user_review"])
        return book_reviews
    return render_template("activity.html", books=books, reviews=reviews, find=find_reviews)
