from urllib import response
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
    resp = requests.post(config.url + "message/send/v1", json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

    assert resp.status_code == 200

    message_id = resp.json()

    return message_id

def channel_join(token, channel_id):
    return requests.post(config.url + "channel/join/v2", json={
        'token': token,
        'channel_id': channel_id
    })


def message_pin_v1(token, message_id):
    resp = requests.post(config.url + "message/pin/v1", json={
        'token': token,
        'message_id': message_id,
    })
    
    assert resp.status_code == 200
    
    return resp  

def message_unpin_v1(token, message_id):
    return requests.post(config.url + "message/unpin/v1", json={
        'token': token,
        'message_id': message_id,
    })

def channel_messages(token, channel_id, start):
    resp = requests.get(config.url + "channel/messages/v2", params={
        'token': token,
        'channel_id': channel_id,
        'start': start
    })

    assert resp.status_code == 200

    messages = resp.json()

    return messages

def dm_create(token, u_ids):
    resp = requests.post(config.url + "dm/create/v1", json={
        'token': token,
        'u_ids': u_ids
    })
    assert resp.status_code == 200
    return resp.json()

def message_senddms(token, dm_id, message):
    resp = requests.post(config.url + "message/senddm/v1", json={
        'token': token,
        'dm_id': dm_id,
        'message': message
    })
    assert resp.status_code == 200
    return resp.json()
    
def dm_messages(token, dm_id, start):
    return requests.get(config.url + "dm/messages/v1", params={
        'token': token,
        'dm_id': dm_id,
        'start': start
    }).json()
'''
--------------------------------------------------------
    Test for Messages Pin on channels
--------------------------------------------------------
'''
@pytest.fixture
def setup1():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = create_user("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman")
    user4 = create_user("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger")

    chan = create_channel(user1['token'], "Test01", True)
    
    channel_join(user2['token'], chan['channel_id'])

    channel_join(user3['token'], chan['channel_id'])

    msg_id = message_send(user1['token'], chan['channel_id'], "Hello World!").get('message_id')

    return [msg_id, user1, user2, user3, user4, chan['channel_id']]

@pytest.fixture
def setup2():
    clear()
    # Create users and creates dm 

    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = create_user("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman")
    user4 = create_user("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger")

    dm_id = dm_create(user1['token'], [user2['auth_user_id'], user3['auth_user_id']])['dm_id']

    msg = message_senddms(user2['token'], dm_id, "Umi").get('message_id')

    return [msg, user1, user2, user3, user4, dm_id]

# When message ID doesn't exist - Channel
def test_invalid_message_id(setup1):
    resp = message_unpin_v1(setup1[1]['token'], 1729)
    assert resp.status_code == 400
    
# When user in not a part of the dm/channel where message id is in - Channel
def test_unauthorised_message_id1(setup1):
    resp = message_unpin_v1(setup1[4]['token'], setup1[0])
    assert resp.status_code == 400
    
# When user in not a part of the dm/channel where message id is in - DM
def test_unauthorised_message_id2(setup2):
    resp = message_unpin_v1(setup2[4]['token'], setup2[0])
    assert resp.status_code == 400
    
# When user does not exist/ Invalid Token
def test_invalid_token(setup1):
    invalid_token = -1
    resp = message_unpin_v1(invalid_token, setup1[0])
    assert resp.status_code == 403
    
# When the message was already unpinned - channel
def test_already_unpinned(setup1):
    resp = message_unpin_v1(setup1[1]['token'], setup1[0])
    assert resp.status_code == 400
    
# When the message was already unpinned - dm
def test_already_unpinned2(setup2):
    resp = message_unpin_v1(setup2[1]['token'], setup2[0])    
    assert resp.status_code == 400
    
# User does not have permissions - channel
def test_owner_permissions1(setup1):
    message_pin_v1(setup1[1]['token'], setup1[0])
    resp = message_unpin_v1(setup1[2]['token'], setup1[0])
    assert resp.status_code == 403
    
# User does not have permissions - dm
def test_owner_permissions2(setup2):
    message_pin_v1(setup2[1]['token'], setup2[0])
    resp = message_unpin_v1(setup2[2]['token'], setup2[0])
    assert resp.status_code == 403
    
# Test successful unpin - Channel
def test_successful_pin1(setup1):
    message_pin_v1(setup1[1]['token'], setup1[0])
    message_unpin_v1(setup1[1]['token'], setup1[0])
    msgs = channel_messages(setup1[2]['token'], setup1[5], 0).get('messages')
    msg_unpin_status = msgs[0].get('is_pinned')
    assert msg_unpin_status == False
    
# Test successful unpin - DM
def test_successful_pin2(setup2):
    message_pin_v1(setup2[1]['token'], setup2[0])
    message_unpin_v1(setup2[1]['token'], setup2[0])
    msgs = dm_messages(setup2[2]['token'], setup2[5], 0).get('messages')
    print(msgs)
    msg_unpin_status = msgs[0].get('is_pinned')
    assert msg_unpin_status == False