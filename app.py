from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'test'
app.config['MONGO_DBNAME'] = 'registration'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/registration'

mongo = PyMongo(app)

def login_required(func):
	@wraps(func)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return func(*args, **kwargs)
		else:
			flash('You aren\'t logged in!')
			return redirect(url_for('login'))
	return wrap

@app.route('/')
@login_required
def home():
	users = mongo.db.users
	user = users.find_one({'username': session['username']})
	return render_template('index.html', firstname=user['firstname'], 
			                     lastname=user['lastname'], 
					     email=user['email'])

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		users = mongo.db.users
		user = users.find_one({'username': request.form['username']})
		if not user or not check_password_hash(user['password'], request.form['password']):
			error = 'Invalid Credentials. Please try again.'
		else:
			session['logged_in'] = True
			session['username'] = user['username']
			flash('Successfully logged in.')
			return redirect(url_for('home'))
	return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		users = mongo.db.users
		user = users.find_one({'username': request.form['username']})
		if user:
			return render_template('register.html', error="User already exists!")
		users.insert({'username': request.form['username'],
			      'email': request.form['email'],
			      'firstname': request.form['firstname'],
			      'lastname': request.form['lastname'],
			      'password': generate_password_hash(request.form['password'], method="sha256")})
		session['logged_in'] = True
		session['username'] = request.form['username']
		return redirect(url_for('home'))
	return render_template('register.html', error=error)
	

@app.route('/logout')
@login_required
def logout():
	session.pop('logged_in')
	flash('Successfully logged out.')
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.run(debug=True)
