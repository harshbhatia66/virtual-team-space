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


def message_edit(token, message_id, message):
    return requests.put(config.url + "message/edit/v1", json={
        'token': token,
        'message_id': message_id,
        'message': message
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
    Test for Messages Edit on channels
--------------------------------------------------------
'''
@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = create_user("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman")
    user4 = create_user("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger")

    chan = create_channel(user1['token'], "Test01", True)

    channel_join(user2['token'], chan['channel_id'])

    channel_join(user3['token'], chan['channel_id'])

    msg_id = message_send(user1['token'], chan['channel_id'], "Hello World!")

    return [msg_id, user1, user2, user3, user4, chan]

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

def test_invalid_token(setup):
    invalid_token = -1
    resp = message_edit(invalid_token, int(setup[0]['message_id']), "Hello World")
    assert resp.status_code == 403

def test_message_over_1000_character(setup):
    msg = "a" * 1001

    resp = message_edit(setup[1]['token'], int(setup[0]['message_id']), msg)
    assert resp.status_code == 400

def test_invalid_message_id(setup):
    msg = "Hello World"
    resp = message_edit(setup[4]['token'], int(setup[0]['message_id']), msg)
    assert resp.status_code == 400
    
def test_invalid_message_id2(setup2):
    msg = "Hello World"
    resp = message_edit(setup2[4]['token'], int(setup2[0]), msg)
    assert resp.status_code == 400

def test_unauthorised_edit(setup):
    msg = "Hello World"
    resp = message_edit(setup[2]['token'], int(setup[0]['message_id']), msg)
    assert resp.status_code == 403
    
def test_unauthorised_edit2(setup2):
    msg = "Hello World"
    resp = message_edit(setup2[3]['token'], int(setup2[0]), msg)
    assert resp.status_code == 403

def test_permission(setup):
    msg_id = message_send(setup[3]['token'], int(setup[5]['channel_id']), "test")['message_id']
    
    message_edit(setup[1]['token'], msg_id, "Rumbling")

    msgs = channel_messages(setup[1]['token'], setup[5]['channel_id'], 0)['messages']

    new_msg = msgs[0]['message']

    # Checking if the message was edited successfully
    assert new_msg == "Rumbling"

def test_permission2(setup2):
    msg_id = message_senddms(setup2[3]['token'], int(setup2[5]), "test")['message_id']
    
    message_edit(setup2[1]['token'], msg_id, "Rumbling")

    msgs = dm_messages(setup2[1]['token'], setup2[5], 0)['messages']

    new_msg = msgs[0]['message']

    # Checking if the message was edited successfully
    assert new_msg == "Rumbling"

def test_successful_edit(setup):
    message_edit(setup[1]['token'], setup[0]['message_id'], "Freedom")

    msgs = channel_messages(setup[1]['token'], int(setup[5]['channel_id']), 0)['messages']

    new_msg = msgs[0]['message']

    # Checking if the message was edited successfully
    assert new_msg == "Freedom"
    
def test_successful_edit2(setup2):
    message_edit(setup2[1]['token'], setup2[0], "Freedom")

    msgs = dm_messages(setup2[1]['token'], int(setup2[5]), 0)['messages']

    new_msg = msgs[0]['message']

    # Checking if the message was edited successfully
    assert new_msg == "Freedom"

def test_empty_string(setup):
    message_edit(setup[1]['token'], setup[0]['message_id'], "")
    msgs = channel_messages(setup[1]['token'], setup[5]['channel_id'], 0).get('messages')
    assert len(msgs) == 0

def test_empty_string2(setup2):
    message_edit(setup2[1]['token'], setup2[0], "")
    msgs = dm_messages(setup2[1]['token'], setup2[5], 0).get('messages')
    assert len(msgs) == 0
