import pytest
import requests
import json
from src import config
from tests.HTTP_tests.channel_tests.channel_invite_test import invalid_token

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

def channel_message(token, channel_id, start):
    return requests.get(config.url + "channel/messages/v2", params={
        'token': token,
        'channel_id': channel_id,
        'start': start
    })

@pytest.fixture
def messages_test():
    clear()

    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")

    chan_resp = create_channel(user1['token'], 'The Sea', True)
    channel_id = chan_resp['channel_id']
    return [user1['token'], user2['token'], int(channel_id)]

# Check if channel id exists
def test_invalid_channel_id(messages_test):
    invalid_channel_id = 10
    start = 0
    resp = channel_message(messages_test[0], invalid_channel_id, start)

    assert resp.status_code == 400

# Check for valid user id
def test_invalid_user_id(messages_test):
    user_id = 5
    start = 0

    resp = channel_message(user_id, messages_test[2], start)       

    assert resp.status_code == 403

# Check whether the auth user is a member of the channel
def test_channel_member(messages_test):
    start = 0
    resp = channel_message(messages_test[1], messages_test[2], start)

    assert resp.status_code == 403

# Check if the start variable is a positive integer 
def test_negative_start(messages_test):
    resp = channel_message(messages_test[0], messages_test[2], -1)

    assert resp.status_code == 400

# Check if the start index is greater than the total messages in channel
def test_max_start(messages_test):
    resp = channel_message(messages_test[0], messages_test[2], 60)

    assert resp.status_code == 400

# Check if end value is -1 when oldest message is reached
def test_negative_end(messages_test):
    resp = channel_message(messages_test[0], messages_test[2], 0)
    
    assert resp.status_code == 200

    data = resp.json()
    assert data['end'] == -1
    
# Check if function working through a simulated return
def test_working_function(messages_test):
    # Newly created channel so expected 0 channel messages

    channel_messages = {
        'messages': [],
        'start': 0,
        'end': -1,
    }

    res = channel_message(messages_test[0], messages_test[2], 0)
    data = res.json()
    
    assert data == channel_messages

# Checks for invalid token
def test_invalid_token(messages_test):
    invalid_token = -1

    resp = channel_message(invalid_token, messages_test[2], 0)

    assert resp.status_code == 403