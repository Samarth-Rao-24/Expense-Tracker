from flask import Flask, request, redirect, url_for, session, render_template, flash
import pymysql
import re
from werkzeug.security import generate_password_hash, check_password_hash

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
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            db.commit()
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
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        account = cursor.fetchone()
        cursor.close()

        if account and check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['user_id'] = account['user_id']
            session['username'] = account['username']
            return redirect(url_for('add_expense'))
        else:
            flash("Invalid username or password!")

    return render_template('login.html')

# ---------------- ADD EXPENSE ----------------
@app.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO expenses 
               (user_id, amount, category, expense_date, description)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                session['user_id'],
                request.form['amount'],
                request.form['category'],
                request.form['expense_date'],
                request.form['description']
            )
        )
        db.commit()
        cursor.close()
        return redirect(url_for('expenses'))

    return render_template('add_expense.html')

# ---------------- VIEW EXPENSES ----------------
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    start_date = request.form.get('start_date') or request.args.get('start_date')
    end_date = request.form.get('end_date') or request.args.get('end_date')
    category = request.form.get('category') or request.args.get('category')

    query = """
        SELECT expense_id, expense_date, category, amount, description
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

# ---------------- EDIT EXPENSE ----------------
@app.route('/edit-expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM expenses WHERE expense_id=%s AND user_id=%s",
        (expense_id, session['user_id'])
    )
    expense = cursor.fetchone()

    if not expense:
        flash("Unauthorized access")
        return redirect(url_for('expenses'))

    if request.method == 'POST':
        cursor.execute(
            """UPDATE expenses 
               SET amount=%s, category=%s, expense_date=%s, description=%s
               WHERE expense_id=%s AND user_id=%s""",
            (
                request.form['amount'],
                request.form['category'],
                request.form['expense_date'],
                request.form['description'],
                expense_id,
                session['user_id']
            )
        )
        db.commit()
        cursor.close()
        return redirect(url_for('expenses'))

    cursor.close()
    return render_template('edit_expense.html', expense=expense)

# ---------------- DELETE EXPENSE ----------------
@app.route('/delete-expense/<int:expense_id>')
def delete_expense(expense_id):
    if not session.get('loggedin'):
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM expenses WHERE expense_id=%s AND user_id=%s",
        (expense_id, session['user_id'])
    )
    db.commit()
    cursor.close()
    return redirect(url_for('expenses'))

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
