import requests
import json
from src import config

def clear():
    response = requests.delete(config.url + 'clear/v1')
    
    assert response.status_code == 200

def setup():
    clear()
    
    # Registers current user
    response = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": "Elvin",
        "name_last": "Manaois"
    })

    assert response.status_code == 200

    data = response.json()

    return data

''' 
----------------------------------------------------
    Test HTTP Server for Login the account  
----------------------------------------------------
'''
def test_valid_login():
    setup()

    response = requests.post(config.url + "auth/login/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass"
    })

    assert response.status_code == 200

    response_data = response.json()

    assert response_data['auth_user_id'] == 1001

# Test invalid user email
def test_invalid_email():
    setup()
    invalid_email = "avc"
    response = requests.post(config.url + "auth/login/v2", json={
        "email": invalid_email,
        "password": "th1s1s@pass"
    })

    assert response.status_code == 400

# Test for invalid password
def test_invalid_password():
    setup()
    invalid_pass = "123"
    response = requests.post(config.url + "auth/login/v2", json={
        "email": "elvin@gmail.com",
        "password": invalid_pass
    })

    assert response.status_code == 400
    
