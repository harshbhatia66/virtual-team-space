import pytest
import requests
import json
from src import config
from src import admin as Admin

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

def create_channel(token, name, is_public):
    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200

    return resp.json()

def change_user_permission(token, u_id, permission_id):
    return requests.post(config.url + "admin/userpermission/change/v1", json={
        'token': token,
        'u_id': u_id,
        'permission_id': permission_id
    })

@pytest.fixture
def init():
    clear()
    user1 = create_user("elvin@gmail.com", "awkjdn2314", "Elvin", "Manaois")
    user2 = create_user("bobdabuilder@yahoo.com", "awdmabw21314", "Bob", "DaBuilder")

    return [user1, user2]

def test_invalid_token(init):
    invalid_token = -1
    u_id = init[1]["auth_user_id"]
    permission_id = Admin.OWNER

    resp = change_user_permission(invalid_token, u_id, permission_id)
    assert resp.status_code == 403

def test_invalid_u_id(init):
    token = init[0]['token']
    invalid_id = -1
    permission_id = Admin.OWNER

    resp = change_user_permission(token, invalid_id, permission_id)
    assert resp.status_code == 400

def test_u_id_only_global_owner(init):
    token = init[0]['token']
    only_u_id = init[0]['auth_user_id']
    permission_id = Admin.OWNER

    resp = change_user_permission(token, only_u_id, permission_id)
    assert resp.status_code == 400

def test_u_id_only_global_owner_demoted(init):
    token = init[0]['token']
    only_u_id = init[0]['auth_user_id']
    permission_id = Admin.MEMBER

    resp = change_user_permission(token, only_u_id, permission_id)
    assert resp.status_code == 400

def test_invalid_permission_id(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    invalid_id = -1

    resp = change_user_permission(token, u_id, invalid_id)
    assert resp.status_code == 400

def test_same_level_permission(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    perm_id = Admin.MEMBER

    resp = change_user_permission(token, u_id, perm_id)
    assert resp.status_code == 400

def test_auth_user_not_global_owner(init):
    new_user = create_user("awdjba@gmail.com", "awdjn232344", "awdjn", "awdjbb")
    token = init[1]['token']
    u_id = new_user['auth_user_id']
    perm_id = Admin.OWNER

    resp = change_user_permission(token, u_id, perm_id)
    assert resp.status_code == 403

def test_valid_permission_change(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    perm_id = Admin.OWNER

    resp = change_user_permission(token, u_id, perm_id)
    assert resp.status_code == 200
