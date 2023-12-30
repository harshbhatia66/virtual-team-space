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

def channel_join(token, channel_id):
    return requests.post(config.url + "channel/join/v2", json={
        'token': token,
        'channel_id': channel_id
    })

@pytest.fixture
def init():
    clear()

    user = {
        'email': 'elvin@gmail.com',
        'pass': 'NowWatchMeWhip',
        'first': 'Elvin',
        'last': 'Manaois',
    }

    auth_user = create_user(user['email'], user['pass'], user['first'], user['last'])
    user.update({'auth_user': auth_user})

    channel = {
        'name': 'test_1',
        'is_public': True,
    }
    
    channel_val = create_channel(user['auth_user']['token'], channel['name'], channel['is_public'])
    channel_id = int(channel_val.get('channel_id'))
    channel.update({'channel_id': channel_id})

    return [user, channel]

# Test invalid token
def test_invalid_token(init):
    invalid_token = 'awd'

    resp = channel_join(invalid_token, init[1]['channel_id'])

    assert resp.status_code == 403

# Checks whether the channel_id does not refer to a valid channel
def test_invalid_channel_id(init):
    invalid_channel_id = 10

    resp = channel_join(init[0]['auth_user']['token'], invalid_channel_id)

    assert resp.status_code == 400

# Check whether the auth user is already an owner member of the channel
def test_user_owner_member(init):
    resp = channel_join(init[0]['auth_user']['token'], init[1]['channel_id'])
    assert resp.status_code == 400

def test_user_member(init):
    channel_id = init[1]['channel_id']
    new_user = create_user("yessir@yahoo.com", "thisiadnwwd", "Yes", "No")

    channel_join(new_user['token'], channel_id)

    resp = channel_join(new_user['token'], channel_id)
    
    assert resp.status_code == 400

# Checks the channel if its private if so will trigger an Acces Error
def test_private_access(init):

    # Creates new user that isn't in the channel
    auth_id = create_user("yes@gmail.com", "thisisapass123", "Yes", "No")
    new_token = auth_id.get('token')

    # New User 2
    user2 = create_user("akjwdn@gmail.com", "alwdnaw", "akjwdn", "oawkndawd")
    user2_token = user2.get('token')

    # Creates new channel and changes the status of the channel to private
    channel_name = "test_2"
    is_public = False
    new_channel_id = int(create_channel(new_token, channel_name, is_public).get('channel_id'))

    resp = channel_join(user2_token, new_channel_id)
    assert resp.status_code == 403

def test_valid_join(init):
    # Get the public channel_id new user will join too
    channel_id = init[1]['channel_id']

    # Creates new user that isn't in the channel
    auth_user = create_user("yes@gmail.com", "thisisapass123", "Yes", "No")
    
    # Attempt to join the new user to a public channel
    resp = channel_join(auth_user['token'], channel_id)
    assert resp.status_code == 200
