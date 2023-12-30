from unicodedata import ucd_3_2_0
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

def get_user(email, password):
    response = requests.post(config.url + "auth/login/v2", json={
        "email": email,
        "password": password
    })

    assert response.status_code == 200

    user = response.json()

    return user

def dm_create(token, u_ids):
    resp = requests.post(config.url + "dm/create/v1", json={
        'token': token,
        'u_ids': u_ids
    })
    assert resp.status_code == 200
    return resp.json()



def message_senddm(token, dm_id, message):
    resp = requests.post(config.url + "message/senddm/v1", json={
        'token': token,
        'dm_id': dm_id,
        'message': message
    })
    assert resp.status_code == 200

    return resp.json()

def create_channel(token, name, is_public):
    resp = requests.post(config.url + "channels/create/v2", json={
        "token": token,
        "name": name,
        "is_public": is_public
    })

    assert resp.status_code == 200

    return resp.json()

def message_send(token, channel_id, message):
    resp = requests.post(config.url + "message/send/v1", json={
        'token': token,
        'channel_id': channel_id,
        'message': message
    })

    assert resp.status_code == 200

    message_id = resp.json()

    return message_id

def channel_join(token, channel_id):
    resp = requests.post(config.url + "channel/join/v2", json={
        'token': token,
        'channel_id': channel_id
    })
    assert resp.status_code == 200
    return resp.json()


def search_v1(token, query_str):
    return requests.get(config.url + "/search/v1", params={
        'token': token,
        'query_str': query_str
    })


'''
--------------------------------------------------------
    Test for Searching Messages
--------------------------------------------------------
'''
@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = create_user("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = create_user("thisworldiscruel@gmail.com", "alsobeautiful!1!", "Mikasa", "Ackerman")

    channel_id1 = create_channel(user1['token'], 'The Sea', True).get('channel_id')

    channel_join(user2['token'], channel_id1)
    channel_join(user3['token'], channel_id1)

    u_ids = [user2['auth_user_id']]
    dm1 = dm_create(user1['token'], u_ids).get('dm_id')

    rumble1 = message_send(user1['token'], channel_id1, "rumbling, word1, both").get('message_id')
    rumble2 = message_send(user2['token'], channel_id1, "rumbling, word2, both").get('message_id')    

    rumble_dms = message_senddm(user2['token'], dm1, "rumbling, dm1").get('message_id')  

    users = {
        'u_1': user1,
        'u_2': user2,
        'u_3': user3,
        'search_ids': [rumble1,rumble2],
        'search_dms': rumble_dms,
    }
    return users

'''
--------------------------------------------------------
    Test for Messages Search
--------------------------------------------------------
'''
def test_search_success(setup):

    output = search_v1(setup['u_1']['token'],'word1')
    assert output.status_code == 200

    data = output.json()
    result = data.get('messages')
    assert len(result) == 1
    assert result[0]['message_id'] == setup['search_ids'][0]

def test_search_doesnotexist(setup):
    output = search_v1(setup['u_1']['token'],'four hundred and four')
    assert output.status_code == 200

    data = output.json()
    result = data.get('messages')    
    assert len(result) == 0

def test_search_multipleusermessages(setup):
    output = search_v1(setup['u_1']['token'],'both')
    assert output.status_code == 200

    data = output.json()
    result = data.get('messages')

    assert len(result) == 2
    assert 'both' in result[0]['message']
    assert 'both' in result[1]['message']

def test_search_dms(setup):
    output = search_v1(setup['u_1']['token'],'dm1')
    assert output.status_code == 200

    data = output.json()
    result = data.get('messages')

    assert len(result) == 1
    assert result[0]['message_id'] == setup['search_dms']

def test_search_both(setup):
    output = search_v1(setup['u_1']['token'],'rumbling')
    assert output.status_code == 200

    data = output.json()
    result = data.get('messages')


    assert len(result) == 3
    assert 'rumbling' in result[0]['message']
    assert 'rumbling' in result[1]['message']
    assert 'rumbling' in result[2]['message']

def test_query_too_short(setup):
    resp = search_v1(setup['u_1']['token'],'')
    assert resp.status_code == 400

    
def test_query_too_long(setup):
    long_query = "Kt3SBFjCGnLc4HfF0u3ho4CJc0bFn7f3znWdwkgtvftpy5Csz55pKoQdbobqx2Az1GOu4Ox5gD7niYc6rxdWeGcWOXNYxMFA5TYSC2b6LCfkbhg7qAqWdTVBJhTGYBrQFrIu9LICiCTwoofsFHPyqlxl0Aw5LaM9A0wKtbmsNwcU3X3MTWQ8LjiR9gfbzNnswA5U2A1y9rkTciAFNuyV3I6cvktVKytZ5MdFN1AjFmuInCIWRHv4vkoaFVOuSjM0C8XYllO3p5JnYLHj9jSXBdoeL6o7i6gDl9Ew4KbIS60THlLtLZhmRZxKCQaLcdquY7LmDWezjIIXFybPzouSZCBnYtimFZAJgjkaFk6B2tf3pcntZuMyz1EJhxgPhYMGEEvpphQKDsQHQkVEm2fBDBhdMRqkLqMzXvneEsB3ccB64UIykggb18Ic2mvwSFXn5QIVAYieSnF1RS6pQwhUWrdbi8WDYexAicwQd1cot0BPb9MbtGQ8aqfNZq8SYG1ZuBgil6CL8EZzcmXAMd8EPGCobQCeLXZ9FQ1lve3FeE1K8vAdkC7GB8H7GNaZPKBgNXmuhdNyeW4Jvl86Z66KG2052CQ9SMr0yXniLhoXqkuNkXK1pU5m9cMO6mU0z6R5SmsLan0IXcDwpOd1Yh94jVqGW8tXb14RhIP7kClQyvVTgaWWeLVbMzt8uhssIxZrVeoFEsVdtnzDZEZ3hVQFA2Dr2INMJPXx8BE6NOoHug5TvImmu4rZCPqoeYqqRSqEmdr3SrzC6qrGuQlIQoPacECGqkxT32qN0QyeMcJY2Q2c5ddEn3y0Q93LvBhc8Ti6sIHl34vvWA8LAhIo4EVoRnCuIgO4FPmDVHsV2n9Wr2v6nagaGxozK6HjHEEixxheCO1KMjWN1jHNAMfZpw0uS4if5kqXQiAS52o7aoZevjJe4JJQzPI3S3vO1TurQ9WOOvu699gHgDfiCldap9lFKOU2uWx7ys7G10fRewFTT"
    resp = search_v1(setup['u_1']['token'],long_query)
    assert resp.status_code == 400

def test_user_not_in_channel(setup):
    new_channel = create_channel(setup['u_1']['token'], 'The Future', True).get('channel_id')
    message_send(setup['u_1']['token'], new_channel, "unique")

    resp = search_v1(setup['u_2']['token'], 'unique')

    assert resp.status_code == 200
    data = resp.json()
    result = data.get('messages')
    assert len(result) == 0

