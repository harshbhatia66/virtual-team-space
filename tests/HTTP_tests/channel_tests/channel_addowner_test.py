import pytest
import requests
import json
from src import config
from tests.helper_test import check_user_is_channel_owner
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
    resp = requests.post(config.url + "channel/join/v2", json={
        'token': token,
        'channel_id': channel_id
    })

    assert resp.status_code == 200


def channel_details(token, channel_id):
    return requests.get(config.url + "channel/details/v2", params={
        'token': token,
        'channel_id': channel_id
    }).json()

def channel_addowner(token, channel_id, u_id):
    return requests.post(config.url + "channel/addowner/v1", json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })

'''
----------------------------------------------------
    Test Functions for channel_addowner
----------------------------------------------------
'''

@pytest.fixture
def setup():
    clear()
    # Create users and a channel to populate some messages

    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = create_user("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman")
    user4 = create_user("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger")

    channel_id = create_channel(user1['token'], 'The Sea', True).get('channel_id')

    channel_join(user2['token'], channel_id)

    channel_join(user3['token'], channel_id)


    return [channel_id, user1, user2, user3, user4]

# Make user with user id u_id an owner of the channel.
# Input - { token, channel_id, u_id }, where token is the auth user who has owner permissions and can add owner

# Invalid channel_id 
def test_invalid_channel_id(setup):

    
    invalid_channel_id = -1   

    u_id = setup[2]['auth_user_id']

    resp = channel_addowner(setup[1]['token'], invalid_channel_id, u_id)
    assert resp.status_code == 400

def test_invalid_token(setup):
    invalid_token = -1

    u_id = setup[2]['auth_user_id']

    resp = channel_addowner(invalid_token, setup[0], u_id)
    assert resp.status_code == 403

def test_invalid_u_id(setup):

    # Assume auth_user_id should never be a negative value or less than 1000
    invalid_u_id = -1

    resp = channel_addowner(setup[1]['token'], setup[0], invalid_u_id)
    assert resp.status_code == 400

def test_invalid_member(setup):

    u_id_notmember = setup[4]['auth_user_id']

    resp = channel_addowner(setup[1]['token'], setup[0], u_id_notmember)
    assert resp.status_code == 400

def test_already_owner(setup):

    owner_id = setup[1]['auth_user_id']

    resp = channel_addowner(setup[1]['token'], setup[0], owner_id)
    assert resp.status_code == 400

def test_unauthorised_access(setup):

    u_id = setup[3]['auth_user_id']

    resp = channel_addowner(setup[2]['token'], setup[0], u_id)
    assert resp.status_code == 403

# Valid channel, however token/ auth user does not exist in channel
def test_unauthorised_token(setup):

    u_id = setup[2]['auth_user_id']

    new_user = create_user("kaNwd@gmail.com", "akjwnd234", "awdjn", "awdjn")

    resp = channel_addowner(new_user['token'], setup[0], u_id)
    assert resp.status_code == 403

# Valid test
def test_successful_addowner(setup):

    u_id = setup[2]['auth_user_id']

    resp = channel_addowner(setup[1]['token'], setup[0], u_id)
    assert resp.status_code == 200

     # Use the channel details function to check if owner has been added

    owner_members = channel_details(setup[1]['token'], setup[0]).get('owner_members')

    status = False

    if check_user_is_channel_owner(owner_members, u_id):
        status = True
    
    assert status == True
