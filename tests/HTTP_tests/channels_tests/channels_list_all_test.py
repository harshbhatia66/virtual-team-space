from lib2to3.pgen2 import token
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

    user = response.json()

    return user

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

def create_channel(token, name, is_public):
    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200

    return resp

def channel_listall(token):
    return requests.get(config.url + "/channels/listall/v2", params={'token': token})

def test_invalid_token():
    user = setup()
    create_channel(user['token'], "Cool Beans", True)
    invalid_token = -1

    resp = channel_listall(invalid_token)
    assert resp.status_code == 403

def test_valid_list_all():
    user = setup()
    token = user['token']
    create_channel(user['token'], "test_channel1", True)
    create_channel(user['token'], "test_channel2", False)

    resp = channel_listall(token)
    assert resp.status_code == 200

    data = resp.json()

    expected_result = {

        'channels': [
            {
            'channel_id': 1,
            'name': 'test_channel1',
            },
             {
            'channel_id': 2,
            'name': 'test_channel2',
            },      
        ]
    }

    assert data == expected_result

def test_user_not_member():
    user = setup()
    create_channel(user['token'], "test_channel1", True)
    create_channel(user['token'], "test_channel2", False)

    new_user = create_user('ajwdbn@yahoo.com', 'awdnv1234', 'awdawb', 'awdhvnd')

    token = new_user['token']
    resp = channel_listall(token)
    assert resp.status_code == 200

    data = resp.json()

    expected_result = {

        'channels': [
            {
            'channel_id': 1,
            'name': 'test_channel1',
            },
             {
            'channel_id': 2,
            'name': 'test_channel2',
            },      
        ]
    }

    assert data == expected_result