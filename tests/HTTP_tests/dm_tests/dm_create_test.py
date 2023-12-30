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

    return resp


@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    
    users = {
        'u_1': user1,
        'u_2': user2,
    }
    return [users]


''' 
----------------------------------------------------
    Test HTTP Server for DM Create
----------------------------------------------------
'''
# Valid DM Create
def test_valid_dm(setup):
    user = setup[0]
    token = user['u_1']['token']
    valid_id = user['u_2']['auth_user_id']
    u_ids = [valid_id, ]
    resp = dm_create(token, u_ids) 
    assert resp.status_code == 200
    
    resp_data = resp.json()
    
    assert resp_data['dm_id'] == 1

# Invalid token
def test_invalid_token(setup):
    user = setup[0]
    invalid_token = -1
    valid_id = user['u_1']['auth_user_id']
    u_ids = [valid_id, ]
    resp = dm_create(invalid_token, u_ids) 
    assert resp.status_code == 403

# Invalid u_id in u_ids
def test_invalid_u_id(setup):
    user = setup[0]
    token = user['u_1']['token']
    invalid_id = -1
    invalid_u_ids = [invalid_id, ]
    
    resp = dm_create(token, invalid_u_ids)
    assert resp.status_code == 400

# Duplicate u_id in u_ids
def test_duplicate_u_id(setup):
    user = setup[0]
    token = user['u_1']['token']
    dup_id = 1002
    duplicate_u_ids = [dup_id, dup_id]
    
    resp = dm_create(token, duplicate_u_ids)
    assert resp.status_code == 400

# Owner of DM in u_ids
def test_owner_in_u_ids(setup):
    user = setup[0]
    token = user['u_1']['token']
    u_id_owner = user['u_1']['auth_user_id']
    u_ids = [u_id_owner, ]

    resp = dm_create(token, u_ids)
    assert resp.status_code == 400
