import re
import pytest

from src.auth import auth_register_v2
from src.message import message_send_v1
from src.channels import channels_create_v2
from src.error import InputError, AccessError
from src.other import clear_v1

# TODO: Add to main file
'''
--------------------------------------------------------
    Test for Messages Send on channels
--------------------------------------------------------
'''
@pytest.fixture
def setup():
    clear_v1()
    reg = auth_register_v2("elvin@gmail.com", "pasksjefns", "Elvin", "Manaois")

    chan = channels_create_v2(reg['token'], "Test01", True)

    return [reg, chan]

def test_invalid_token(setup):
    invalid_token = -1

    with pytest.raises(AccessError):
        assert message_send_v1(invalid_token, setup[1]['channel_id'], "Hello World!")

def test_invalid_channel_id(setup):
    invalid_channel_id = -1

    with pytest.raises(InputError):
        assert message_send_v1(setup[0]['token'], invalid_channel_id, "Helloworld")

def test_message_less_1_character(setup):
    msg = ""
    with pytest.raises(InputError):
        assert message_send_v1(setup[0]['token'], setup[1]['channel_id'], msg)

def test_message_over_1000_character(setup):
    msg = "a" * 1001
    with pytest.raises(InputError):
        assert message_send_v1(setup[0]['token'], setup[1]['channel_id'], msg)

def test_user_not_member(setup):
    new_user = auth_register_v2("yes@gmail.com", "pasword12123", "Yes", "No")
    with pytest.raises(AccessError):
        assert message_send_v1(new_user['token'], setup[1]['channel_id'], "Hello")

def test_valid_message(setup):
    token = setup[0]['token']
    chan_id = setup[1]['channel_id']
    msg = "Hello its me!"

    # Expected first result
    res = {
        "message_id": 1,
    }

    assert message_send_v1(token, chan_id, msg) == res
