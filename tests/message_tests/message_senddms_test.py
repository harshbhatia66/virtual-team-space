import pytest

from src.auth import auth_register_v2
from src.message import message_send_dm_v1
from src.dm import dm_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1

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

    return [user1, user2, dm1]

def test_invalid_token(init):
    dm_id = init[2]['dm_id']
    invalid_token = -1
    with pytest.raises(AccessError):
        assert message_send_dm_v1(invalid_token, dm_id, "HelloWorld!")

def test_invalid_dm_id(init):
    invalid_dm_id = -1
    token = init[0]['token']
    msg = "HelloBob!"
    with pytest.raises(InputError):
        assert message_send_dm_v1(token, invalid_dm_id, msg)

def test_msg_under_1_char(init):
    token = init[0]['token']
    dm_id = init[2]['dm_id']
    invalid_msg = ""
    with pytest.raises(InputError):
        assert message_send_dm_v1(token, dm_id, invalid_msg)

def test_msg_under_1000_char(init):
    token = init[0]['token']
    dm_id = init[2]['dm_id']
    invalid_msg = "a" * 1001
    with pytest.raises(InputError):
        assert message_send_dm_v1(token, dm_id, invalid_msg)

def test_user_not_member(init):
    new_user = auth_register_v2('new@gmail.com','yesir2344', 'Yes', 'No')
    dm_id = init[2]['dm_id']
    msg = "Hello Its Me!"
    with pytest.raises(AccessError):
        assert message_send_dm_v1(new_user['token'], dm_id, msg)

def test_valid_message(init):
    token = init[0]['token']
    dm_id = init[2]['dm_id']
    msg = "Yessir This Is How We Do It"

    res = message_send_dm_v1(token, dm_id, msg)

    assert res['message_id'] == 1
