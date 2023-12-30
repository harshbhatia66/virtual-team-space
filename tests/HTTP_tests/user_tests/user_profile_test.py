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

def user_profile(token, u_id):
    return requests.get(config.url + "user/profile/v1", params={
        'token': token,
        'u_id': u_id
    })
''' 
----------------------------------------------------
    Test HTTP Server for User Profile
----------------------------------------------------
'''
@pytest.fixture
def setup():
    clear()
    user1 = create_user('elvin@gmail.com', 'akwjdhaw123', 'Elvin', 'Manaois')
    user2 = create_user('bobdabuilder@gmail.com', 'awdjnawkdn1123124', 'Bob', 'Builder')

    return [user1, user2]

def test_invalid_token(setup):
    invalid_token = -1
    u_id = setup[1]['auth_user_id']

    resp = user_profile(invalid_token, u_id)
    assert resp.status_code == 403

def test_invalid_u_id(setup):
    token = setup[0]['token']
    invalid_u_id = -1

    resp = user_profile(token, invalid_u_id)
    assert resp.status_code == 400

def test_valid_profile(setup):
    token = setup[0]['token']
    u_id = setup[1]['auth_user_id']

    resp = user_profile(token, u_id)
    assert resp.status_code == 200

    data = resp.json()

    details = {
        'user': {
            'u_id': 1002,
            'email': "bobdabuilder@gmail.com",
            'name_first': 'Bob',
            'name_last': 'Builder',
            'handle_str': 'bobbuilder',
            'profile_img_url': ""
        },
    }

    assert data == details
