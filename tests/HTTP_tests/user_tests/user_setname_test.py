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

def user_profile_setname(token, name_first, name_last):
    resp = requests.put(config.url + "user/profile/setname/v1", json={
        'token': token,
        'name_first': name_first,
        'name_last': name_last
    })

    return resp


@pytest.fixture
def setup():
    clear()
    user = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    name_first = "Eren"
    name_last = "Yaegar"

    return [user, name_first, name_last]


''' 
----------------------------------------------------
    Test HTTP Server to Setname to profile  
----------------------------------------------------
'''
# Valid user
def test_valid_user(setup):
    token = setup[0]['token']
    name_first = setup[1]
    name_last = setup[2]
    resp = user_profile_setname(token, name_first, name_last)
    assert resp.status_code == 200

# Invalid token
def test_invalid_token(setup):
    invalid_token = -1
    name_first = setup[1]
    name_last = setup[2]

    resp = user_profile_setname(invalid_token, name_first, name_last)
    assert resp.status_code == 403

# Invalid name_first (name < 1 or name > 50)
def test_invalid_name_first(setup):
    token = setup[0]['token']
    invalid_name_first_50 = "abcdefgjienfnfkdjsnvsdjnvfsjdfnjsfjwehfwuhfjsdfnjknfvsjkfbnjfbcsdfsf"
    invalid_name_first_1 = ""
    name_last = setup[2]
    resp1 = user_profile_setname(token, invalid_name_first_50, name_last)
    resp2 = user_profile_setname(token, invalid_name_first_1, name_last)
    assert resp1.status_code == 400
    assert resp2.status_code == 400

# Invalid name_last (name < 1 or name > 50)
def test_invalid_name_last(setup):
    token = setup[0]['token']
    name_first = setup[1]
    invalid_name_last_50 = "abcdefgjienfnfkdjsnvsdjnvfsjdfnjsfjwehfwuhfjsdfnjknfvsjkfbnjfbcsdfsf"
    invalid_name_last_1 = ""
    resp1 = user_profile_setname(token, name_first, invalid_name_last_50)
    resp2 = user_profile_setname(token, name_first, invalid_name_last_1)
    assert resp1.status_code == 400
    assert resp2.status_code == 400
