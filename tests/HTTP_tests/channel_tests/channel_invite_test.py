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

def channel_invite(token, channel_id, u_id):
    return requests.post(config.url + "channel/invite/v2", json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })

@pytest.fixture
def init():
    clear()
    user1 = create_user("elvin@gmail.com","awdbawd234", "Elvin", "Manaois")
    user2 = create_user('asldkwfj@gmail.com', 'awddjvdwad', 'adkjwdn', 'awddjnv')
    user3 = create_user('asldkdwfj@gmail.com', 'awdjvdawad', 'akjdwdn', 'awdjfnv')

    chan_1 = create_channel(user1['token'], "test_channel1", True)
    chan_2 = create_channel(user2['token'], "test_channel2", False)
    chan_3 = create_channel(user3['token'], "test_channel3", True)

    users = {
        'u_1': user1,
        'u_2': user2,
        'u_3': user3,
    }

    chan_ids = { 
        'chan_1': chan_1.get('channel_id'), 
        'chan_2': chan_2.get('channel_id'), 
        'chan_3': chan_3.get('channel_id'),
    }
    
    return [users, chan_ids]

# test invalid token
def invalid_token(init):
    invalid_token = -1
    chan_id = init[1]['chan_1']
    u_id = init[0]['auth_user_id']
    
    resp = channel_invite(invalid_token, chan_id, u_id)

    assert resp.status_code == 403

# test invalid channel_id
def test_invalid_channel_id(init):
    users = init[0]
    token = users['u_1']['token']
    u_id = users['u_2']['auth_user_id']

    invalid_chan_id = -1

    resp = channel_invite(token, invalid_chan_id, u_id)

    assert resp.status_code == 400    

# test invalid u_id
def test_invalid_u_id(init):
    users = init[0]
    user_1 = users['u_1']['auth_user_id']
    channel_id = init[1]['chan_1']

    # Assume u_id should never be a negative value or less than 1000
    invalid_u_id = -1

    resp = channel_invite(user_1, channel_id, invalid_u_id)
    assert resp.status_code == 400

# test invite someone who is a member already
def test_invalid_invite(init):
    users = init[0]
    user_1 = users['u_1']['token']
    channel_id = init[1]['chan_1']

    # Assume that user 1 is already a member of channel 1
    invalid_invite = users['u_1']['auth_user_id']

    resp = channel_invite(user_1, channel_id, invalid_invite)
    assert resp.status_code == 400

# authorised user is not in the channel
def test_invalid_auth(init):
    users = init[0]
    user_1 = users['u_1']['token']
    user_2 = users['u_2']['auth_user_id']

    # user 1 is not in channel 2
    channel_id = init[1]['chan_3']

    invalid_authurisor = user_1

    resp = channel_invite(invalid_authurisor, channel_id, user_2)
    assert resp.status_code == 403

# Test for a valid channel_invite function
def test_channel_valid(init):
    users = init[0]
    user_1 = users['u_1']['token'] 
    user_2 = int(users['u_2']['auth_user_id'])
    channel_id = init[1]['chan_1']
    
    # User 1 invites user 2 to channel 1
    resp = channel_invite(user_1, channel_id, user_2)
    assert resp.status_code == 200