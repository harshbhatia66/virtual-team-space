import pytest
import requests
from src import config
import time

def clear():
    response = requests.delete(config.url + '/clear/v1')
    
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

def channel_join(token, channel_id):
    resp = requests.post(config.url + "channel/join/v2", json={
        'token': token,
        'channel_id': channel_id
    })
    assert resp.status_code == 200
    return resp.json()

def standup_active(token, channel_id):
    return requests.get(config.url + "/standup/active/v1", params={
        'token': token,
        'channel_id': channel_id
    })

def standup_start(token, channel_id, length):
    return requests.post(config.url + "/standup/start/v1", json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })

def standup_send(token, channel_id, message):
    return requests.post(config.url + "/standup/send/v1", json={
        "token": token,
        "channel_id": channel_id,
        "message": message
    })

'''
--------------------------------------------------------
    Setup for Standup tests
--------------------------------------------------------
'''
@pytest.fixture 
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    channel_id1 = create_channel(user1['token'], 'The Sea', True).get('channel_id')

    users = {
        'u_1': user1,
        'channel': int(channel_id1)
    }
    return users

'''
--------------------------------------------------------
    Tests for Standup
--------------------------------------------------------
'''
def test_standup_start_valid(setup):
    resp_start = standup_start(setup['u_1']['token'], setup['channel'], 1)
    assert resp_start.status_code == 200


def test_standup_active_true(setup):
    standup_start(setup['u_1']['token'], setup['channel'], 15)

    resp_active = standup_active(setup['u_1']['token'], setup['channel'])
    assert resp_active.status_code == 200
    # data = resp_active.json()
    # assert data['is_active'] == True

def test_standup_active_false(setup):
    resp_start = standup_start(setup['u_1']['token'], setup['channel'], 1)
    assert resp_start.status_code == 200    

    # delays the program for two seconds
    time.sleep(2)
    resp_active = standup_active(setup['u_1']['token'], setup['channel'])
    assert resp_active.status_code == 200
    data = resp_active.json()
    assert data['is_active'] == False
    assert data['time_finish'] == None

def test_standup_send(setup):
    resp_start = standup_start(setup['u_1']['token'], setup['channel'], 15)
    assert resp_start.status_code == 200

    resp_active = standup_active(setup['u_1']['token'], setup['channel'])
    assert resp_active.status_code == 200
    data = resp_active.json()
    assert data['is_active'] == True

    resp_send = standup_send(setup['u_1']['token'], setup['channel'], "Hello, World!")
    assert resp_send.status_code == 200


# def test_standup_send_multiple_users(setup):
#     user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
#     channel_join(user2['token'], setup['channel'])

#     standup_start(setup['u_1']['token'], setup['channel'], 15)

#     resp_send = standup_send(user2['token'], setup['channel'], "Hello, Eren!")
#     assert resp_send.status_code == 200