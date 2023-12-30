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

def create_dm(token, u_ids):
    resp = requests.post(config.url + "dm/create/v1", json={
        "token": token,
        "u_ids": u_ids
    })

    assert resp.status_code == 200

    return resp.json()

def message_senddm(token, dm_id, message):
    return requests.post(config.url + "message/senddm/v1", json={
        'token': token,
        'dm_id': dm_id,
        'message': message
    })

'''
--------------------------------------------------------
    Test for Messages Send on dms
--------------------------------------------------------
'''
@pytest.fixture
def init():
    clear()
    user1 = create_user("elvin@gmail.com", "thisisapassword", "Elvin", "Manaois")
    user2 = create_user("florenz@yahoo.com", "notapassword", "Florenz", "Fulo")

    u_ids = [user2['auth_user_id']]
    dm1 = create_dm(user1['token'], u_ids)

    return [user1, user2, dm1]

def test_invalid_token(init):
    dm_id = init[2]['dm_id']
    invalid_token = -1 
    resp = message_senddm(invalid_token, dm_id, "HelloWorld!")
    assert resp.status_code == 403

def test_invalid_dm_id(init):
    invalid_dm_id = -1
    token = init[0]['token']
    msg = "HelloBob!"

    resp = message_senddm(token, invalid_dm_id, msg)
    assert resp.status_code == 400

def test_msg_under_1_char(init):
    token = init[0]['token']
    dm_id = init[2]['dm_id']
    invalid_msg = ""

    resp = message_senddm(token, dm_id, invalid_msg)
    assert resp.status_code == 400

def test_msg_under_1000_char(init):
    token = init[0]['token']
    dm_id = init[2]['dm_id']
    invalid_msg = "a" * 1001

    resp = message_senddm(token, dm_id, invalid_msg)
    assert resp.status_code == 400


def test_user_not_member(init):
    new_user = create_user('new@gmail.com','yesir2344', 'Yes', 'No')
    dm_id = init[2]['dm_id']
    msg = "Hello Its Me!"

    resp = message_senddm(new_user['token'], dm_id, msg)
    assert resp.status_code == 403

def test_valid_message(init):
    token = init[0]['token']
    dm_id = init[2]['dm_id']
    msg = "Yessir This Is How We Do It"

    resp = message_senddm(token, dm_id, msg)
    assert resp.status_code == 200

    data = resp.json()

    assert data['message_id'] == 1
