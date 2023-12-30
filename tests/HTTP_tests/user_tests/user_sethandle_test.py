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
    assert resp.status_code == 200

    return resp.json()

def user_profile(token, u_id):
    resp = requests.get(config.url + "user/profile/v1", params={
        'token': token,
        'u_id': u_id
    })
    assert resp.status_code == 200
    return resp.json()

def user_profile_sethandle(token, handle_str):
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={
        'token': token,
        'handle_str': handle_str
    })
    
    return resp

@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    token1 = user1['token']
    u_id1 = user1.get('auth_user_id')
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert").get('token')
    
    return [token1, user2, u_id1]


''' 
----------------------------------------------------
    Test HTTP Server to Sethandle to profile  
----------------------------------------------------
'''

# Invalid token
def test_invalid_token(setup):
    invalid_token = -1

    resp = user_profile_sethandle(invalid_token, "test")
    assert resp.status_code == 403

def test_invalid_strlen1(setup):
    resp = user_profile_sethandle(setup[0], "Vi")
    assert resp.status_code == 400
    
def test_invalid_strlen2(setup):

    resp = user_profile_sethandle(setup[0], "Rascaldoesnotdreamofbunnygirlsenpai")
    assert resp.status_code == 400

def test_handle_taken(setup):
    
    resp1 = user_profile_sethandle(setup[0], "test")
    assert resp1.status_code == 200
    
    resp2 = user_profile_sethandle(setup[1], "test")
    assert resp2.status_code == 400
    
def test_changing_to_same_handle(setup):
    
    resp1 = user_profile_sethandle(setup[0], "erenyeager")
    assert resp1.status_code == 200

    resp2 = user_profile_sethandle(setup[0], "erenyeager")
    assert resp2.status_code == 400

def test_alphanumeric(setup):
    resp = user_profile_sethandle(setup[0], "@ttack")
    assert resp.status_code == 400

def test_handle_success(setup):
    
    resp = user_profile_sethandle(setup[0], "AttackTitan")
    assert resp.status_code == 200
