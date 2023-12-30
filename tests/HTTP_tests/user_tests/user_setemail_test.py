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

def set_user_email(token, email):
    response = requests.put(config.url + "user/profile/setemail/v1", json={
        "token": token,
        "email": email 
    })
    return response

def user_all(token):
    response = requests.get(config.url + "users/all/v1", params={
        "token": token
    })
    assert response.status_code == 200
    user = response.json()
    return user

@pytest.fixture
def users():
    clear()
    user1 = create_user("thisworldiscruel@gmail.com", "tatakae!1!", "Mikasa", "Ackerman")
    user2 = create_user("butistillloveyou@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    users = {
        'u_1': user1,
        'u_2': user2,
    }

    return users

''' 
----------------------------------------------------
    Test HTTP Server for Set User Email
----------------------------------------------------
'''
def test_duplicate_email(users):
    user_token = users['u_1']['token']
    dupe_email = "butistillloveyou@gmail.com"
    resp = set_user_email(user_token, dupe_email)
    assert resp.status_code == 400

def test_invalid_email(users):
    user_token = users['u_1']['token']
    not_email = "this_is_not_an_email"
    resp = set_user_email(user_token, not_email)
    assert resp.status_code == 400

def test_setemail(users):
    user_token = users['u_1']['token']
    new_email = "butitisbeautiful@gmail.com"
    resp = set_user_email(user_token, new_email)

    assert resp.status_code == 200
    result = user_all(user_token)

    assert result == {
        'users' : [
                {
                    'u_id': users['u_1']['auth_user_id'],
                    'email': "butitisbeautiful@gmail.com",
                    'name_first': 'Mikasa', 
                    'name_last': 'Ackerman',
                    'handle_str': 'mikasaackerman',
                    'profile_img_url': ""
                },
                {
                    'u_id': users['u_2']['auth_user_id'],
                    'email' : "butistillloveyou@gmail.com",
                    'name_first' : 'Eren',
                    'name_last' : 'Yaeger',
                    'handle_str': 'erenyaeger',
                    'profile_img_url': ""
                },
        ]
    }
