from flask import Flask, request, redirect, url_for, session, render_template, flash
import pymysql
import re

app = Flask(__name__)
app.secret_key = 'adeee'

# ---------------- DB CONNECTION ----------------
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        account = cursor.fetchone()

        if account:
            flash("Account already exists!")
        elif not re.match(r'^[A-Za-z0-9]+$', username):
            flash("Username must contain letters and numbers only!")
        elif not username or not password:
            flash("Please fill out the form!")
        else:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password)
            )
            db.commit()
            cursor.close()
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))

        cursor.close()

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
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
            flash("Login successful!")
            return redirect(url_for('add_expense'))
        else:
            flash("Invalid username or password!")

    return render_template('login.html')

# ---------------- ADD EXPENSE ----------------
@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if not session.get('loggedin'):
        flash("Please login first")
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

        flash("Expense added successfully!")
        return redirect(url_for('expenses'))

    return render_template('add_expense.html')

# ---------------- VIEW EXPENSES  ----------------
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if not session.get('loggedin'):
        flash("Please login first")
        return redirect(url_for('login'))

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        category = request.form.get('category')
    else:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')

    query = """
        SELECT expense_date, category, amount, description
        FROM expenses
        WHERE user_id = %s
    """
    params = [session['user_id']]

    if start_date and end_date:
        query += " AND expense_date BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    if category:
        query += " AND category = %s"
        params.append(category)

    query += " ORDER BY expense_date DESC"

    cursor = db.cursor()
    cursor.execute(query, params)
    expenses = cursor.fetchall()

    cursor.execute(
        "SELECT IFNULL(SUM(amount),0) AS total FROM expenses WHERE user_id=%s",
        (session['user_id'],)
    )
    total = cursor.fetchone()['total']

    cursor.execute(
        "SELECT category, SUM(amount) AS total FROM expenses WHERE user_id=%s GROUP BY category",
        (session['user_id'],)
    )
    category_totals = cursor.fetchall()

    cursor.close()

    return render_template(
        'expenses.html',
        expenses=expenses,
        total=total,
        category_totals=category_totals
    )


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect(url_for('login'))

# ---------------- HOME ----------------
@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
