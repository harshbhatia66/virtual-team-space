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

def dm_list(token):
    return requests.get(config.url + "dm/list/v1", params={
        'token': token
    })


@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    
    u_ids = [user2['auth_user_id']]
    
    dm = dm_create(user1['token'], u_ids)
    
    return [user1, u_ids, dm]


''' 
----------------------------------------------------
    Test HTTP Server for DM List
----------------------------------------------------
'''
# Valid DM
def test_valid_dm(setup):
    user = setup[0]
    token = user['token']

    resp = dm_list(token)
    assert resp.status_code == 200
    
    data = resp.json()
    
    result = {
        'dms': [
            {
                'dm_id': 1,
                'name': 'arminarlert, erenyaeger'
            },
        ]
    }
    assert data == result

# Valid DM List
def test_valid_dm_list(setup):
    user = setup[0]
    token = user['token']

    resp = dm_list(token)
    assert resp.status_code == 200
    
# Invalid token
def test_invalid_token(setup):
    invalid_token = -1 
    resp = dm_list(invalid_token)
    assert resp.status_code == 403
