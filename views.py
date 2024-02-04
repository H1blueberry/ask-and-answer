from flask import Flask, Blueprint, render_template, request, redirect, flash, url_for
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

db = SQL("sqlite:///website2/accounts2.db")

views = Blueprint('views', __name__)

login_ = False
user_id = 0

@views.route('/')
def start():
    return redirect("/login")


@views.route('/home', methods=['GET', 'POST'])
def home():
    if login_ == True:
        if request.method == 'GET':
            credit = db.execute("SELECT credits FROM users WHERE id = ?", user_id)
            credits = credit[0]["credits"]
            questions = db.execute("SELECT * FROM questions WHERE user_id = ? ORDER BY id DESC", user_id)
            answers = db.execute("SELECT * FROM answers WHERE user_id = ? ORDER BY id DESC", user_id)
            return render_template("home.html", credits=credits, questions=questions, answers=answers)
        if request.method == 'POST':
            answer_id_answers = request.form.get("answer_id_answers")
            question_id_answers = request.form.get("question_id_answers")
            if question_id_answers != None:
                question = db.execute("SELECT question FROM questions WHERE id = ?", question_id_answers)
                answers = db.execute("SELECT answer FROM answers WHERE question_id = ? ORDER BY id DESC", question_id_answers)
                question = question[0]["question"]
                return render_template("see_answers.html", answers=answers, question=question)
            question_id = db.execute("SELECT question_id FROM answers WHERE id = ?", answer_id_answers)
            question_id = question_id[0]["question_id"]
            question = db.execute("SELECT question FROM questions WHERE id = ?", question_id)
            answers = db.execute("SELECT answer FROM answers WHERE question_id = ? ORDER BY id DESC", question_id)
            question = question[0]["question"]
            return render_template("see_answers.html", answers=answers, question=question)
    else:
        error5 = "You have to log in!"
        return render_template("login.html", error=error5)


@views.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if username != (""):
            t = db.execute('SELECT * FROM users WHERE username = ?', username)
            if len(t) != 0:
                error = "Username already exists!"
                return render_template("register.html", error=error)
            elif password == (""):
                error2 = "You must enter a password!"
                return render_template("register.html", error=error2)
            elif confirmation == (""):
                error3 = "You must enter a confirmation!"
                return render_template("register.html", error=error3)
            elif confirmation != password:
                error4 = "password and confirmation are not equal!"
                return render_template("register.html", error=error4)
            else:
                hash = generate_password_hash(password)
                db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
                error0 = "You are registered!"
                return render_template("login.html", error=error0)
        else:
            error1 = "You must enter a Username!"
            return render_template("register.html", error=error1)


@views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username == (""):
            error1 = "You must enter your username"
            return render_template("login.html", error=error1)
        elif password == (""):
            error2 = "You must enter your password"
            return render_template("login.html", error=error2)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1:
            error3 = "Invalid username and/or password"
            return render_template("login.html", error=error3)
        password_hash = db.execute("SELECT hash FROM users WHERE username = ?", username)
        if not check_password_hash(password_hash[0]["hash"], password):
            error4 = "Invalid username and/or password"
            return render_template("login.html", error=error4)
        global user_id
        user_id = rows[0]["id"]
        global login_
        login_ = True
        return redirect("/home")


@views.route('/ask', methods=['GET', 'POST'])
def ask():
    if login_ == True:
        if request.method=='GET':
            return render_template('ask.html')
        if request.method=='POST':
            credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)
            credits = credits[0]["credits"]
            if credits > 0:
                question = request.form.get("question")
                if question == (""):
                    error1 = "You have to enter a question!"
                    return render_template("ask.html", error=error1)
                db.execute("INSERT INTO questions (question, answered, user_id) VALUES(?, 0, ?)", question, user_id,)
                credits -= 1
                db.execute("UPDATE users SET credits = ? WHERE id = ?", credits, user_id)
                return redirect("/home")
            error2 = "You do not have enough credits to ask a question!"
            return render_template("ask.html", error=error2)
    else:
        error5 = "You have to log in!"
        return render_template("login.html", error=error5)


@views.route('/answer', methods=['GET', 'POST'])
def answer():
    if login_ == True:
        if request.method == 'GET':
            questions = db.execute("SELECT * FROM questions ORDER BY id DESC")
            return render_template("answer.html", questions=questions)
        if request.method == 'POST':
            questions = db.execute("SELECT question FROM questions")
            answer = request.form.get("answer")
            question_id = request.form.get ("question_id")
            question_id_answers = request.form.get("question_id_answers")
            if question_id_answers != None:
                question = db.execute("SELECT question FROM questions WHERE id = ?", question_id_answers)
                answers = db.execute("SELECT answer FROM answers WHERE question_id = ? ORDER by id DESC", question_id_answers)
                question = question[0]["question"]
                return render_template("see_answers.html", answers=answers, question=question)
            if answer == (""):
                return redirect("/answer")
            db.execute("INSERT INTO answers (answer, user_id, question_id) VALUES(?, ?, ?)", answer, user_id, question_id)
            db.execute("UPDATE questions SET answered = 1 WHERE id = ?", question_id)
            credits = db.execute("SELECT credits FROM users WHERE id = ?", user_id)
            credits = credits[0]["credits"]
            credits += 5
            db.execute("UPDATE users SET credits = ? WHERE id = ?", credits, user_id)
            return redirect("/home")
    else:
        error5 = "You have to log in!"
        return render_template("login.html", error=error5)


@views.route('/logout')
def logout():
    if request.method == 'GET':
        global user_id
        user_id = 0
        global login_
        login_ = False
        return render_template("login.html")
