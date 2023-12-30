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


def auth_logout(token):
    resp = requests.post(config.url + "auth/logout/v1", json={
        'token': token
    })

    return resp

@pytest.fixture
def setup():
    clear()
    user = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")

    return user

''' 
----------------------------------------------------
    Test HTTP Server to Logout the account  
----------------------------------------------------
'''
# Valid logout
def test_valid_logout(setup):
    token = setup['token']
    
    resp = auth_logout(token)

    assert resp.status_code == 200

# Test invalid token
def test_invalid_token(setup):
    invalid_token = -1
    resp = auth_logout(invalid_token)

    assert resp.status_code == 403
