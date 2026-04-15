import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.fake_db import db

client = TestClient(app)

# Исходное состояние базы (для сброса между тестами)
INITIAL_USERS = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

@pytest.fixture(autouse=True)
def reset_database():
    """Сбрасываем базу в исходное состояние перед каждым тестом"""
    db._users = [user.copy() for user in INITIAL_USERS]
    db._id = len(db._users)


def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': INITIAL_USERS[0]['email']})
    assert response.status_code == 200
    assert response.json() == {
        'id': INITIAL_USERS[0]['id'],
        'name': INITIAL_USERS[0]['name'],
        'email': INITIAL_USERS[0]['email']
    }


def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'nonexistent@mail.com'})
    assert response.status_code == 404
    assert response.json()['detail'] == 'User not found'


def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'Sergey Sergeev',
        'email': 's.s.sergeev@mail.com'
    }
    response = client.post("/api/v1/user", json=new_user)
    assert response.status_code == 201
    assert isinstance(response.json(), int)


def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_user = {
        'name': 'Duplicate Name',
        'email': INITIAL_USERS[0]['email']
    }
    response = client.post("/api/v1/user", json=existing_user)
    assert response.status_code == 409
    assert response.json()['detail'] == 'User with this email already exists'


def test_delete_user():
    '''Удаление пользователя'''
    temp_user = {
        'name': 'Temporary User',
        'email': 'temp@mail.com'
    }
    # Создаём
    create_response = client.post("/api/v1/user", json=temp_user)
    assert create_response.status_code == 201
    
    # Удаляем
    delete_response = client.delete("/api/v1/user", params={'email': temp_user['email']})
    assert delete_response.status_code == 204
    
    # Проверяем, что удалён
    get_response = client.get("/api/v1/user", params={'email': temp_user['email']})
    assert get_response.status_code == 404