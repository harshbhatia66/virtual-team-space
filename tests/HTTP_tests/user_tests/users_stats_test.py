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

def users_stats_v1(token):
    return requests.get(config.url + "users/stats/v1", params={
        'token': token
    })

@pytest.fixture
def user1():
    clear()

    user1 = create_user("elvin@gmail.com", "elvinmanaois11", "Elvin", "Manaois")

    return user1

def test_invalid_token():
    clear()

    invalid_token = -1

    resp = users_stats_v1(invalid_token)
    assert resp.status_code == 403

def test_zero_utilization_rate(user1):
    token = user1['token']

    resp =  users_stats_v1(token)

    assert resp.status_code == 200

    stats = resp.json()

    assert stats['workspace_stats']['utilization_rate'] == 0

def test_no_active_user(user1):
    token = user1['token']

    resp =  users_stats_v1(token)

    assert resp.status_code == 200

def test_channel_member(user1):
    token = user1['token']

    create_channel(token, "Test_1", True)

    resp =  users_stats_v1(token)

    assert resp.status_code == 200

    stats = users_stats_v1(token).json()

    assert stats['workspace_stats']['channels_exist'][1]['num_channels_exist'] == 1

def test_dm_member(user1):
    token = user1['token']

    user2 = create_user("yessr@gmail.com", "thisisaver124234", "Yes", "Sir")
    u_ids = [user2['auth_user_id'], ]

    dm_create(token, u_ids)

    resp =  users_stats_v1(token)

    assert resp.status_code == 200

    stats = users_stats_v1(token).json()

    assert stats['workspace_stats']['dms_exist'][1]['num_dms_exist'] == 1

def test_channel_msg(user1):
    token = user1['token']

    chan_id = create_channel(token, "Test_1", True).get('channel_id')

    message_send(token, chan_id, "Test_1")

    resp =  users_stats_v1(token)

    assert resp.status_code == 200

    stats = users_stats_v1(token).json()

    assert stats['workspace_stats']['messages_exist'][1]['num_messages_exist'] == 1

def test_dm_msg(user1):
    token = user1['token']

    user2 = create_user("yessr@gmail.com", "thisisaver124234", "Yes", "Sir")
    u_ids = [user2['auth_user_id'], ]

    dm_id = dm_create(token, u_ids).get('dm_id')
    
    message_senddm(token, dm_id, "Test")

    resp =  users_stats_v1(token)

    assert resp.status_code == 200

    stats = users_stats_v1(token).json()

    assert stats['workspace_stats']['messages_exist'][1]['num_messages_exist'] == 1