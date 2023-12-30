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

def channel_details(token, channel_id):
    return requests.get(config.url + "channel/details/v2", params={
        'token': token,
        'channel_id': channel_id
    })

@pytest.fixture
def init():
    clear()

    # Creating User and initialising Channel attributes
    user = {
        'email': "elvin@gmail.com",
        'pass': "p@55worD123",
        'first': "Elvin",
        'last': "Manaois",
    }
    
    auth_user = create_user(user['email'], user['pass'], user['first'], user['last'])
    user.update({'auth_user': auth_user})

    channel_name = 'test_1'
    is_public = True

    # Creates Temporary Channel
    chan = create_channel(user['auth_user']['token'], channel_name, is_public)
    channel_id = int(chan['channel_id'])
    channel = {
        'channel_id': channel_id,
        'name': channel_name,
        'is_public': is_public,
    }

    return [user, channel]

# A valid channels_detail function
def test_valid_initial_channel_detail(init):

    details = {
        'name': init[1]['name'],
        'is_public': init[1]['is_public'],
        'owner_members': [
                {
                    'u_id': int(init[0]['auth_user']['auth_user_id']),
                    'email': init[0]['email'],
                    'name_first': init[0]['first'],
                    'name_last': init[0]['last'],
                    'handle_str': (init[0]['first'] + init[0]['last']).lower(),
                    'profile_img_url': ""
                }
            ],
            'all_members': [
            {
                'u_id': int(init[0]['auth_user']['auth_user_id']),
                'email': init[0]['email'],
                'name_first': init[0]['first'],
                'name_last': init[0]['last'],
                'handle_str': (init[0]['first'] + init[0]['last']).lower(),
                'profile_img_url': ""
            }
        ],
    }

    resp = channel_details(init[0]['auth_user']['token'], init[1]['channel_id'])

    assert resp.status_code == 200

    data = resp.json()

    assert data == details

# Invalid channel_id 
def test_invalid_channel_id(init):
    valid_token = init[0]['auth_user']['token']

    # Only one channel has been created so there is no channel 10
    invalid_channel_id = 10   

    resp = channel_details(valid_token, invalid_channel_id)

    assert resp.status_code == 400

def test_invalid_token(init):
    invalid_token = -1

    resp = channel_details(invalid_token, init[1]['channel_id'])

    assert resp.status_code == 403

# Invalid Access Error
def test_invalid_user_id(init):
    # Created a new user not authorised in current channel
    new_user = create_user("elon@gmail.com", "H@ppyT1me123", "Elon", "Musk")

    token = new_user['token']

    valid_channel_id = init[1]['channel_id']

    resp = channel_details(token, valid_channel_id)

    assert resp.status_code == 403