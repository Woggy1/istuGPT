from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import openai
import os
from dotenv import load_dotenv  
app = Flask(__name__)

# Перевіряємо, чи тестове середовище
if app.config['TESTING']:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory SQLite для тестів
else:
    # Налаштування для MySQL
    if os.getenv('DOCKER') == '1':  # Перевірка на Docker
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:userpass@db/mydb'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:userpass@localhost:3306/mydb'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

load_dotenv()  # Завантажує змінні середовища з файлу .env
openai.api_key = os.getenv("OPENAI_API_KEY")  # Отримання API ключа з змінних середовища
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Модель для користувачів
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Створення таблиць
with app.app_context():
    db.create_all()

# Реєстрація
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Вхід
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('chat'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

# Вихід
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Чат
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        flash('Please log in first', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        message = request.json['message']
        response = openai.ChatCompletion.create(
            model="gpt-4",  
            messages=[
                {"role": "user", "content": message}
            ],
            max_tokens=150
        )
        return {'reply': response.choices[0].message['content'].strip()}

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
