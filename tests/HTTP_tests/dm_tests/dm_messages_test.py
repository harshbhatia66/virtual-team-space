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

def dm_create(token, u_ids):
    
    resp = requests.post(config.url + "dm/create/v1", json={
        'token': token,
        'u_ids': u_ids
    })
    assert resp.status_code == 200

    return resp.json()


def dm_messages(token, dm_id, start):
    return requests.get(config.url + "dm/messages/v1", params={
        'token': token,
        'dm_id': dm_id,
        'start': start
    })


@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = create_user("chelseaarezo@gmail.com", "comp1531", "Chelsea", "Arezo")
    
    u_ids = [user2['auth_user_id']]
    
    dm_id = dm_create(user1['token'], u_ids).get('dm_id')
    
    return [user1, user3, u_ids, dm_id]


''' 
----------------------------------------------------
    Test HTTP Server for DM Messages
----------------------------------------------------
'''
# Valid DM Message
def test_valid_dm(setup):
    user = setup[0]
    token = user['token']
    dm_id = setup[3]
    start = 0

    resp = dm_messages(token, dm_id, start)
    assert resp.status_code == 200
    
    data = resp.json()
    
    result = {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    
    assert data == result

# Invalid DM ID
def test_invalid_dm_id(setup):
    user = setup[0]
    token = user['token']
    invalid_dm_id = -1
    start = 0
    
    resp = dm_messages(token, invalid_dm_id, start)
    assert resp.status_code == 400

# Negative start index 
def test_negative_start(setup):
    user = setup[0]
    token = user['token']
    dm_id = setup[3]
    invalid_start = -1
    
    resp = dm_messages(token, dm_id, invalid_start)
    assert resp.status_code == 400

# Invalid maximum start index
def test_max_start(setup):
    user = setup[0]
    token = user['token']
    dm_id = setup[3]
    invalid_start = 60
    
    resp = dm_messages(token, dm_id, invalid_start)   
    assert resp.status_code == 400
    
# Negative end index
def test_negative_end(setup):
    user = setup[0]
    token = user['token']
    dm_id = setup[3]
    start = 0
    
    resp = dm_messages(token, dm_id, start)
    assert resp.status_code == 200
    
    data = resp.json()
    assert data['end'] == -1

# Invalid user
def test_invalid_token(setup):
    invalid_token = -1
    dm_id = setup[3]
    start = 0
    
    resp = dm_messages(invalid_token, dm_id, start)   
    assert resp.status_code == 403

# Invalid authoriser 
def test_invalid_user(setup):
    user = setup[1]
    invalid_token = user['token']
    dm_id = setup[3]
    start = 0
    
    resp = dm_messages(invalid_token, dm_id, start)   
    assert resp.status_code == 403
