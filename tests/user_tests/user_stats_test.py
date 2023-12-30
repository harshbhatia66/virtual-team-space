import pytest

from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.dm import dm_create_v1
from src.message import message_send_dm_v1, message_send_v1
from src.user import user_stats_v1
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
        assert user_stats_v1(invalid_token)

def test_zero_involvement(user1):

    token = user1['token']

    assert user_stats_v1(token)

    stats = user_stats_v1(token)

    assert stats['user_stats']['involvement_rate'] == 0

def test_first_channel_created(user1):

    token = user1['token']

    channels_create_v2(token, "Test_1", True)

    stats = user_stats_v1(token)

    assert stats

    assert stats['user_stats']['channels_joined'][0]['num_channels_joined'] == 1

def test_first_dm_created(user1):
    token = user1['token']

    user2 = auth_register_v2("yessr@gmail.com", "thisisaver124234", "Yes", "Sir")
    u_ids = [user2['auth_user_id'], ]

    dm_create_v1(token, u_ids)

    stats = user_stats_v1(token)

    assert stats

    assert stats['user_stats']['dms_joined'][0]['num_dms_joined'] == 1

def test_channel_msg(user1):
    token = user1['token']

    chan_id = channels_create_v2(token, "Test_1", True).get('channel_id')

    message_send_v1(token, chan_id, "Test_1")

    stats = user_stats_v1(token)

    assert stats

    assert stats['user_stats']['messages_sent'][0]['num_messages_sent'] == 1

def test_dm_msg(user1):
    token = user1['token']

    user2 = auth_register_v2("yessr@gmail.com", "thisisaver124234", "Yes", "Sir")
    u_ids = [user2['auth_user_id'], ]

    dm_id = dm_create_v1(token, u_ids).get('dm_id')

    dm_id = message_send_dm_v1(token, dm_id, "Test 1")

    stats = user_stats_v1(token)

    assert stats

    assert len(stats['user_stats']['messages_sent']) == 1

    assert stats['user_stats']['messages_sent'][0]['num_messages_sent'] == 1