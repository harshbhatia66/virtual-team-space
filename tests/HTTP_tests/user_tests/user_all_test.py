import pytest
import requests
import json
from src import config

def clear():
    response = requests.delete(config.url + 'clear/v1')
    
    assert response.status_code == 200

def create_user(email, password, name_first, name_last):
    response = requests.post(config.url + "auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last
    })

    assert response.status_code == 200

    user = response.json()

    return user

def get_user(email, password):
    response = requests.post(config.url + "auth/login/v2", json={
        "email": email,
        "password": password
    })

    assert response.status_code == 200

    user = response.json()

    return user

def create_channel(token, name, is_public):
    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200

    return resp.json()

def user_all(token):
    return requests.get(config.url + "users/all/v1", params={
        'token': token,
    })

# TODO:
@pytest.fixture
def init():
    clear()
    token = create_user('elvin@gmail.com', 'pasfsjnef', 'Elvin', 'Manaois').get('token')
    return token

def test_invalid_token(init):
    invalid_token = -1

    resp = user_all(invalid_token)

    assert resp.status_code == 403

def test_valid_user_all(init):
    token = init
    resp = user_all(token)
    assert resp.status_code == 200
