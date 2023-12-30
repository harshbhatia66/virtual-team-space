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
    
    u_ids = [user2['auth_user_id'],]
    dm = dm_create(user1['token'], u_ids)

    users = {
        'u_1': user1,
        'u_2': user2,
    }
    return [users, dm]


''' 
----------------------------------------------------
    Test HTTP Server for DM Details
----------------------------------------------------
'''
def test_invalid_dm_id(setup):
    test_users = setup[0]
    user_token = test_users['u_1']['token']
    fake_dm = 6969

    resp = dm_details(user_token, fake_dm)
    assert resp.status_code == 400
    

def test_invalid_user(setup):
    resp = dm_details("this_user_is_invalid", setup[1]['dm_id'])
    assert resp.status_code == 403
    
# ASSUMPTION THAT DM_DETAILS RAISES INPUT BEFORE ACCESS
def test_both_invalid(setup):
    invalid_user = 'this_user_is_invalid'
    fake_dm = 6969
    resp = dm_details(invalid_user, fake_dm)
    assert resp.status_code == 400

def test_details(setup):
    test_users = setup[0]
    user_token = test_users['u_1']['token']
    user_id1 = test_users['u_1']['auth_user_id']
    user_id2 = test_users['u_2']['auth_user_id']

    details_result = dm_details(user_token, setup[1]['dm_id'])

    assert details_result.status_code == 200
    assert details_result.json() == {
        'name': 'arminarlert, erenyaeger',
        'members': [
                {
                    'u_id': user_id1,
                    'email' : "andacrossthesea@gmail.com",
                    'name_first' : 'Eren',
                    'name_last' : 'Yaeger',
                    'handle_str': 'erenyaeger',
                    'profile_img_url': ""
                },

                {
                    'u_id': user_id2,
                    'email': "areourenemies@gmail.com",
                    'name_first': 'Armin', 
                    'name_last': 'Arlert',
                    'handle_str': 'arminarlert',
                    'profile_img_url': ""
                },
   
        ]
    }
