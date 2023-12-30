import pytest
import src.admin as Admin
from src.admin import user_remove_v1, user_permission_change_v1
from src.auth import auth_register_v2, auth_logout_v1
from src.channel import channel_invite_v2, channel_messages_v2
from src.channels import channels_create_v2
from src.message import message_send_v1, message_send_dm_v1
from src.dm import dm_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1

# TODO:

@pytest.fixture
def init():
    clear_v1()

    user1 = auth_register_v2("elvin@gmail.com", "awdahwd1234", "Elvin", "Manaois")
    user2 = auth_register_v2("akwjdna@yahoo.com", "awdjn1234", "Chels", "Yes")

    return [user1, user2]

def test_invalid_token(init):
    invalid_token = -1
    u_id = init[1]['auth_user_id']

    with pytest.raises(AccessError):
        assert user_remove_v1(invalid_token, u_id)

def test_invalid_u_id(init):
    token = init[0]['token']
    invalid_id = -1

    with pytest.raises(InputError):
        assert user_remove_v1(token, invalid_id)
    
# Tests for a user that is the only global member
# Input Error
def test_u_id_only_global_member(init):
    token = init[0]['token']
    only_u_id = init[0]['auth_user_id']
    
    with pytest.raises(InputError):
        assert user_remove_v1(token, only_u_id)
        
# Tests for an auth user that is not a global member
# Access Error
def test_auth_user_not_global_member(init):
    new_user = auth_register_v2("awdjba@gmail.com", "awdjn232344", "awdjn", "awdjbb")
    token = init[1]['token']
    u_id = new_user['auth_user_id']

    with pytest.raises(AccessError):
        assert user_remove_v1(token, u_id)

# Tests for valid user_remove_v1()
def test_valid_user_remove_v1(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    user_remove_v1(token, u_id)

def test_reusable_email(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    user_remove_v1(token, u_id)
    assert  auth_register_v2('akwjdna@yahoo.com', "awkjdhawkd", "kajwndakwjnd", "awdnawkjnd")

def test_reusable_handle_str(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    user_remove_v1(token, u_id)
    assert auth_register_v2("akwjdna@yahoo.com", "awdjn1234", "Chels", "Yes")

def test_u_id_in_channel(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    chan = channels_create_v2(token, "Test_Channel_1", True)
    chan_id = chan['channel_id']

    channel_invite_v2(token, chan_id, u_id)

    user_remove_v1(token, u_id)

def test_u_id_chan_message(init):
    
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    chan = channels_create_v2(token, "Test_Channel_1", True)
    chan_id = chan['channel_id']

    channel_invite_v2(token, chan_id, u_id)

    u_id_token = init[1]['token']
    message_send_v1(u_id_token, chan_id, "Hello World")

    user_remove_v1(token, u_id)

def test_u_id_chan_no_msg(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    chan = channels_create_v2(token, "Test_Channel_1", True)
    chan_id = chan['channel_id']

    channel_invite_v2(token, chan_id, u_id)

    message_send_v1(token, chan_id, "Hello World")

    user_remove_v1(token, u_id)

def test_u_id_not_member(init):
    new_user = auth_register_v2("awdj@gmail.com", "awkjdna124", "wadjn", "awdfg")

    token = init[0]['token']

    channels_create_v2(token, "Test_Channel_1", True)

    user_remove_v1(token, new_user['auth_user_id'])

def test_more_than_one_global_owner(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    user_permission_change_v1(token, u_id, Admin.OWNER)

    user_remove_v1(token, u_id)

def test_dm_create(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    dm_create_v1(token, [u_id])

    user_remove_v1(token, u_id)

def test_dm_message(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    
    dm_id = dm_create_v1(token, [u_id]).get('dm_id')

    u_id_token = init[1]['token']
    message_send_dm_v1(u_id_token, dm_id, "Hello")

    user_remove_v1(token, u_id)
    
def test_dm_no_message(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    
    dm_id = dm_create_v1(token, [u_id]).get('dm_id')

    message_send_dm_v1(token, dm_id, "Hello")

    user_remove_v1(token, u_id)

def test_no_dms(init):
    new_user = auth_register_v2("awdj@gmail.com", "awkjdna124", "wadjn", "awdfg")

    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    dm_create_v1(token, [u_id]).get('dm_id')

    user_remove_v1(token, new_user['auth_user_id'])

def test_once_removed_user_cant_do_anything(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    user_remove_v1(token, u_id)

    with pytest.raises(AccessError):
        auth_logout_v1(init[1]['token'])

def test_user_channel_content(init):
    
    token = init[0]['token']
    u_id = init[1]['auth_user_id']

    chan = channels_create_v2(token, "Test_Channel_1", True)
    chan_id = chan['channel_id']

    channel_invite_v2(token, chan_id, u_id)

    u_id_token = init[1]['token']
    message_send_v1(u_id_token, chan_id, "Hello World")

    user_remove_v1(token, u_id)

    msgs = channel_messages_v2(token, chan_id, 0).get('messages')[0]

    assert msgs['message'] == 'Removed user'

def test_cannot_remove_user_nonowner(init):
    with pytest.raises(AccessError):
        user_remove_v1(init[1]['token'], init[0]['auth_user_id'])
