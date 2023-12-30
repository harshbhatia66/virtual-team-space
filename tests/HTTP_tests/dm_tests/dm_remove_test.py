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

def dm_remove(token, dm_id):
    return requests.delete(config.url + "dm/remove/v1", json={
        'token': token,
        'dm_id': dm_id
    })

def dm_list(token):
    return requests.get(config.url + "dm/list/v1", params={
        'token': token
    })


@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = create_user("thisworldiscruel@gmail.com", "alsobeautiful!1!", "Mikasa", "Ackerman")

    u_ids = [user2['auth_user_id'], user3['auth_user_id']]    
    dm = dm_create(user1['token'], u_ids)

    users = {
        'u_1': user1,
        'u_2': user2,
        'u_3': user3,
    }
    return [users, dm]

''' 
----------------------------------------------------
    Test HTTP Server for DM Remove
----------------------------------------------------
'''
def test_invalid_dm_id(setup):
    test_users = setup[0]
    user_token = test_users['u_1']['token']
    fake_dm = 6969

    resp = dm_remove(user_token, fake_dm)
    assert resp.status_code == 400
    
def test_invalid_user(setup):
    resp = dm_remove("this_user_is_invalid", setup[1]['dm_id'])
    assert resp.status_code == 403

def test_not_owner(setup):
    test_users = setup[0]
    user_token = test_users['u_2']['token']

    resp = dm_remove(user_token, setup[1]['dm_id'])
    assert resp.status_code == 403

def test_remove(setup):
    test_users = setup[0]
    owner_token = test_users['u_1']['token']

    dm_remove(owner_token, setup[1]['dm_id'])

    resp = dm_list(owner_token)

    assert resp.status_code == 200
    assert resp.json() == {'dms': []}
    
