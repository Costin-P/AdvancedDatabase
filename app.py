from xml.etree.ElementTree import tostring
from flask import Flask, request, jsonify, abort , url_for, session
from flask.templating import render_template
from model import predict
from features import features_list, feature_form_structure
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re 

app = Flask(__name__)


app.secret_key = 'your secret key'
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'house_rent'

mysql = MySQL(app)

@app.route('/')
def hello_world():
    i = 0
    return render_template('new_login.html', feature_form_structure=feature_form_structure, i=i)


@app.route('/predict', methods=['POST'])
def create_task():
    if not request.json:
        abort(400)
    prediction = predict(request.json)
    return jsonify({'done': True, 'prediction': prediction[0]}), 201

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
        print(username)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', feature_form_structure=feature_form_structure, i=0)
        else:
            msg = 'Incorrect username / password !'
    else: 
        print(request.method)
    
    return render_template('new_login.html', msg = msg)


@app.route('/logout')
def logout(redirect):
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Username  already taken  !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered ! Sign in to continue'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('new_register.html', msg = msg)

if __name__ == '__main__':
    app.run(use_reloader=True)
