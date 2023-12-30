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

def channel_message(token, channel_id, start):
    return requests.get(config.url + "channel/messages/v2", params={
        'token': token,
        'channel_id': channel_id,
        'start': start
    })
    
def channel_join(token, channel_id):
    resp = requests.post(config.url + "channel/join/v2", json={
        'token': token,
        'channel_id': channel_id
    })
    assert resp.status_code == 200

def check_user_is_channel_member(all_members, u_id):
    
    status = False

    for member in all_members:
        if member['u_id'] == u_id:
            status = True
            break
    return status

def channel_addowner(token, channel_id, u_id):
    resp = requests.post(config.url + "channel/addowner/v1", json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })
    assert resp.status_code == 200

def channel_details(token, channel_id):
    resp = requests.get(config.url + "channel/details/v2", params={
        'token': token,
        'channel_id': channel_id
    })
    assert resp.status_code == 200
    return resp.json()

def channel_removeowner(token, channel_id, u_id):
    resp = requests.post(config.url + "channel/removeowner/v1", json={
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    })

    return resp

@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = create_user("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman")
    user4 = create_user("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger")

    channel_id = create_channel(user1['token'], 'The Sea', True).get('channel_id')

    channel_join(user2['token'], channel_id)

    channel_join(user3['token'], channel_id)


    return [channel_id, user1, user2, user3, user4]

def test_invalid_channel_id(setup):
    
    invalid_channel_id = -1   

    u_id = setup[2]['auth_user_id']

    resp = channel_removeowner(setup[1]['token'], invalid_channel_id, u_id)
    assert resp.status_code == 400

def test_invalid_token(setup):
    invalid_token = -1

    u_id = setup[2]['auth_user_id']

    resp = channel_removeowner(invalid_token, setup[0], u_id)
    assert resp.status_code == 403

def test_invalid_u_id(setup):
    
    # Assume auth_user_id should never be a negative value or less than 1000
    invalid_u_id = -1

    resp = channel_removeowner(setup[1]['token'], setup[0], invalid_u_id)
    assert resp.status_code == 400

def test_invalid_member(setup):
    
    u_id_notmember = setup[4]['auth_user_id']

    resp = channel_removeowner(setup[1]['token'], setup[0], u_id_notmember)
    assert resp.status_code == 400

def test_already_not_owner(setup):
    
    u_id = setup[2]['auth_user_id']

    resp = channel_removeowner(setup[1]['token'], setup[0], u_id)
    assert resp.status_code == 400

def test_unauthorised_access(setup):
    
    u_id = setup[1]['auth_user_id']

    resp = channel_removeowner(setup[2]['token'], setup[0], u_id)
    assert resp.status_code == 403

def test_unauthorised_token(setup):
    
    u_id = setup[2]['auth_user_id']

    resp = channel_removeowner(setup[4]['token'], setup[0], u_id)
    assert resp.status_code == 403

def test_removing_single_owner(setup):
    
    u_id = setup[1]['auth_user_id']

    resp = channel_removeowner(setup[1]['token'], setup[0], u_id)
    assert resp.status_code == 400

def test_successful_removeowner(setup):
    
    u_id = setup[2]['auth_user_id']
    channel_addowner(setup[1]['token'], setup[0], u_id)
    
    resp = channel_removeowner(setup[1]['token'], setup[0], u_id)
    assert resp.status_code == 200
