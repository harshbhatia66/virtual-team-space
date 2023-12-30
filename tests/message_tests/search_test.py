import pytest

from src.auth import auth_register_v2
from src.message import message_send_dm_v1, search_v1, message_send_v1
from src.dm import dm_create_v1, dm_messages_v1
from src.channels import channels_create_v2
from src.channel import channel_join_v2, channel_messages_v2
from src.error import InputError, AccessError
from src.other import clear_v1

'''
--------------------------------------------------------
    Test for Searching Messages
--------------------------------------------------------
'''
@pytest.fixture
def setup():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = auth_register_v2("thisworldiscruel@gmail.com", "alsobeautiful!1!", "Mikasa", "Ackerman")

    channel_id1 = channels_create_v2(user1['token'], 'The Sea', True).get('channel_id')

    channel_join_v2(user2['token'], channel_id1)
    channel_join_v2(user3['token'], channel_id1)

    u_ids = [user2['auth_user_id']]
    dm1 = dm_create_v1(user1['token'], u_ids).get('dm_id')

    rumble1 = message_send_v1(user1['token'], channel_id1, "rumbling, word1, both").get('message_id')
    rumble2 = message_send_v1(user2['token'], channel_id1, "rumbling, word2, both").get('message_id')    

    rumble_dms = message_send_dm_v1(user2['token'], dm1, "rumbling, dm1").get('message_id')  

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
    result = output.get('messages')

    assert len(result) == 1
    assert result[0]['message_id'] == setup['search_ids'][0]

#TODO need to figure out what the correct behaviour should be
# def test_search_invalid(setup):
#     pass

def test_search_doesnotexist(setup):
    output = search_v1(setup['u_1']['token'],'four hundred and four')
    result = output.get('messages')
    
    assert len(result) == 0

def test_search_multipleusermessages(setup):
    output = search_v1(setup['u_1']['token'],'both')
    result = output.get('messages')


    assert len(result) == 2
    assert 'both' in result[0]['message']
    assert 'both' in result[1]['message']

def test_search_dms(setup):
    output = search_v1(setup['u_1']['token'],'dm1')
    result = output.get('messages')


    assert len(result) == 1
    assert result[0]['message_id'] == setup['search_dms']

def test_search_both(setup):
    output = search_v1(setup['u_1']['token'],'rumbling')
    result = output.get('messages')

    assert len(result) == 3
    assert 'rumbling' in result[0]['message']
    assert 'rumbling' in result[1]['message']
    assert 'rumbling' in result[2]['message']


