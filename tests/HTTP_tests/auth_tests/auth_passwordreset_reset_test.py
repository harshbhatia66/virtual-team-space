import pytest
import requests
import json
from src.other import random_code
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


def passwordreset_request(email):
    resp = requests.post(config.url + "auth/passwordreset/request/v1", json={
        "email": email
    })
    assert resp.status_code == 200
    
    return resp

def passwordreset_reset(reset_code, new_password):
    resp = requests.post(config.url + "auth/passwordreset/reset/v1", json={
        "reset_code": reset_code,
        "new_password": new_password
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
    Test HTTP Server for Password Reset 
----------------------------------------------------
'''

def test_invalid_code(setup):
    email = setup[0]
    invalid_code = -1
    new_password = "COMP1531"
    passwordreset_request(email)
    resp = passwordreset_reset(invalid_code, new_password)
    assert resp.status_code == 400

def test_invalid_password(setup):
    email = setup[0]
    N = 8
    reset_code = random_code(N)
    invalid_password = "C"
    passwordreset_request(email)
    resp = passwordreset_reset(reset_code, invalid_password)
    assert resp.status_code == 400
