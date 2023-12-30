import pytest
import requests
import json
from src import config
from tests.HTTP_tests.message_tests.message_senddms_test import create_dm

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

def user_stats_v1(token):
    return requests.get(config.url + "user/stats/v1", params={
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

    resp =  user_stats_v1(invalid_token)
    assert resp.status_code == 403

def test_zero_involvement(user1):

    token = user1['token']

    resp = user_stats_v1(token)

    assert resp.status_code == 200

    stats = resp.json()

    assert stats['user_stats']['involvement_rate'] == 0

def test_first_channel_created(user1):

    token = user1['token']

    create_channel(token, "Test_1", True)

    resp = user_stats_v1(token)

    assert resp.status_code == 200

    stats = resp.json()

    assert stats['user_stats']['channels_joined'][0]['num_channels_joined'] == 1

def test_first_dm_created(user1):
    token = user1['token']

    user2 = create_user("yessr@gmail.com", "thisisaver124234", "Yes", "Sir")
    u_ids = [user2['auth_user_id'], ]

    create_dm(token, u_ids)

    resp = user_stats_v1(token)

    assert resp.status_code == 200

    stats = resp.json()

    assert stats['user_stats']['dms_joined'][0]['num_dms_joined'] == 1

def test_channel_msg(user1):
    token = user1['token']

    chan_id = create_channel(token, "Test_1", True).get('channel_id')

    message_send(token, chan_id, "Test_1")

    resp = user_stats_v1(token)

    assert resp.status_code == 200

    stats = resp.json()

    assert stats['user_stats']['messages_sent'][0]['num_messages_sent'] == 1

def test_dm_msg(user1):
    token = user1['token']

    user2 = create_user("yessr@gmail.com", "thisisaver124234", "Yes", "Sir")
    u_ids = [user2['auth_user_id'], ]

    dm_id = create_dm(token, u_ids).get('dm_id')

    dm_id = message_senddm(token, dm_id, "Test 1")

    resp = user_stats_v1(token)

    assert resp.status_code == 200
    
    stats = resp.json()

    assert len(stats['user_stats']['messages_sent']) == 1

    assert stats['user_stats']['messages_sent'][0]['num_messages_sent'] == 1