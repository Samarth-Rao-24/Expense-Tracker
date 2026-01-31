from flask import Flask, request, redirect, url_for, session, render_template
import pymysql
import re

app = Flask(__name__)
app.secret_key = 'adeee'

# MySQL connection config
db = pymysql.connect(
    host="localhost",
    user="root",
    password="scs123",
    database="expense_tracker",
    cursorclass=pymysql.cursors.DictCursor
)

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        account = cursor.fetchone()

        if account:
            msg = "Account already exists!"
        elif not re.match(r'^[A-Za-z0-9]+$', username):
            msg = "Username must contain letters and numbers only!"
        elif not username or not password:
            msg = "Please fill out the form!"
        else:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            db.commit()
            cursor.close()
            return redirect(url_for('login'))

        cursor.close()

    return render_template('register.html', msg=msg)

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        account = cursor.fetchone()
        cursor.close()

        if account:
            session['loggedin'] = True
            session['user_id'] = account['user_id']
            session['username'] = account['username']
            return redirect(url_for('add_expense'))
        else:
            msg = "Incorrect username or password!"

    return render_template('login.html', msg=msg)

# ---------------- ADD EXPENSE ----------------
@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        expense_date = request.form['expense_date']
        description = request.form['description']
        user_id = session['user_id']

        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO expenses
               (user_id, amount, category, expense_date, description)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, amount, category, expense_date, description)
        )
        db.commit()
        cursor.close()

        return "Expense Added Successfully"

    return render_template('add_expense.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- HOME ----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
