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

def message_send(token, channel_id, message):
    return requests.post(config.url + "/message/send/v1", json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

'''
--------------------------------------------------------
    Test for Messages Send on channels
--------------------------------------------------------
'''
@pytest.fixture
def setup():
    clear()
    reg = create_user("elvin@gmail.com", "pasksjefns", "Elvin", "Manaois")

    chan = create_channel(reg['token'], "Test01", True)

    return [reg, chan]

def test_invalid_token(setup):
    invalid_token = -1
    resp = message_send(invalid_token, int(setup[1]['channel_id']), "Hello World!")
    assert resp.status_code == 403

def test_invalid_channel_id(setup):
    invalid_channel_id = -1

    resp = message_send(setup[0]['token'], invalid_channel_id, "Helloworld")
    assert resp.status_code == 400

def test_message_less_1_character(setup):
    msg = ""

    resp = message_send(setup[0]['token'], int(setup[1]['channel_id']), msg)
    assert resp.status_code == 400

def test_message_over_1000_character(setup):
    msg = "a" * 1001

    resp = message_send(setup[0]['token'], int(setup[1]['channel_id']), msg)
    assert resp.status_code == 400

def test_user_not_member(setup):
    new_user = create_user("yes@gmail.com", "pasword12123", "Yes", "No") 

    resp = message_send(new_user['token'], int(setup[1]['channel_id']), "Hello")
    assert resp.status_code == 403

def test_valid_message(setup):
    token = setup[0]['token']
    chan_id = int(setup[1]['channel_id'])
    msg = "Hello its me!"

    resp = message_send(token, chan_id, msg)
    assert resp.status_code == 200

    data = resp.json()

    # Expected first result
    res = {
        "message_id": 1,
    }

    assert data == res
