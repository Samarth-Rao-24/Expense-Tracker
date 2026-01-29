from flask import Flask
from flask_mysqldb import MySQL

# Step 1: Initialize Flask app
app = Flask(__name__)

# Step 2: Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'          # MySQL server is running locally
app.config['MYSQL_USER'] = 'root'               # Default MySQL user
app.config['MYSQL_PASSWORD'] = 'your_password'  # Replace with your actual MySQL root password
app.config['MYSQL_DB'] = 'expense_tracker'      # The database you created earlier

# Step 3: Initialize MySQL extension
mysql = MySQL(app)

# Step 4: Create a test route
@app.route('/')
def home():
    return "Flask-MySQL Connected Successfully!"

# Step 5: Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)