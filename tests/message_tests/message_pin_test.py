from pickle import TRUE
import re
import pytest

from src.auth import auth_register_v2
from src.message import message_send_v1, message_send_dm_v1, message_pin_v1
from src.channels import channels_create_v2
from src.channel import channel_join_v2, channel_messages_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.error import InputError, AccessError
from src.other import clear_v1

'''
--------------------------------------------------------
    Test for Messages Pin on channels
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

    msg = message_send_v1(user2, channel_id1, "RUMBLING").get('message_id')

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

    msg = message_send_dm_v1(user2['token'], dm_id, "RUMBLING").get('message_id')

    return [msg, user1.get('token'), user2.get('token'), user3.get('token'), user4.get('token'), dm_id]

# Check for:
# Input error when message_id does not refer to a valid message within a channel/DM 
# that the authorised user has joined
# Input error for Invalid token
# Input error when the message is already pinned
# Access error when message_id refers to a valid message in a joined channel/DM 
# and the authorised user does not have owner permissions in the channel/DM

# When message ID doesn't exist - Channel
def test_invalid_message_id(setup1):
    with pytest.raises(InputError):
        assert message_pin_v1(setup1[1], 1729)
        
# When user in not a part of the dm/channel where message id is in - Channel
def test_unauthorised_message_id1(setup1):
    with pytest.raises(InputError):
        assert message_pin_v1(setup1[4], setup1[0])
        
# When user in not a part of the dm/channel where message id is in - DM
def test_unauthorised_message_id2(setup2):
    with pytest.raises(InputError):
        assert message_pin_v1(setup2[4], setup2[0])
        
# When user does not exist/ Invalid Token
def test_invalid_token(setup1):
    invalid_token = -1
    with pytest.raises(AccessError):
        assert message_pin_v1(invalid_token, setup1[0])
        
# When the message was already pinned - channel
def test_already_pinned1(setup1):
    message_pin_v1(setup1[1], setup1[0])
    with pytest.raises(InputError):
        assert message_pin_v1(setup1[1], setup1[0])
        
# When the message was already pinned - dm
def test_already_pinned2(setup2):
    message_pin_v1(setup2[1], setup2[0])
    with pytest.raises(InputError):
        assert message_pin_v1(setup2[1], setup2[0])
        
# User does not have permissions - channel
def test_owner_permissions1(setup1):
    with pytest.raises(AccessError):
        assert message_pin_v1(setup1[2], setup1[0])
        
# User does not have permissions - dm
def test_owner_permissions2(setup2):
    with pytest.raises(AccessError):
        assert message_pin_v1(setup2[2], setup2[0])
        
# Test successful pin - Channel
def test_successful_pin1(setup1):
    message_pin_v1(setup1[1], setup1[0])
    msgs = channel_messages_v2(setup1[2], setup1[5], 0).get('messages')
    msg_pin_status = msgs[0].get('is_pinned')
    assert msg_pin_status == True
    
# Test successful pin - DM
def test_successful_pin2(setup2):
    message_pin_v1(setup2[1], setup2[0])
    msgs = dm_messages_v1(setup2[2], setup2[5], 0).get('messages')
    msg_pin_status = msgs[0].get('is_pinned')
    assert msg_pin_status == True
        

    
    