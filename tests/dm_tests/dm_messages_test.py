import pytest

from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.error import AccessError, InputError
from src.other import clear_v1
from src.message import message_send_dm_v1

@pytest.fixture
def init():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = auth_register_v2("chelseaarezo@gmail.com", "comp1531", "Chelsea", "Arezo")
    
    u_ids = [user2['auth_user_id']]
    
    
    dm_id = dm_create_v1(user1['token'], u_ids).get('dm_id')
    
    return [user1, user3, u_ids, dm_id]

def test_valid_message(init):
    valid_token = init[0]['token']
    valid_dm_id = init[3]
    valid_start = 0
    first_dm = {
        'messages': [],
        'start': 0,
        'end': -1,
    }
    assert dm_messages_v1(valid_token, valid_dm_id, valid_start) == first_dm
    
def test_invalid_dm_id(init):
    valid_token = init[0]['token']
    invalid_dm_id = -1
    valid_start = 0
    with pytest.raises(InputError):
        assert dm_messages_v1(valid_token, invalid_dm_id, valid_start)

def test_negative_start(init):
    valid_token = init[0]['token']
    valid_dm_id = init[3]
    invalid_start = -1
    with pytest.raises(InputError):
        assert dm_messages_v1(valid_token, valid_dm_id, invalid_start)

def test_max_start(init):
    valid_token = init[0]['token']
    valid_dm_id = init[3]
    invalid_start = 60
    with pytest.raises(InputError):
      assert dm_messages_v1(valid_token, valid_dm_id, invalid_start)

def test_negative_end(init):
    valid_token = init[0]['token']
    valid_dm_id = init[3]
    valid_start = 0
    end = dm_messages_v1(valid_token, valid_dm_id, valid_start).get('end')
    assert end == -1

def test_invalid_user(init):
    invalid_token = -1
    valid_dm_id = init[3]
    valid_start = 0
    with pytest.raises(AccessError):
        assert dm_messages_v1(invalid_token, valid_dm_id, valid_start)

def test_invalid_authoriser(init):
    invalid_token = init[1]['token']
    valid_dm_id = init[3]
    valid_start = 0
    with pytest.raises(AccessError):
        assert dm_messages_v1(invalid_token, valid_dm_id, valid_start)

def test_under_fifty_messages_sent(init):
    msg_ids = [message_send_dm_v1(init[0]['token'], init[3], "Yessir")['message_id'] for x in range(10)]

    dm_msgs = dm_messages_v1(init[0]['token'], init[3], 0)

    assert dm_msgs['start'] == 0
    assert dm_msgs['end'] == -1
    assert msg_ids[::-1] == [m['message_id'] for m in dm_msgs['messages']]
    
def test_over_fifty_messages_sent(init):
    msg_ids = [message_send_dm_v1(init[0]['token'], init[3], "Yessir")['message_id'] for x in range(51)]
    msg_ids.reverse()
    
    dm_msgs = dm_messages_v1(init[0]['token'], init[3], 0)

    assert dm_msgs['start'] == 0
    assert dm_msgs['end'] == 50
    assert msg_ids[0:50] == [m['message_id'] for m in dm_msgs['messages']]

'''
    InputError when any of:

        dm_id does not refer to a valid DM
        start is greater than the total number of messages in the channel
      
      AccessError when:
      
        dm_id is valid and the authorised user is not a member of the DM
'''
