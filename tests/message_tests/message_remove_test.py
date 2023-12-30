import re
import pytest

from src.auth import auth_register_v2
from src.message import message_send_v1, message_remove_v1, message_send_dm_v1
from src.channels import channels_create_v2
from src.channel import channel_join_v2, channel_messages_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.error import InputError, AccessError
from src.other import clear_v1

'''
--------------------------------------------------------
    Test for Messages Edit on channels
--------------------------------------------------------
'''

@pytest.fixture
def setup1():
    clear_v1()
    # Create users and a channel to populate some messages

    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger").get('token')
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert").get('token')
    user3 = auth_register_v2("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman").get('token')
    user4 = auth_register_v2("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger").get('token')

    channel_id1 = channels_create_v2(user1, 'The Sea', True).get('channel_id')

    channel_join_v2(user2, channel_id1)

    channel_join_v2(user3, channel_id1)

    msg = message_send_v1(user2, channel_id1, "Umi").get('message_id')

    return [msg, user1, user2, user3, user4, channel_id1]

@pytest.fixture
def setup2():
    clear_v1()
    # Create users and creates dm 

    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = auth_register_v2("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman")
    user4 = auth_register_v2("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger")

    dm_id = dm_create_v1(user1['token'], [user2['auth_user_id'], user3['auth_user_id']])['dm_id']

    msg = message_send_dm_v1(user2['token'], dm_id, "Umi").get('message_id')

    return [msg, user1, user2, user3, user4, dm_id]

# Check for:
# Input error when message_id does not refer to a valid message within a channel/DM that the authorised user has joined
# Invalid token
# Access error if the message id exists for the channel the user is part of, but user did not send message so they can't edit it
# Access error if the above is true and the user also does not have owner permissions in the channel
# Deletion if the message is an empty string



# If the message does not exist in any of the users channels/dms
def test_invalid_message_id1(setup1):
    with pytest.raises(InputError):
        assert message_remove_v1(setup1[4], setup1[0])
        
# If the message does not exist in any of the users dms
def test_invalid_message_id2(setup2):
    with pytest.raises(InputError):
        assert message_remove_v1(setup2[4]['token'], setup2[0])
        
def test_invalid_token(setup1):
    invalid_token = -1
    with pytest.raises(AccessError):
        assert message_remove_v1(invalid_token, setup1[0])

def test_unauthorised_edit1(setup1):
    with pytest.raises(AccessError):
        assert message_remove_v1(setup1[3], setup1[0])
        
def test_unauthorised_edit2(setup2):
    with pytest.raises(AccessError):
        assert message_remove_v1(setup2[3]['token'], setup2[0])

# Testing for a successful message remove if the user did not send the message but has owner permissions to edit
def test_permission1(setup1):
    # Authorised user with owner permission tries to remove message
    message_remove_v1(setup1[1], setup1[0])
    msgs = channel_messages_v2(setup1[1], setup1[5], 0).get('messages')
    assert len(msgs) == 0
    
# Testing for a successful message remove if the user did not send the message but has owner permissions to edit
def test_permission2(setup2):
    # Authorised user with owner permission tries to remove message
    message_remove_v1(setup2[1]['token'], setup2[0])
    msgs = dm_messages_v1(setup2[1]['token'], setup2[5], 0).get('messages')
    assert len(msgs) == 0

def test_successful_remove1(setup1):
    message_remove_v1(setup1[2], setup1[0])
    msgs = channel_messages_v2(setup1[1], setup1[5], 0).get('messages')
    assert len(msgs) == 0

def test_successful_remove2(setup2):
    message_remove_v1(setup2[2]['token'], setup2[0])
    msgs = dm_messages_v1(setup2[1]['token'], setup2[5], 0).get('messages')
    assert len(msgs) == 0

def test_global_owner_can_remove_members_message_channel(setup1):
    new_chan_id = channels_create_v2(setup1[2], "Test", True).get('channel_id')

    channel_join_v2(setup1[1], new_chan_id)

    msg_id = message_send_v1(setup1[2], new_chan_id, "Hello World").get('message_id')

    message_remove_v1(setup1[1], msg_id)