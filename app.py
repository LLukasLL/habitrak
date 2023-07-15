"""
TO DO:
- Journal
"""
import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import sqlite3
import calendar

from helpers import apology, login_required

date_format = "%d-%m-%Y"

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
con = sqlite3.connect("database_lukas.db", check_same_thread=False)
db = con.cursor()

"""
FUNCTIONS:
"""
def create_task(user_id, name):
    """
    configures new task in sqlite3
    """
    db.execute("INSERT INTO tasks (user_id, name) VALUES (?, ?)", (user_id, name))
    con.commit()

def delete_task(user_id, task_name):
    db.execute("SELECT * FROM tasks WHERE user_id = ? AND name = ?", (user_id, task_name))
    task = db.fetchall()
    if len(task) == 0:
        return False
    else:
        db.execute("DELETE FROM tasks WHERE user_id = ? AND name = ?", (user_id, task_name))
        con.commit()
        db.execute("DELETE FROM task_entries WHERE user_id = ? AND name = ?", (user_id, task_name))
        con.commit()

def create_task_entry(user_id, task_id, date, entry):
    db.execute("INSERT INTO task_entries (user_id, task_id, date, entry) VALUES (?, ?, ?, ? )", (user_id, task_id, date, entry))
    con.commit()

def delete_task_entry(user_id, task_id, date, entry):   
    db.execute("DELETE FROM task_entries WHERE user_id = ? AND task_id = ? AND date = ?", (user_id, task_id, date))
    con.commit()

def create_checkbox_element(row, column, bool):
    if bool == True:
        checkbox_element = {"id": str(row) + str(column), "bool": True, "checked": "checked"}
    else:
        checkbox_element = {"id": str(row) + str(column), "bool": False, "checked": ""}
    return checkbox_element

def set_new_start_date(new_date, user_id):
    db.execute("UPDATE users SET registration_date = ? WHERE id = ?", (new_date, user_id))
    con.commit()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/habits", methods=["GET", "POST"])
@login_required
def habits():
    # get user info
    temp_id = int(session["user_id"])

    db.execute("SELECT * FROM users WHERE id = ?", (temp_id,))
    user_info = db.fetchall()

    # get registration date => start date habit stacking
    registration_date_str = user_info[0][4]
    registration_date = datetime.strptime(registration_date_str, date_format)
    today_str = datetime.now().strftime(date_format)
    today = datetime.strptime(today_str, date_format)

    date_delta = today - registration_date
    date_delta_int = date_delta.days

    # get tasks from database
    db.execute("SELECT * FROM tasks WHERE user_id = ?", (temp_id,))
    tasks = db.fetchall()
    task_id_list = []
    for task in tasks:
        task_id_list.append(task[0])

    db.execute("SELECT * FROM task_entries WHERE user_id = ?", (temp_id,))
    task_entries = db.fetchall()

    # list of dates in datetime format:
    dates = []
    i = 0
    while i <= date_delta_int:
        dates.append(registration_date + timedelta(days=i))
        i = i + 1

    # list of formatted dates
    dates_formatted = []
    i = 0
    while i <= date_delta_int:
        dates_formatted.append(dates[i].strftime(date_format))
        i = i + 1

    j = 0
    html_checkbox_table = []
    for date in dates:
        date_formatted = date.strftime(date_format)
        html_checkbox_row = [date_formatted]
        m = 0
        for taskid in task_id_list:
            check = False
            for entry in task_entries:    
                if entry[1] == taskid and entry[2] == date_formatted:
                    checkbox_element = {"id": str(j) + str(m), "bool": True, "checked": "checked"}
                    check = True
            if check == False:
                checkbox_element = {"id": str(j) + str(m), "bool": False, "checked": ""}
            html_checkbox_row.append(checkbox_element)
            m = m + 1
        html_checkbox_table.append(html_checkbox_row)
        j = j + 1

    if request.method == "POST":

        if request.form.get("new_task"):
            create_task(temp_id, request.form.get("new_task"))
        
        if request.form.get("delete_task"):
            if delete_task(temp_id, request.form.get("delete_task")) == False:
                return apology("No such Task", 400)
            else:
                return redirect("/habits")
        
        if request.form.get("newstartdate_day") and request.form.get("newstartdate_month") and request.form.get("newstartdate_year"):
            dd = request.form.get("newstartdate_day")
            mm = request.form.get("newstartdate_month")
            yyyy = request.form.get("newstartdate_year")
            if len(dd) == 2 and len(mm) == 2 and len(yyyy) == 4:
                newstartdate_str = dd + '-' + mm + '-' + yyyy
                newstartdate = datetime.strptime(newstartdate_str, date_format)
                minstartdate_str = '01-10-2022'
                minstartdate = datetime.strptime(minstartdate_str, date_format)
                today = datetime.now()
                if newstartdate < minstartdate:
                    return apology("New start date too far back", 400)
                if today < newstartdate:
                    return apology("New start date lies in the future", 400)
                else:
                    set_new_start_date(newstartdate_str, temp_id)
            else:
                return apology("wrong date format", 400)

        checked_ids = request.form.getlist("checkbox")
        j = int(0) # row counter
        for row in html_checkbox_table:
            m = int(0) # element / column counter
            for task_id_ in task_id_list:
                element_id_string = str(j) + str(m)
                date_str_ = dates[j].strftime(date_format)
                db.execute("SELECT * FROM task_entries WHERE user_id = ? AND task_id = ? AND date = ?", (temp_id, task_id_, date_str_))
                check_entry = db.fetchall()
                if element_id_string in checked_ids:
                    if len(check_entry) == 0:
                        create_task_entry(temp_id, task_id_, date_str_, 1)
                elif len(check_entry) == 1:
                    delete_task_entry(temp_id, task_id_, date_str_, 1)

                m = m + 1
            j = j + 1
        return redirect("/habits")

    else:
        return render_template("habits.html", dates=dates, tasks=tasks, html_checkbox_table=html_checkbox_table, task_id_list=task_id_list)


@app.route("/")
@login_required
def index():

    # get user info
    temp_id = int(session["user_id"])

    return redirect("/habits")

@app.route("/journal")
@login_required
def journal():

    # get user info
    temp_id = int(session["user_id"])

    return render_template("/journal.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        rows = db.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return apology("invalid username", 403)
            
        if not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/habits")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = ?", [request.form.get("username")])
        user = db.fetchall()

        # Ensure username doesn't exist already
        if len(user) != 0:
            return apology("username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmed password was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmed password", 400)

        # Ensure passwords match
        elif not request.form.get("password")==request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        
        # set time mark
        registration_date = datetime.now().strftime(date_format)
        
        # Insert user data into database
        db.execute("INSERT INTO users (username, hash, registration_date) VALUES(?, ?, ? )", (request.form.get("username"), generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8), registration_date))
        con.commit()

    else:
        return render_template("register.html")

    #
    return redirect("/")