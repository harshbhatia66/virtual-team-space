import pytest
import requests
import json
from src import config
import time

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

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    return requests.post(config.url + "/message/sendlaterdm/v1", json={
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent
    })

# TODO: Add to main file
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

    return [dm1, user1, user2]

def test_invalid_token(init):
    invalid_token = -1
    dm_id = init[0]['dm_id']
    msg = "Test"
    time_sent = int(time.time())

    resp = message_sendlaterdm_v1(invalid_token, dm_id, msg, time_sent)
    assert resp.status_code == 403

def test_invalid_dm_id(init):
    token = init[1]['token']
    invalid_dm_id = -1
    msg = "Test"
    time_sent = int(time.time())

    resp = message_sendlaterdm_v1(token, invalid_dm_id, msg, time_sent)
    assert resp.status_code == 400

def test_auth_user_non_member(init):
    token = create_user("skdjnfa@gmail.com", "sadkjfnasf", "asjdna", "awjdnawd")['token']
    dm_id = init[0]['dm_id']
    msg = "Test"
    time_sent = int(time.time())

    resp = message_sendlaterdm_v1(token, dm_id, msg, time_sent)
    assert resp.status_code == 403

def test_message_under_1_character(init):
    token = init[1]['token']
    dm_id = init[0]['dm_id']
    msg = ""
    time_sent = int(time.time())

    resp = message_sendlaterdm_v1(token, dm_id, msg, time_sent)
    assert resp.status_code == 400

def test_message_over_1000_character(init):
    token = init[1]['token']
    dm_id = init[0]['dm_id']
    msg = "a" * 1001
    time_sent = int(time.time())

    resp = message_sendlaterdm_v1(token, dm_id, msg, time_sent)
    assert resp.status_code == 400

def test_invalid_time_sent(init):
    token = init[1]['token']
    dm_id = init[0]['dm_id']
    msg = "Hello World!"
    time_sent = int(time.time()) - 10

    resp = message_sendlaterdm_v1(token, dm_id, msg, time_sent)
    assert resp.status_code == 400

def test_valid_message_send_later_dm(init):
    token = init[1]['token']
    dm_id = init[0]['dm_id']
    msg = "Hello World!"
    time_sent = int(time.time()) + 1

    resp = message_sendlaterdm_v1(token, dm_id, msg, time_sent)
    assert resp.status_code == 200