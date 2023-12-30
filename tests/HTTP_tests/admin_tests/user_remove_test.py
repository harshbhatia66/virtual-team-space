import pytest
import requests
import json
from src import config
from src import admin as Admin

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

def channel_invite(token, channel_id, u_id):
    return requests.post(config.url + "channel/invite/v2", json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })

def change_user_permission(token, u_id, permission_id):
    return requests.post(config.url + "admin/userpermission/change/v1", json={
        'token': token,
        'u_id': u_id,
        'permission_id': permission_id
    })

def message_send(token, channel_id, message):
    return requests.post(config.url + "/message/send/v1", json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

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

def user_remove(token, u_id):
    return requests.delete(config.url + "admin/user/remove/v1", json={
        'token': token, 
        'u_id': u_id
    })

@pytest.fixture
def init():
    clear()

    user1 = create_user("elvin@gmail.com", "awdahwd1234", "Elvin", "Manaois")
    user2 = create_user("akwjdna@yahoo.com", "awdjn1234", "Chels", "Yes")

    return [user1, user2]

def test_invalid_token(init):
    invalid_token = -1
    u_id = init[1]['auth_user_id']

    resp = user_remove(invalid_token, u_id)
    assert resp.status_code == 403

def test_invalid_u_id(init):
    token = init[0]['token']
    invalid_id = -1

    resp = user_remove(token, invalid_id)
    assert resp.status_code == 400

# Tests for a user that is the only global member
# Input Error
def test_u_id_only_global_member(init):
    token = init[0]['token']
    only_u_id = init[0]['auth_user_id']

    resp = user_remove(token, only_u_id)
    assert resp.status_code == 400

# Tests for an auth user that is not a global member
# Access Error
def test_auth_user_not_global_member(init):
    new_user = create_user("awdjba@gmail.com", "awdjn232344", "awdjn", "awdjbb")
    token = init[1]['token']
    u_id = new_user['auth_user_id']

    resp = user_remove(token, u_id)
    assert resp.status_code == 403

# Tests for valid user_remove_v1()
def test_valid_user_remove_v1(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    resp = user_remove(token, u_id)
    assert resp.status_code == 200

def test_u_id_in_channel(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    chan = create_channel(token, "Test_Channel_1", True)
    chan_id = chan['channel_id']

    channel_invite(token, chan_id, u_id)

    resp = user_remove(token, u_id)
    assert resp.status_code == 200

def test_u_id_chan_message(init):
    
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    chan = create_channel(token, "Test_Channel_1", True)
    chan_id = chan['channel_id']

    channel_invite(token, chan_id, u_id)

    u_id_token = init[1]['token']
    message_send(u_id_token, chan_id, "Hello World")


    resp = user_remove(token, u_id)
    assert resp.status_code == 200

def test_u_id_chan_no_msg(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    chan = create_channel(token, "Test_Channel_1", True)
    chan_id = chan['channel_id']

    channel_invite(token, chan_id, u_id)

    message_send(token, chan_id, "Hello World")

    resp = user_remove(token, u_id)
    assert resp.status_code == 200

def test_u_id_not_member(init):
    new_user = create_user("awdj@gmail.com", "awkjdna124", "wadjn", "awdfg")

    token = init[0]['token']

    create_channel(token, "Test_Channel_1", True)

    resp = user_remove(token, new_user['auth_user_id'])
    assert resp.status_code == 200

def test_more_than_one_global_owner(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    change_user_permission(token, u_id, Admin.OWNER)

    resp = user_remove(token, u_id)
    assert resp.status_code == 200

def test_dm_create(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    create_dm(token, [u_id])

    resp = user_remove(token, u_id)
    assert resp.status_code == 200

def test_dm_message(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    
    dm_id = create_dm(token, [u_id]).get('dm_id')

    u_id_token = init[1]['token']
    message_senddm(u_id_token, dm_id, "Hello")

    resp = user_remove(token, u_id)
    assert resp.status_code == 200

def test_dm_no_message(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    
    dm_id = create_dm(token, [u_id]).get('dm_id')

    message_senddm(token, dm_id, "Hello")

    resp = user_remove(token, u_id)
    assert resp.status_code == 200

def test_no_dms(init):
    new_user = create_user("awdj@gmail.com", "awkjdna124", "wadjn", "awdfg")

    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    create_dm(token, [u_id]).get('dm_id')

    resp = user_remove(token, new_user['auth_user_id'])
    assert resp.status_code == 200
