import pytest

from src.auth import auth_register_v2
from src.message import message_sendlater_v1
from src.channels import channels_create_v2
from src.error import InputError, AccessError
from src.other import clear_v1
import time

'''
--------------------------------------------------------
    Test for Messages Send later on channels
--------------------------------------------------------
'''
@pytest.fixture
def init():
    clear_v1()
    reg = auth_register_v2("elvin@gmail.com", "pasksjefns", "Elvin", "Manaois")

    chan = channels_create_v2(reg['token'], "Test01", True)

    return [reg, chan]

def test_invalid_token(init):
    invalid_token = -1
    chan_id = init[1]['channel_id']
    message = "Yessirrr"
    time_sent = int(time.time())
    
    with pytest.raises(AccessError):
        assert message_sendlater_v1(invalid_token, chan_id, message, time_sent)

def test_invalid_channel_id(init):
    token = init[0]['token']
    invalid_chan_id = -1
    message = "Yessirr"
    time_sent = int(time.time())

    with pytest.raises(InputError):
        assert message_sendlater_v1(token, invalid_chan_id, message, time_sent)

def test_auth_user_non_member(init):
    token = auth_register_v2("skljdfhns@gmail.com", "aksdjhnaksjnd", "ajdn", "asdjansd").get('token')
    chan_id = init[1]['channel_id']
    message = "Test"
    time_sent = int(time.time())

    with pytest.raises(AccessError):
        assert message_sendlater_v1(token, chan_id, message, time_sent)

def test_message_under_1_character(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    message = ""
    time_sent = int(time.time())

    with pytest.raises(InputError):
        assert message_sendlater_v1(token, chan_id, message, time_sent)

def test_message_over_1000_characters(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    message = "a" * 1001
    time_sent = int(time.time())

    with pytest.raises(InputError):
        assert message_sendlater_v1(token, chan_id, message, time_sent)

def test_invalid_time_sent(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    message = "Hello World!"
    time_sent = int(time.time()) - 10 

    with pytest.raises(InputError):
        assert message_sendlater_v1(token, chan_id, message, time_sent)

def test_valid_message_send_later(init):
    token = init[0]['token']
    chan_id = init[1]['channel_id']
    message = "Hello World!"
    time_sent = int(time.time()) + 1

    assert message_sendlater_v1(token, chan_id, message, time_sent)
