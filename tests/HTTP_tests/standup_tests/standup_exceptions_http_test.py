import pytest
import requests
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

def channel_join(token, channel_id):
    resp = requests.post(config.url + "channel/join/v2", json={
        'token': token,
        'channel_id': channel_id
    })
    assert resp.status_code == 200
    return resp.json()

def standup_send(token, channel_id, message):
    return requests.post(config.url + "standup/send/v1", json={
        "token": token,
        'channel_id': channel_id,
        "message": message
    })

def standup_active(token, channel_id):
    return requests.get(config.url + "standup/active/v1", params={
        'token': token,
        'channel_id': channel_id
    })

def standup_start(token, channel_id, length):
    return requests.post(config.url + "standup/start/v1", json={
        'token': token,
        'channel_id': channel_id,
        'length': length
    })

'''
--------------------------------------------------------
    Setting up for Standup Tests
--------------------------------------------------------
'''
@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    channel_id1 = create_channel(user1['token'], 'The Sea', True).get('channel_id')

    users = {
        'u_1': user1,
        'channel': int(channel_id1)
    }
    return users

'''
--------------------------------------------------------
    Exceptions for Standup
--------------------------------------------------------
'''

def test_invalid_token(setup):

    not_token = -1
    channel_id = setup['channel']

    resp_start = standup_start(not_token, channel_id, 1)
    assert resp_start.status_code == 403

    resp_active = standup_active(not_token, channel_id)
    assert resp_active.status_code == 403    

    standup_start(setup['u_1']['token'], channel_id, 1)
    resp_send = standup_send(not_token, channel_id, "hello")
    assert resp_send.status_code == 403


def test_invalid_standup_length(setup):
    channel_id = setup['channel']
    resp = standup_start(setup['u_1']['token'], channel_id, -1)
    assert resp.status_code == 400

def test_invalid_message_length(setup):

    channel_id = setup['channel']

    standup_start(setup['u_1']['token'], channel_id, 1)
    long_msg = "Kt3SBFjCGnLc4HfF0u3ho4CJc0bFn7f3znWdwkgtvftpy5Csz55pKoQdbobqx2Az1GOu4Ox5gD7niYc6rxdWeGcWOXNYxMFA5TYSC2b6LCfkbhg7qAqWdTVBJhTGYBrQFrIu9LICiCTwoofsFHPyqlxl0Aw5LaM9A0wKtbmsNwcU3X3MTWQ8LjiR9gfbzNnswA5U2A1y9rkTciAFNuyV3I6cvktVKytZ5MdFN1AjFmuInCIWRHv4vkoaFVOuSjM0C8XYllO3p5JnYLHj9jSXBdoeL6o7i6gDl9Ew4KbIS60THlLtLZhmRZxKCQaLcdquY7LmDWezjIIXFybPzouSZCBnYtimFZAJgjkaFk6B2tf3pcntZuMyz1EJhxgPhYMGEEvpphQKDsQHQkVEm2fBDBhdMRqkLqMzXvneEsB3ccB64UIykggb18Ic2mvwSFXn5QIVAYieSnF1RS6pQwhUWrdbi8WDYexAicwQd1cot0BPb9MbtGQ8aqfNZq8SYG1ZuBgil6CL8EZzcmXAMd8EPGCobQCeLXZ9FQ1lve3FeE1K8vAdkC7GB8H7GNaZPKBgNXmuhdNyeW4Jvl86Z66KG2052CQ9SMr0yXniLhoXqkuNkXK1pU5m9cMO6mU0z6R5SmsLan0IXcDwpOd1Yh94jVqGW8tXb14RhIP7kClQyvVTgaWWeLVbMzt8uhssIxZrVeoFEsVdtnzDZEZ3hVQFA2Dr2INMJPXx8BE6NOoHug5TvImmu4rZCPqoeYqqRSqEmdr3SrzC6qrGuQlIQoPacECGqkxT32qN0QyeMcJY2Q2c5ddEn3y0Q93LvBhc8Ti6sIHl34vvWA8LAhIo4EVoRnCuIgO4FPmDVHsV2n9Wr2v6nagaGxozK6HjHEEixxheCO1KMjWN1jHNAMfZpw0uS4if5kqXQiAS52o7aoZevjJe4JJQzPI3S3vO1TurQ9WOOvu699gHgDfiCldap9lFKOU2uWx7ys7G10fRewFTT"
    resp = standup_send(setup['u_1']['token'], channel_id,long_msg)

    assert resp.status_code == 400

def test_invalid_channel(setup):
    token = setup['u_1']['token']
    not_channel = -1

    resp_start = standup_start(token, not_channel, 1)
    assert resp_start.status_code == 400

    resp_active = standup_active(token, not_channel)
    assert resp_active.status_code == 400

    channel_id = setup['channel']
    standup_start(setup['u_1']['token'], channel_id, 1)
    resp_send = standup_send(token, not_channel, 'hello')
    assert resp_send.status_code == 400

def test_nonmember(setup):    
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    channel_id = setup['channel']

    resp_start = standup_start(user2['token'], channel_id, 1)
    assert resp_start.status_code == 403

    resp_active = standup_active(user2['token'], channel_id)
    assert resp_active.status_code == 403

    standup_start(setup['u_1']['token'], channel_id, 1)
    resp_send = standup_send(user2['token'], channel_id, 'hello')
    assert resp_send.status_code == 403

def test_send_to_inactive(setup):

    channel_id = setup['channel']

    resp_send = standup_send(setup['u_1']['token'], channel_id, 'hello')
    assert resp_send.status_code == 400

# def test_already_active(setup):
#     resp_start = standup_start(setup['u_1']['token'], setup['channel'], 15)
#     assert resp_start.status_code == 200
#     resp_start_2 = standup_start(setup['u_1']['token'], setup['channel'], 1)

#     assert resp_start_2.status_code == 400

    
