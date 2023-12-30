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

def dm_leave(token, dm_id):
    return requests.post(config.url + "dm/leave/v1", json={
        'token': token,
        'dm_id': dm_id
    })

def dm_details(token, dm_id):
    return requests.get(config.url + "dm/details/v1", params={
        'token': token,
        'dm_id': dm_id
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
    Test HTTP Server for DM Leave
----------------------------------------------------
'''
def test_invalid_dm_id(setup):
    test_users = setup[0]
    user_token = test_users['u_1']['token']
    fake_dm = 6969

    resp = dm_leave(user_token, fake_dm)
    assert resp.status_code == 400
    

def test_invalid_user(setup):
    resp = dm_leave("this_user_is_invalid", setup[1]['dm_id'])
    assert resp.status_code == 403
    
# ASSUMPTION THAT DM_LEAVE RAISES INPUT BEFORE ACCESS
def test_both_invalid(setup):
    invalid_user = 'this_user_is_invalid'
    fake_dm = 6969
    resp = dm_leave(invalid_user, fake_dm)
    assert resp.status_code == 400

def test_leave(setup):
    test_users = setup[0]
    user_token = test_users['u_1']['token']
    user_id1 = test_users['u_2']['auth_user_id']
    user_id2 = test_users['u_3']['auth_user_id']

    resp = dm_leave(user_token, setup[1]['dm_id'])
    assert resp.status_code == 200
    current_members = dm_details(test_users['u_3']['token'], setup[1]['dm_id'])

    assert current_members.json() == {
        'name': 'arminarlert, erenyaeger, mikasaackerman',
        'members': [
                {
                    'u_id': user_id1,
                    'email': "areourenemies@gmail.com",
                    'name_first': 'Armin', 
                    'name_last': 'Arlert',
                    'handle_str': 'arminarlert',
                    'profile_img_url': ""
                },
                {
                    'u_id': user_id2,
                    'email' : "thisworldiscruel@gmail.com",
                    'name_first' : 'Mikasa',
                    'name_last' : 'Ackerman',
                    'handle_str': 'mikasaackerman',
                    'profile_img_url': ""
                },
        ]
    }
