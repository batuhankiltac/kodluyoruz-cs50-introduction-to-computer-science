import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd


app = Flask(__name__)


app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


app.jinja_env.filters["usd"] = usd


app.jinja_env.globals.update(usd=usd)
app.jinja_env.globals.update(lookup=lookup)
app.jinja_env.globals.update(round=round)


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


db = SQL("sqlite:///finance.db")


@app.route("/", methods=["GET"])
@login_required
def index():
    """Show portfolio of stocks"""

    summary = db.execute(
        "SELECT stock_name, stock_symbol, SUM(bought_shares) AS bought FROM tran_history where user = :user GROUP BY stock_name", user=session["username"])

    cash = db.execute("SELECT cash FROM users where id = :id",
                      id=session["user_id"])

    total_value = 0

    for stock in summary:
        total_value += lookup(stock["stock_symbol"])["price"] * stock["bought"]

    return render_template("index.html", summary=summary, cash=cash, total_value=total_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        if not request.form.get("shares").isdigit():
            return apology("Number of shares must be a positive integer!", 400)

        cash = db.execute(
            "SELECT cash FROM users WHERE id = :id", id=session["user_id"])

        quote = lookup(request.form.get("symbol"))

        if quote is None:
            return apology("Incorrect or non-existant symbol!", 400)

        want_to_buy = quote["price"] * int(request.form.get("shares"))

        if cash[0]["cash"] < want_to_buy:
            return apology("Not enough cash!", 400)

        else:

            db.execute("UPDATE users SET cash = :cash - :want_to_buy WHERE username = :user",
                       cash=cash[0]["cash"], want_to_buy=want_to_buy, user=session["username"])

            db.execute("INSERT INTO tran_history (user, stock_name, stock_symbol, action, bought_shares, price) VALUES(:user, :stock_name, :stock_symbol, :action, :bought_shares, :price)",
                       user=session["username"], stock_name=quote["name"], stock_symbol=quote["symbol"], action="B", bought_shares=int(request.form.get("shares")), price=want_to_buy)

            return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""

    username = request.args.get("username")

    database = db.execute("SELECT username FROM users")

    users_list = []

    for pair in database:
        for k, v in pair.items():
            users_list.append(v)

    if len(username) > 0 and username not in users_list:
        return jsonify(True)

    else:
        return jsonify(False)


@app.route("/dashboard", methods=["GET"])
@login_required
def dash():
    return render_template("dashboard.html")


@app.route("/dashboard/add", methods=["GET", "POST"])
@login_required
def add():
    """Add virtual cash to account"""

    if request.method == "POST":
        amount = request.form.get("amount")

        current_cash = db.execute(
            "SELECT cash FROM users where username = :user", user=session["username"])

        db.execute("UPDATE users SET cash = :amount + :current_cash WHERE username = :user",
                   amount=amount, user=session["username"], current_cash=current_cash[0]["cash"])

        flash("Cash successfully added!")

        return redirect("/")

    else:
        return render_template("dashboard.html")


@app.route("/dashboard/change", methods=["GET", "POST"])
@login_required
def change():
    """Allow user to change password:
        Enter current password
        Enter new password
        Confirm new password"""

    if request.method == "POST":
        old_password = db.execute(
            "SELECT hash FROM users where username = :user", user=session["username"])

        if not request.form.get("old_password") or not request.form.get("new_password") or not request.form.get("confirm_password"):
            return apology("Some fields are empty!", 400)

        if not check_password_hash(old_password[0]["hash"], request.form.get("old_password")):
            return apology("Incorrect old password!", 400)

        if request.form.get("new_password") != request.form.get("confirm_password"):
            return apology("Confirmation fields don't match!", 400)

        if check_password_hash(old_password[0]["hash"], request.form.get("new_password")):
            return apology("Old and new password can't be identical!", 400)

        hash = generate_password_hash(request.form.get(
            "new_password"), method='pbkdf2:sha256', salt_length=8)

        db.execute("UPDATE users SET hash = :hash WHERE username = :user",
                   hash=hash, user=session["username"])

        flash("Password changed!")

        return redirect("/")

    else:
        return render_template("dashboard.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    history = db.execute(
        "SELECT * FROM tran_history WHERE user = :user", user=session["username"])

    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":

        quote = lookup(request.form.get("symbol"))

        if quote is None:
            return apology("Incorrect or non-existant symbol!", 400)

        return render_template("quoted.html", quote=quote)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        if not request.form.get("username"):
            return apology("Missing username!", 400)

        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Missing password!", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match!", 400)

        hash = generate_password_hash(request.form.get(
            "password"), method='pbkdf2:sha256', salt_length=8)

        id = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                        username=request.form.get("username"), hash=hash)

        if not id:
            return apology("Username already exists!", 400)

        session["user_id"] = id
        session["username"] = request.form.get("username")

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    summary = db.execute(
        "SELECT stock_name, stock_symbol, SUM(bought_shares) AS bought FROM tran_history where user = :user GROUP BY stock_name", user=session["username"])

    if request.method == "POST":

        if not request.form.get("shares"):
            return apology("You didn't input number of shares to sell!", 400)

        if int(request.form.get("shares")) < 0:
            return apology("Number of shares can't be negative!", 400)

        cash = db.execute(
            "SELECT cash FROM users WHERE id = :id", id=session["user_id"])

        quote = lookup(request.form.get("symbol"))

        if quote is None:
            return apology("Incorrect or non-existant symbol!", 400)

        for stock in summary:
            own = len(summary)
            if stock["stock_symbol"] != request.form.get("symbol"):
                own -= 1
            if not own:
                return apology("User does not own any shares of that stock!", 400)

        want_to_sell = quote["price"] * int(request.form.get("shares"))

        sum = db.execute("SELECT SUM(bought_shares) AS bought from tran_history WHERE user = :user and stock_symbol = :stock",
                         user=session["username"], stock=request.form.get("symbol"))

        if int(request.form.get("shares")) > int(sum[0]["bought"]):
            return apology("You don't own enough stock!", 400)

        db.execute("UPDATE users SET cash = :cash + :want_to_sell WHERE username = :user",
                   cash=cash[0]["cash"], want_to_sell=want_to_sell, user=session["username"])

        db.execute("INSERT INTO tran_history (user, stock_name, stock_symbol, action, bought_shares, price) VALUES(:user, :stock_name, :stock_symbol, :action, :bought_shares, :price)",
                   user=session["username"], stock_name=quote["name"], stock_symbol=quote["symbol"], action="S", bought_shares=-int(request.form.get("shares")), price=want_to_sell)

        return redirect("/")

    else:
        # summary = db.execute("SELECT stock_name, stock_symbol, SUM(bought_shares) AS bought FROM tran_history where user = :user GROUP BY stock_name", user=session["username"])
        return render_template("sell.html", summary=summary)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
