import pytest

from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.dm import dm_create_v1
from src.message import message_send_dm_v1, message_send_v1
from src.user import users_stats_v1
from src.error import AccessError
from src.other import clear_v1

@pytest.fixture
def user1():
    clear_v1()

    user1 = auth_register_v2("elvin@gmail.com", "elvinmanaois11", "Elvin", "Manaois")

    return user1

def test_invalid_token():
    clear_v1()

    invalid_token = -1

    with pytest.raises(AccessError):
        assert users_stats_v1(invalid_token)

def test_zero_utilization_rate(user1):
    token = user1['token']

    assert users_stats_v1(token)

    stats = users_stats_v1(token)

    assert stats['workspace_stats']['utilization_rate'] == 0

def test_no_active_user(user1):
    token = user1['token']

    assert users_stats_v1(token)

def test_channel_member(user1):
    token = user1['token']

    channels_create_v2(token, "Test_1", True)

    assert users_stats_v1(token)

    stats = users_stats_v1(token)

    assert stats['workspace_stats']['channels_exist'][1]['num_channels_exist'] == 1

def test_dm_member(user1):
    token = user1['token']

    user2 = auth_register_v2("yessr@gmail.com", "thisisaver124234", "Yes", "Sir")
    u_ids = [user2['auth_user_id'], ]

    dm_create_v1(token, u_ids)

    assert users_stats_v1(token)

    stats = users_stats_v1(token)

    assert stats['workspace_stats']['dms_exist'][1]['num_dms_exist'] == 1

def test_channel_msg(user1):
    token = user1['token']

    chan_id = channels_create_v2(token, "Test_1", True).get('channel_id')

    message_send_v1(token, chan_id, "Test_1")

    assert users_stats_v1(token)

    stats = users_stats_v1(token)

    assert stats['workspace_stats']['messages_exist'][1]['num_messages_exist'] == 1

def test_dm_msg(user1):
    token = user1['token']

    user2 = auth_register_v2("yessr@gmail.com", "thisisaver124234", "Yes", "Sir")
    u_ids = [user2['auth_user_id'], ]

    dm_id = dm_create_v1(token, u_ids).get('dm_id')
    
    message_send_dm_v1(token, dm_id, "Test")

    assert users_stats_v1(token)

    stats = users_stats_v1(token)

    assert stats['workspace_stats']['messages_exist'][1]['num_messages_exist'] == 1