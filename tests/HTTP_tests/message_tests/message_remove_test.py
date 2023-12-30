from tracemalloc import start
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
    resp =  requests.post(config.url + "message/send/v1", json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

    assert resp.status_code == 200
    return resp.json()

def message_remove(token, message_id):
    return requests.delete(config.url + "message/remove/v1", json={
        'token': token,
        'message_id': message_id
    })

def channel_join(token, channel_id):
    return requests.delete(config.url + "channel/join/v2", params={
        'token': token,
        'channel_id': channel_id
    })

def channel_messages(token, channel_id, start):
    return requests.get(config.url + "channel/messages/v2", params={
        'token': token,
        'channel_id': channel_id,
        'start': start
    }).json()
    
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
    Test for Messages Remove
--------------------------------------------------------
'''
@pytest.fixture
def setup():
    clear()
    # Create users and a channel to populate some messages
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger").get('token')
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert").get('token')
    user3 = create_user("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman").get('token')
    user4 = create_user("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger").get('token')

    channel_id1 = create_channel(user1, 'The Sea', True).get('channel_id')

    channel_join(user2, channel_id1)
    channel_join(user3, channel_id1)

    msg = message_send(user1, channel_id1, "Umi").get('message_id')

    return [msg, user1, user2, user3, user4, channel_id1]

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

# If the message does not exist in any of the users channels/dms
def test_invalid_message_id(setup):
    resp = message_remove(setup[4], setup[0])
    assert resp.status_code == 400
    
def test_invalid_message_id2(setup2):
    resp = message_remove(setup2[4]['token'], setup2[0])
    assert resp.status_code == 400
        
def test_invalid_token(setup):
    invalid_token = -1
    resp = message_remove(invalid_token, setup[0])
    assert resp.status_code == 403

# Need to double check on this, this should return 403
def test_unauthorised_edit(setup):
    resp = message_remove(setup[3], setup[0])
    assert resp.status_code == 400
    
def test_unauthorised_edit2(setup2):
    resp = message_remove(setup2[3], setup2[0])
    assert resp.status_code == 403

# Testing for a successful message edit if the user did not send the message but has owner permissions to edit
def test_permission(setup):
    # Authorised user with owner permission tries to remove message
    resp = message_remove(setup[1], setup[0])
    assert resp.status_code == 200
    msgs = channel_messages(setup[1], setup[5], 0).get('messages')
    assert len(msgs) == 0
    
def test_permission2(setup2):
    resp = message_remove(setup2[1]['token'], setup2[0])
    assert resp.status_code == 200
    msgs = dm_messages(setup2[1]['token'], setup2[5], 0).get('messages')
    assert len(msgs) == 0

def test_successful_remove(setup):
    resp = message_remove(setup[1], setup[0])
    assert resp.status_code == 200
    msgs = channel_messages(setup[1], setup[5], 0).get('messages')
    assert len(msgs) == 0
    
def test_successful_remove2(setup2):
    resp = message_remove(setup2[1]['token'], setup2[0])
    assert resp.status_code == 200
    msgs = dm_messages(setup2[1]['token'], setup2[5], 0).get('messages')
    assert len(msgs) == 0
