import pytest
import string
import random
import json
import requests
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

def create_channel(token, name, is_public):
    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200

    return resp.json()

def dm_create(token, u_ids):
    resp = requests.post(config.url + "dm/create/v1", json={
        'token': token,
        'u_ids': u_ids
    })
    assert resp.status_code == 200
    return resp.json()

def message_send(token, channel_id, message):
    resp = requests.post(config.url + "message/send/v1", json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

    assert resp.status_code == 200

    message_id = resp.json()

    return message_id

def message_share(token, og_message_id, message, channel_id, dm_id):
    resp = requests.post(config.url + "message/share/v1", json={
        'token': token,
        'og_message_id': og_message_id,
        'message': message,
        'channel_id': channel_id,
        'dm_id': dm_id
    })
    return resp

@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert") 
    user3 = create_user("chelseaarezo@gmail.com", "Boomer10", "Chelsea", "Arezo")   
    u_ids = [user2['auth_user_id']]
    dm1 = dm_create(user1['token'], u_ids)
    
    channel1 = create_channel(user1['token'], "test_channel1", True)
    channel2 = create_channel(user3['token'], "test_channel2", True)
    message_id = message_send(user1['token'], channel1['channel_id'], "freedom")
    message_id2 = message_send(user3['token'], channel2['channel_id'], "freedom2")
    return [user1, user2, dm1, channel1, user3, message_id, channel2, message_id2]

''' 
----------------------------------------------------
    Test HTTP Server to Share Message to Channel/DM  
----------------------------------------------------
'''

def test_message_share_to_channel(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = setup[3]['channel_id']
    dm_id = -1
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 200
    
def test_message_share_to_dm(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = -1
    dm_id = setup[2]['dm_id']
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 200
    
def test_invalid_dm_id(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = setup[3]['channel_id']
    dm_id = 0
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 400

def test_invalid_channel_id(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = 0
    dm_id = setup[2]['dm_id']
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 400

def test_both_invalid_ids(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = setup[3]['channel_id']
    dm_id = setup[2]['dm_id']
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 400

def test_both_negative_ids(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = -1
    dm_id = -1
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 400

def test_invalid_og_message_id(setup):
    token = setup[0]['token']
    og_message_id = -5
    message = "hello" + "freedom"
    channel_id = -1
    dm_id = setup[2]['dm_id']
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 400

def test_empty_message_share(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = ""
    new_message = "freedom" + message
    channel_id = -1
    dm_id = setup[2]['dm_id']
    resp = message_share(token, og_message_id, new_message, channel_id, dm_id)
    assert resp.status_code == 200

def test_message_over_1000(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    channel_id = -1
    dm_id = setup[2]['dm_id']
    invalid_message = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1005))
    resp = message_share(token, og_message_id, invalid_message, channel_id, dm_id)
    assert resp.status_code == 400

def test_invalid_token(setup):
    invalid_token = -1
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = setup[3]['channel_id']
    dm_id = -1
    resp = message_share(invalid_token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 403
    
def test_unauthorised_user_dms(setup):
    unauthorised_user = setup[4]['token']
    og_message_id = setup[7]['message_id']
    message = "hello" + "freedom2"
    channel_id = -1
    dm_id = setup[2]['dm_id']
    resp = message_share(unauthorised_user, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 403

def test_unauthorised_user_channels(setup):
    create_channel(setup[1]['token'], "test_channel1", True)
    unauthorised_user = setup[4]['token']
    og_message_id = setup[7]['message_id']
    message = "hello" + "freedom2"
    channel_id = setup[3]['channel_id']
    dm_id = -1
    resp = message_share(unauthorised_user, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 403

def test_invalid_channel_id_noDm(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = 0
    dm_id = -1
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 400

def test_invalid_dm_id_noChannel(setup):
    token = setup[0]['token']
    og_message_id = setup[5]['message_id']
    message = "hello" + "freedom"
    channel_id = -1
    dm_id = 0
    resp = message_share(token, og_message_id, message, channel_id, dm_id)
    assert resp.status_code == 400
