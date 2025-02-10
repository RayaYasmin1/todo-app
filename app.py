from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
import random
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key


# MongoDB Atlas connection
connection_string = "mongodb+srv://rayayasmin111:1234@cluster0.idaqm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(connection_string)
db = client['todo_db']
tasks_collection = db['tasks']
users_collection = db['users']

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        return User(str(user['_id']))
    return None

# List of motivational quotes
motivational_quotes = [
    
   "Verily, with hardship comes ease. – Quran 94:6",
    "Allah does not burden a soul beyond that it can bear. – Quran 2:286",
    "Indeed, Allah is with the patient. – Quran 2:153",
    "And whoever relies upon Allah – then He is sufficient for him. – Quran 65:3",
    "So remember Me; I will remember you. – Quran 2:152",
    "Allah is the best of planners. – Quran 8:30",
    "The strong believer is better and more beloved to Allah than the weak believer. – Sahih Muslim",
    "Do not be sad, for Allah is with us. – Quran 9:40",
    "Allah does not look at your appearance or wealth, but He looks at your hearts and deeds. – Sahih Muslim",
    "The best among you are those who have the best manners and character. – Sahih Bukhari"
]

# Home page - Display all tasks and a random quote
@app.route('/')
@login_required
def index():
    tasks = list(tasks_collection.find({'user_id': current_user.id}))  # Fetch tasks for the logged-in user
    random_quote = random.choice(motivational_quotes)  # Pick a random quote
    return render_template('index.html', tasks=tasks, quote=random_quote)

# Sign Up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Check if the username already exists
        if users_collection.find_one({'username': username}):
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('signup'))

        # Insert the new user into the database
        user_id = users_collection.insert_one({
            'username': username,
            'password': hashed_password
        }).inserted_id

        # Log the user in
        user = User(str(user_id))
        login_user(user)
        return redirect(url_for('index'))

    return render_template('signup.html')

# Sign In
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user in the database
        user = users_collection.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            user_obj = User(str(user['_id']))
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'error')

    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Add a new task
@app.route('/add', methods=['POST'])
@login_required
def add():
    content = request.form['content']
    if content:
        task = {
            'content': content,
            'done': False,
            'user_id': current_user.id  # Associate the task with the logged-in user
        }
        tasks_collection.insert_one(task)
    return redirect(url_for('index'))

# Mark a task as done
@app.route('/done/<string:id>')
@login_required
def done(id):
    tasks_collection.update_one({'_id': ObjectId(id), 'user_id': current_user.id}, {'$set': {'done': True}})
    return redirect(url_for('index'))

# Delete a task
@app.route('/delete/<string:id>')
@login_required
def delete(id):
    tasks_collection.delete_one({'_id': ObjectId(id), 'user_id': current_user.id})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)