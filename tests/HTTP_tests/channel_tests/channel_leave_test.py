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

def channel_leave(token, channel_id):
    return requests.post(config.url + "channel/leave/v1", json={
        'token': token,
        'channel_id': channel_id
    })

@pytest.fixture
def init():
    clear()
    reg = create_user("elvin@gmail.com", "thisisapassword", "Elvin", "Manaois")
    
    chan = create_channel(reg['token'], "Test01", True)

    return [reg, chan]

def test_invalid_token(init):
    chan_id = int(init[1]['channel_id'])
    invalid_token = -1

    resp = channel_leave(invalid_token, chan_id)

    assert resp.status_code == 403

def test_invalid_channel_id(init):
    token = init[0]['token']
    invalid_channel_id = -1

    resp = channel_leave(token, invalid_channel_id)

    assert resp.status_code == 400

def test_user_not_member(init):
    chan_id = int(init[1]['channel_id'])
    new_user = create_user("new@gmail.com", "thisisapasswd", "New", "User")
    token = new_user['token']

    resp = channel_leave(token, chan_id)

    assert resp.status_code == 403

def test_valid_leave(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    
    resp = channel_leave(token, chan_id)
    assert resp.status_code == 200
