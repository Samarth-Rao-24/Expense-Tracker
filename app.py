from flask import Flask , request , redirect , url_for , session, render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors 
import re

app=Flask(__name__)
app.secret_key = 'adeee'

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='scs123'
app.config['MYSQL_DB']='expense_tracker'

mysql=MySQL(app)

@app.route('/register',methods=['GET','POST'])
def register():
    msg=''
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']

        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username=%s',(username,))
        account=cursor.fetchone()

        if account:
            msg='Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg='Username must contain only characters and numbers!'
        elif not username or not password:
            msg='Please fill out the form!'
        else:
            cursor.execute('INSERT INTO users (username,password) VALUES (%s,%s)',(username, password))
            mysql.connection.commit()
            msg='You have successfully registered!'
            return redirect(url_for('login'))

    return render_template('register.html',msg=msg)


@app.route('/login',methods=['GET','POST'])
def login():
    msg=''
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password=%s',(username,password))
        account=cursor.fetchone()

        if account:
            session['loggedin']=True
            session['id']=account['user_id']
            session['username']=account['username']
            msg='Logged in successfully!'
            return redirect(url_for('home'))
        else:
            msg='Incorrect username/password!'
    return render_template('login.html',msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('id',None)
    session.pop('username',None)
    return 'You have successfully logged out!'

    
@app.route('/')
def home():
    return "Flask–MySQL Connected"

if __name__ == '__main__':
    app.run(debug=True)