import requests
import json
from src import config

def clear():
    response = requests.delete(config.url + 'clear/v1')
    
    assert response.status_code == 200

''' 
----------------------------------------------------
    Test HTTP Server for Registering the account  
----------------------------------------------------
'''

def test_valid_register():
    clear()
    response = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": "Elvin",
        "name_last": "Manaois"
    })

    assert response.status_code == 200

    response_data = response.json()

    assert response_data['auth_user_id'] == 1001

def test_different_register():
    clear()
    res1 = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": "Elvin",
        "name_last": "Manaois"
    })

    res2 = requests.post(config.url + "auth/register/v2", json={
        "email": "lkamf@gmail.com",
        "password": "tawdngbs",
        "name_first": "Cool",
        "name_last": "Math"
    })

    assert res1.status_code == 200
    assert res2.status_code == 200

    reg1 = res1.json()
    reg2 = res2.json()

    assert reg1 != reg2

# Invalid Email Test
def test_register_invalid_email():
    clear()

    invalid_email = "abc"
    res1 = requests.post(config.url + "auth/register/v2", json={
        "email": invalid_email,
        "password": "th1s1s@pass",
        "name_first": "Elvin",
        "name_last": "Manaois"
    })

    # Input Report
    assert res1.status_code == 400

# Test duplicate email
def test_duplicate_email():
    clear()

    same_email = "elvin@gmail.com"
    res1 = requests.post(config.url + "auth/register/v2", json={
        "email": same_email,
        "password": "th1s1s@pass",
        "name_first": "Elvin",
        "name_last": "Manaois"
    })

    assert res1.status_code == 200

    res2 = requests.post(config.url + "auth/register/v2", json={
        "email": same_email,
        "password": "tawdngawdbs",
        "name_first": "Cool",
        "name_last": "Math"
    })

    assert res2.status_code == 400
    
# Invalid Password
def test_invalid_pass():
    clear()

    invalid_pass = '123'
    res1 = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": invalid_pass,
        "name_first": "Elvin",
        "name_last": "Manaois"
    })

    assert res1.status_code == 400

# First name length 1 -  50 characters inclusive
def test_invalid_name_first():
    clear()
    invalid_name_50 = 'Advsvsldkvjsdsdfkjsndfksjdnfksjdnfksjdnfsdfasdfasdfasdwd'

    res = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": invalid_name_50,
        "name_last": "Manaois"
    })

    assert res.status_code == 400

    clear()
    invalid_name_1 = ""
    res = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": invalid_name_1,
        "name_last": "Manaois"
    })

    assert res.status_code == 400

# Last name length 1 - 50 characters inclusive
def test_invalid_name_last():
    clear()
    invalid_name_50 = 'Advsvsldkvjsdsdfkjsndfksjdnfksjdnfksjdnfsdfasdfasdfasdwd'

    res = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": "Elvin",
        "name_last": invalid_name_50
    })

    assert res.status_code == 400

    clear()
    invalid_name_1 = ""
    res = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": "Elvin",
        "name_last": invalid_name_1
    })

    assert res.status_code == 400

# Tests for valid handle_str with more than 20 characters
def test_handle_str_over_20_chars():
    clear()
    name_first = "awdknawlkdnawlkdnakwjndaw"
    name_last = "awkjldnawkjdnawkjdnawkjdn"

    res = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": name_first,
        "name_last": name_last
    })

    assert res.status_code == 200

# Tests for two different registered account with the same name
def test_handle_str_duplicate():
    clear()

    name_first = "Elvin"
    name_last = "Manaois"

    res1 = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": name_first,
        "name_last": name_last
    })

    assert res1.status_code == 200

    res2 = requests.post(config.url + "auth/register/v2", json={
        "email": "florenz@gmail.com",
        "password": "thdawdff1s1s@pass",
        "name_first": name_first,
        "name_last": name_last
    })

    assert res2.status_code == 200

# Tests for two different registered account with the same name over 20 characters
def test_handle_str_duplicate_over_20_chars():
    clear()
    name_first = "awdknawlkdnawlkdnakwjndaw"
    name_last = "awkjldnawkjdnawkjdnawkjdn"

    res1 = requests.post(config.url + "auth/register/v2", json={
        "email": "elvin@gmail.com",
        "password": "th1s1s@pass",
        "name_first": name_first,
        "name_last": name_last
    })

    assert res1.status_code == 200

    res2 = requests.post(config.url + "auth/register/v2", json={
        "email": "florenz@gmail.com",
        "password": "thdawdff1s1s@pass",
        "name_first": name_first,
        "name_last": name_last
    })

    assert res2.status_code == 200

# Empty register
def test_empty_register():
    clear()
    response = requests.post(config.url + "auth/register/v2", json={})

    assert response.status_code != 200
