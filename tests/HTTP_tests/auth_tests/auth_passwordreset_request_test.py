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

    return resp.status_code == 200

def passwordreset_request(email):
    resp = requests.post(config.url + "auth/passwordreset/request/v1", json={
        "email": email
    })
    return resp

@pytest.fixture
def setup():
    clear()
    email = "andacrossthesea@gmail.com"
    password = "TATAKAE!1!"
    name_first = "Eren"
    name_last = "Yaeger"
    return [email, password, name_first, name_last]

''' 
----------------------------------------------------
    Test HTTP Server for Password Reset Request  
----------------------------------------------------
'''

# Test for Valid Request
def test_valid_request(setup):
    email = setup[0]
    token = create_user(setup[0], setup[1], setup[2], setup[3]).get('token')
    auth_logout(token)
    resp = passwordreset_request(email)
    assert resp.status_code == 200
