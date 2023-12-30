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

    return resp.json()

def message_senddm(token, dm_id, message):
    resp = requests.post(config.url + "message/senddm/v1", json={
        'token': token,
        'dm_id': dm_id,
        'message': message
    })

    assert resp.status_code == 200

    return resp.json()

def channel_join(token, channel_id):
    resp = requests.post(config.url + "channel/join/v2", json={
        'token': token,
        'channel_id': channel_id
    })

    assert resp.status_code == 200

    return resp.json()

def channel_invite(token, channel_id, u_id):
    resp = requests.post(config.url + "channel/invite/v2", json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })

    assert resp.status_code == 200

    return resp.json()

def message_react_v1(token, message_id, react_id):
    resp = requests.post(config.url + "message/react/v1", json={
        'token': token,
        'message_id': message_id,
        'react_id': react_id
    })

    assert resp.status_code == 200

    return resp.json()

def notifications_get_v1(token):
    return requests.get(config.url + "notifications/get/v1", params={
        'token': token
    })

@pytest.fixture
def channel_test():
    clear()
    user1 = create_user("elvin@gmail.com", "elvinmanaois11", "Elvin", "Manaois")
    user2 = create_user("homer@gmail.com", "homersimpson11", "Homer", "Simpson")

    chan_id = create_channel(user1['token'], "Test_1", True).get('channel_id')

    channel_join(user2['token'], chan_id)

    return [chan_id, user1, user2]

@pytest.fixture
def dm_test():
    clear()
    user1 = create_user("elvin@gmail.com", "elvinmanaois11", "Elvin", "Manaois")
    user2 = create_user("homer@gmail.com", "homersimpson11", "Homer", "Simpson")

    u_ids = [user2['auth_user_id'], ]

    dm_id = dm_create(user1['token'], u_ids).get('dm_id')

    return [dm_id, user1, user2]

def test_invalid_token(channel_test):
    invalid_token = -1
    resp = notifications_get_v1(invalid_token)
    assert resp.status_code == 403

def test_tagged_channel_message(channel_test):
    token = channel_test[1]['token']
    chan_id = channel_test[0]
    msg = "@homersimpson Hello World!"
    message_send(token, chan_id, msg)
    
    user_2_token = channel_test[2]['token']
    resp = notifications_get_v1(user_2_token)

    assert resp.status_code == 200

    notification = resp.json()

    user_handle = "elvinmanaois"
    chan_name = "Test_1"
    notification_msg = f"{user_handle} tagged you in {chan_name}: {msg[:20]}"
    assert notification['notifications'][0] == {
        'channel_id': chan_id,
        'dm_id': -1,
        'notification_message': notification_msg,
    }

def test_tagged_dm_message(dm_test):
    token = dm_test[1]['token']
    dm_id = dm_test[0]
    msg = "@elvinmanaois Hello "

    user_2_token = dm_test[2]['token']
    message_senddm(user_2_token, dm_id, msg)
    
    resp = notifications_get_v1(token)

    assert resp.status_code == 200

    notification = resp.json()

    user_handle = "homersimpson"
    dm_name = "elvinmanaois, homersimpson"
    notification_msg = f"{user_handle} tagged you in {dm_name}: {msg[:20]}"
    assert notification['notifications'][0] == {
        'channel_id': -1,
        'dm_id': dm_id,
        'notification_message': notification_msg,
    }

def test_reacted_channel_message(channel_test):
    token = channel_test[1]['token']
    channel_id = channel_test[0]
    msg = "Hello World!"
    msg_id = message_send(token, channel_id, msg).get('message_id')
    react_id = 1

    user_2_token = channel_test[2]['token']
    message_react_v1(user_2_token, msg_id, react_id)
    
    resp = notifications_get_v1(token)

    assert resp.status_code == 200

    notification = resp.json()

    user_handle = "homersimpson"
    chan_name = "Test_1"
    notification_msg = f"{user_handle} reacted to your message in {chan_name}"
    assert notification['notifications'][0] == {
        'channel_id': channel_id,
        'dm_id': -1,
        'notification_message': notification_msg,
    }

def test_reacted_dm_message(dm_test):
    token = dm_test[1]['token']
    dm_id = dm_test[0]
    msg = "Hello World!"
    msg_id = message_senddm(token, dm_id, msg).get('message_id')
    react_id = 1

    user_2_token = dm_test[2]['token']
    message_react_v1(user_2_token, msg_id, react_id)

    resp = notifications_get_v1(token)

    assert resp.status_code == 200

    notification = resp.json()

    user_handle = "homersimpson"
    dm_name = "elvinmanaois, homersimpson"
    notification_msg = f"{user_handle} reacted to your message in {dm_name}"
    assert notification['notifications'][0] == {
        'channel_id': -1,
        'dm_id': dm_id,
        'notification_message': notification_msg,
    }

def test_channel_join(channel_test):
    token = channel_test[1]['token']
    chan_id = channel_test[0]
    new_user = create_user("florenz@gmail.com", "akwjdnwa123", "florenz", "fulo")

    channel_invite(token, chan_id, new_user['auth_user_id'])
    new_token = new_user['token']

    resp = notifications_get_v1(new_token)

    assert resp.status_code == 200

    notification = resp.json()
    
    user_handle = "elvinmanaois"
    chan_name = "Test_1"
    
    notification_msg = f"{user_handle} added you to {chan_name}"
    assert notification['notifications'][0] == {
        'channel_id': chan_id,
        'dm_id': -1,
        'notification_message': notification_msg,
    }
