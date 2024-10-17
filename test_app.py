import pytest
from app import app, db, User

@pytest.fixture
def client():
    # Налаштування тестового клієнта
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Використання in-memory SQLite для тестування
    with app.app_context():
        db.create_all()  # Створити всі таблиці
    yield app.test_client()  # Повертаємо тестовий клієнт
    with app.app_context():
        db.drop_all()  # Очищення бази даних після тестування

def test_register(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 302  # Очікуємо перенаправлення
    assert User.query.filter_by(username='testuser').first() is not None  # Перевірка, що користувач зареєстрований

def test_login(client):
    # Спочатку реєструємо користувача
    client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    # Тепер пробуємо увійти
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 302  # Очікуємо перенаправлення

    # Створюємо сесію для тестування
    with client.session_transaction() as session:
        assert session.get('user_id') is not None  # Перевірка, що сесія містить user_id

def test_logout(client):
    # Спочатку реєструємо та логінемося
    client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    response = client.post('/logout')  # Вихід
    assert response.status_code == 302  # Очікуємо перенаправлення

    # Перевірка, що сесія була видалена
    with client.session_transaction() as session:
        assert 'user_id' not in session
