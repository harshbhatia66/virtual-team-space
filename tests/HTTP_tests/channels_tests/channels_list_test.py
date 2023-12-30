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

def channel_list(token):
    return requests.get(config.url + "channels/list/v2", params={'token': token})

def test_invalid_token():
    user = setup()
    create_channel(user['token'], "Cool beans", False)

    invalid_token = -1
    resp = channel_list(invalid_token)
    assert resp.status_code == 403

def test_channel_public():
    user = setup()
    chan_resp = create_channel(user['token'], "test_channel2", True)
    chan = chan_resp.json()

    token = user['token']
    resp = channel_list(token)
    assert resp.status_code == 200
    
    expected_result = {

        'channels': [
            {
            'channel_id': chan.get('channel_id'),
            'name': 'test_channel2',
            }

        ]
    }

    assert resp.json() == expected_result

def test_channel_private():
    user = setup()
    chan_resp = create_channel(user['token'], "Yessir", False)
    chan = chan_resp.json()

    token = user['token']
    resp = channel_list(token)
    assert resp.status_code == 200
    
    expected_result = {

        'channels': [
            {
            'channel_id': chan.get('channel_id'),
            'name': 'Yessir',
            }

        ]
    }

    assert resp.json() == expected_result

def test_user_not_member():
    user = setup()
    create_channel(user['token'], "test_channel1", True)
    create_channel(user['token'], "test_channel2", True)

    new_user = create_user('ajwdbn@yahoo.com', 'awdnv1234', 'awdawb', 'awdhvnd')

    token = new_user['token']
    resp = channel_list(token)
    assert resp.status_code == 200

    data = resp.json()

    expected_result = {
        'channels': []
    }

    assert data == expected_result
