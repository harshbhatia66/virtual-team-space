import pytest

from src.auth import auth_register_v2
from src.message import message_sendlaterdm_v1
from src.dm import dm_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1

import time

# TODO: Add to main file
'''
--------------------------------------------------------
    Test for Messages Send on dms
--------------------------------------------------------
'''
@pytest.fixture
def init():
    clear_v1()
    user1 = auth_register_v2("elvin@gmail.com", "thisisapassword", "Elvin", "Manaois")
    user2 = auth_register_v2("florenz@yahoo.com", "notapassword", "Florenz", "Fulo")

    u_ids = [user2['auth_user_id']]
    dm1 = dm_create_v1(user1['token'], u_ids)

    return [dm1, user1, user2]

def test_invalid_token(init):
    invalid_token = -1
    dm_id = init[0]['dm_id']
    msg = "Test"
    time_sent = int(time.time())

    with pytest.raises(AccessError):
        assert message_sendlaterdm_v1(invalid_token, dm_id, msg, time_sent)

def test_invalid_dm_id(init):
    token = init[1]['token']
    invalid_dm_id = -1
    msg = "Test"
    time_sent = int(time.time())

    with pytest.raises(InputError):
        assert message_sendlaterdm_v1(token, invalid_dm_id, msg, time_sent)

def test_auth_user_non_member(init):
    token = auth_register_v2("skdjnfa@gmail.com", "sadkjfnasf", "asjdna", "awjdnawd")['token']
    dm_id = init[0]['dm_id']
    msg = "Test"
    time_sent = int(time.time())

    with pytest.raises(AccessError):
        assert message_sendlaterdm_v1(token, dm_id, msg, time_sent)

def test_message_under_1_character(init):
    token = init[1]['token']
    dm_id = init[0]['dm_id']
    msg = ""
    time_sent = int(time.time())

    with pytest.raises(InputError):
        assert message_sendlaterdm_v1(token, dm_id, msg, time_sent)

def test_message_over_1000_character(init):
    token = init[1]['token']
    dm_id = init[0]['dm_id']
    msg = "a" * 1001
    time_sent = int(time.time())

    with pytest.raises(InputError):
        assert message_sendlaterdm_v1(token, dm_id, msg, time_sent)

def test_invalid_time_sent(init):
    token = init[1]['token']
    dm_id = init[0]['dm_id']
    msg = "Hello World!"
    time_sent = int(time.time()) - 10

    with pytest.raises(InputError):
        assert message_sendlaterdm_v1(token, dm_id, msg, time_sent)

def test_valid_message_send_later_dm(init):
    token = init[1]['token']
    dm_id = init[0]['dm_id']
    msg = "Hello World!"
    time_sent = int(time.time()) + 1

    assert message_sendlaterdm_v1(token, dm_id, msg, time_sent)
