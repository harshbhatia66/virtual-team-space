import re
import pytest

from src.auth import auth_register_v2
from src.message import message_send_v1, message_edit_v1, message_send_dm_v1
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
def setup():
    clear_v1()
    # Create users and a channel to populate some messages

    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger").get('token')
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert").get('token')
    user3 = auth_register_v2("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman").get('token')
    user4 = auth_register_v2("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger").get('token')

    channel_id1 = channels_create_v2(user1, 'The Sea', True).get('channel_id')

    channel_join_v2(user2, channel_id1)

    channel_join_v2(user3, channel_id1)

    msg = message_send_v1(user1, channel_id1, "RUMBLING").get('message_id')

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

    msg = message_send_dm_v1(user1['token'], dm_id, "RUMBLING").get('message_id')

    return [msg, user1, user2, user3, user4, dm_id]

# Check for:
# Input error when length of message is over 1000 characters
# Input error when message_id does not refer to a valid message within a channel/DM that the authorised user has joined
# Invalid token
# Access error if the message id exists for the channel the user is part of, but user did not send message so they can't edit it
# Access error if the above is true and the user also does not have owner permissions in the channel
# Deletion if the message is an empty string

def test_message_over_1000_character(setup):
    msg = "a" * 1001
    with pytest.raises(InputError):
        assert message_edit_v1(setup[1], setup[0], msg)

def test_invalid_message_id(setup):
    with pytest.raises(InputError):
        assert message_edit_v1(setup[4], setup[0], "Euthanasia")
        
# If the message does not exist in any of the users dms
def test_invalid_message_id2(setup2):
    with pytest.raises(InputError):
        assert message_edit_v1(setup2[4]['token'], setup2[0], "Euthanasia")
        
        
def test_invalid_token(setup):
    invalid_token = -1
    with pytest.raises(AccessError):
        assert message_edit_v1(invalid_token, setup[0], "test")

def test_unauthorised_edit(setup):
    with pytest.raises(AccessError):
        assert message_edit_v1(setup[2], setup[0], "test")
        
def test_unauthorised_edit2(setup2):
    with pytest.raises(AccessError):
        assert message_edit_v1(setup2[3]['token'], setup2[0], "test")

# Testing for a successful message edit if the user did not send the message but has owner permissions to edit
def test_permission(setup):

    # A channel member sends a message
    msg = message_send_v1(setup[3], setup[5], "test").get('message_id')

    # Channel owner tries to edit the message who has owner permsissions
    message_edit_v1(setup[1], msg, "Rumbling")
    msgs = channel_messages_v2(setup[1], setup[5], 0).get('messages')
    new_msg = msgs[0].get('message')

    # Checking if the message was edited successfully
    assert new_msg == "Rumbling"
    
# Testing for a successful message edit if the user did not send the message but has owner permissions to edit
def test_permission2(setup2):

    # A channel member sends a message
    msg = message_send_dm_v1(setup2[3]['token'], setup2[5], "test").get('message_id')

    # Channel owner tries to edit the message who has owner permsissions
    message_edit_v1(setup2[1]['token'], msg, "Rumbling")
    msgs = dm_messages_v1(setup2[1]['token'], setup2[5], 0).get('messages')
    new_msg = msgs[0].get('message')

    # Checking if the message was edited successfully
    assert new_msg == "Rumbling"


def test_successful_edit(setup):
    message_edit_v1(setup[1], setup[0], "Freedom")
    msgs = channel_messages_v2(setup[1], setup[5], 0).get('messages')
    new_msg = msgs[0].get('message')
    assert new_msg == "Freedom"
    
def test_successful_edit2(setup2):
    message_edit_v1(setup2[1]['token'], setup2[0], "Freedom")
    msgs = dm_messages_v1(setup2[1]['token'], setup2[5], 0).get('messages')
    new_msg = msgs[0].get('message')
    assert new_msg == "Freedom"

def test_empty_string(setup):
    message_edit_v1(setup[1], setup[0], "")
    msgs = channel_messages_v2(setup[1], setup[5], 0).get('messages')
    assert len(msgs) == 0

def test_empty_string2(setup2):
    message_edit_v1(setup2[1]['token'], setup2[0], "")
    msgs = dm_messages_v1(setup2[1]['token'], setup2[5], 0).get('messages')
    assert len(msgs) == 0

def test_global_owner_can_edit_members_message_channel(setup):
    new_chan_id = channels_create_v2(setup[2], "Test", True).get('channel_id')

    channel_join_v2(setup[1], new_chan_id)

    msg_id = message_send_v1(setup[2], new_chan_id, "Hello World").get('message_id')

    message_edit_v1(setup[1], msg_id, 'Nice One')
