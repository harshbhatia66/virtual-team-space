import pytest
import requests
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

def create_channel(token, name, is_public):
    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200

    return resp.json()

def message_sendlater_v1(token, channel_id, message, time_sent):
    return requests.post(config.url + "/message/sendlater/v1", json={
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent
    })

'''
--------------------------------------------------------
    Test for Messages Send later on channels
--------------------------------------------------------
'''
@pytest.fixture
def init():
    clear()
    reg = create_user("elvin@gmail.com", "pasksjefns", "Elvin", "Manaois")

    chan = create_channel(reg['token'], "Test01", True)

    return [reg, chan]

def test_invalid_token(init):
    invalid_token = -1
    chan_id = init[1]['channel_id']
    message = "Yessirrr"
    time_sent = int(time.time())
    
    resp = message_sendlater_v1(invalid_token, chan_id, message, time_sent)
    assert resp.status_code == 403

def test_invalid_channel_id(init):
    token = init[0]['token']
    invalid_chan_id = -1
    message = "Yessirr"
    time_sent = int(time.time())

    resp = message_sendlater_v1(token, invalid_chan_id, message, time_sent)
    assert resp.status_code == 400

def test_auth_user_non_member(init):
    token = create_user("skljdfhns@gmail.com", "aksdjhnaksjnd", "ajdn", "asdjansd").get('token')
    chan_id = init[1]['channel_id']
    message = "Test"
    time_sent = int(time.time())

    
    resp = message_sendlater_v1(token, chan_id, message, time_sent)
    assert resp.status_code == 403

def test_message_under_1_character(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    message = ""
    time_sent = int(time.time())

    resp = message_sendlater_v1(token, chan_id, message, time_sent)
    assert resp.status_code == 400

def test_message_over_1000_characters(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    message = "a" * 1001
    time_sent = int(time.time())

    resp = message_sendlater_v1(token, chan_id, message, time_sent)
    assert resp.status_code == 400

def test_invalid_time_sent(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    message = "Hello World!"
    time_sent = int(time.time()) - 60

    resp = message_sendlater_v1(token, chan_id, message, time_sent)
    assert resp.status_code == 400

def test_valid_message_send_later(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    message = "Hello World!"
    time_sent = int(time.time()) + 1

    resp = message_sendlater_v1(token, chan_id, message, time_sent)
    assert resp.status_code == 200
