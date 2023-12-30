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
    Test HTTP Server for channels create
----------------------------------------------------
'''

# Invalid token
def test_invalid_token():
    setup()
    invalid_token = -1
    name = "literallyanything"
    is_public = True

    resp = requests.post(config.url + "channels/create/v2", json={
        "token": invalid_token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 403

# Testing invalid name lengths
def test_channels_name_len_1():
    user = setup()
    token = user['token']

    invalid_name = ""
    is_public = True

    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": invalid_name,
        "is_public": is_public
    })
    
    assert resp.status_code == 400

# Testing invalid name length
def test_channels_name_len_20():
    user = setup()
    token = user['token']

    invalid_name = 'longerthanthgwentycharacters'
    is_public = True

    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": invalid_name,
        "is_public": is_public
    })

    assert resp.status_code == 400

# Testing valid_channel_create 1
def test_valid_channel_create_1_char():
    user = setup()
    token = user['token']
    name = "1"
    is_public = True

    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200

# Testing valid channel_create 20
def test_valid_channel_create_20_chars():
    user = setup()
    token = user['token']
    name = 'qwertyuioplkjhgfdsaz'
    is_public = True
   
    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200

# Test normal valid channel create
def test_valid_channel_create():
    user = setup()
    token = user['token']
    name = "Cool Channel"
    is_public = True

    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200
    
