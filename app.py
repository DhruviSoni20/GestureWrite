from flask import Flask, render_template, url_for, flash,  request, redirect, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Admin@123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'GestureWrite'
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''

    if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form:
        Username = request.form['Username']
        Password = request.form['Password']
        
        # Check if Username and Password are provided
        if not Username or not Password:
            message = 'Please enter your username/password!'
            return render_template('login.html', message=message)
        
        # Establish database connection
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE Username = % s AND Password = % s', (Username, Password, ))
        user = cursor.fetchone()
        
        # Check if user exists and password matches
        if user:
            session['loggedin'] = True
            session['Username'] = user['Username']
            message = 'Logged in successfully!'
            return redirect(url_for('dashboard'))
        else:
            message = 'Incorrect username / password!'    
    return render_template('login.html', message=message)


@app.route('/register', methods =['GET', 'POST'])
def register():
    if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form:
        Username = request.form['Username']
        Password = request.form['Password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE Username = %s', (Username,))
        account = cursor.fetchone()
        
        if account:
            flash('Account already exists!', 'danger')
        elif not Username or not Password:
            flash('Please fill out the form!', 'danger')
        else:
            try:
                cursor.execute('INSERT INTO login (Username, Password) VALUES (%s, %s)', (Username, Password))
                mysql.connection.commit()
                flash('You have successfully registered!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error: {str(e)}', 'danger')
    
    elif request.method == 'POST':
        flash('Please fill out the form!', 'danger')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
     if 'loggedin' in session and session['loggedin']:
         return render_template('dashboard.html')
     else:
         return redirect(url_for('login'))

@app.route('/saved_images')
def saved_images():
    if 'loggedin' not in session:
        flash('Please log in to view saved images!', 'danger')
        return redirect(url_for('login'))
    return render_template('saved_images.html')

# @app.route('/Login')
# def Login():
#     return render_template('Login.html')

# @app.route('/Signup')
# def Signup():
#     return render_template('Signup.html')
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('Username', None)
    session.pop('Password', None)
    return redirect(url_for('login'))

@app.route('/run-script', methods=['POST'])
def run_script():
    # Path to your Python script
    script_path = 'air_canvas.py'
    
    # Run the Python script
    subprocess.run(['python', script_path])
    
    return 'Script executed successfully!'

if __name__ == '__main__':
    app.run(debug=True)
