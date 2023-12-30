import pytest

from src.auth import auth_register_v2
from src.channel import channel_leave_v1
from src.channels import channels_create_v2, channels_list_v2
from src.error import InputError, AccessError
from src.other import clear_v1

# TODO: Add to main file
'''
--------------------------------------------------------
    Test for Channel Leave
--------------------------------------------------------
'''

@pytest.fixture
def init():
    clear_v1()
    reg = auth_register_v2("elvin@gmail.com", "thisisapassword", "Elvin", "Manaois")
    
    chan = channels_create_v2(reg['token'], "Test01", True)

    return [reg, chan]

def test_invalid_token(init):
    chan_id = init[1]['channel_id']
    invalid_token = -1
    with pytest.raises(AccessError):
        assert channel_leave_v1(invalid_token, chan_id)

def test_invalid_channel_id(init):
    token = init[0]['token']
    invalid_channel_id = -1
    with pytest.raises(InputError):
        assert channel_leave_v1(token, invalid_channel_id)

def test_user_not_member(init):
    chan_id = init[1]['channel_id']
    new_user = auth_register_v2("new@gmail.com", "thisisapasswd", "New", "User")

    with pytest.raises(AccessError):
        assert channel_leave_v1(new_user['token'], chan_id)

# 
def test_valid_leave(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    
    channel_leave_v1(token, chan_id)

    channels = channels_list_v2(init[0]['token']).get('channels')
    
    is_member = True

    for channel in channels:
        if chan_id == channel['channel_id']:
            is_member = False

    assert is_member == True
    

