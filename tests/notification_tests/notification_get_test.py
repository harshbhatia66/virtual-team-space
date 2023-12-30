import pytest
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_join_v2, channel_invite_v2
from src.dm import dm_create_v1
from src.message import message_send_v1, message_send_dm_v1, message_react_v1
from src.notification import notifications_get_v1
from src.error import AccessError
from src.other import clear_v1

@pytest.fixture
def channel_test():
    clear_v1()
    user1 = auth_register_v2("elvin@gmail.com", "elvinmanaois11", "Elvin", "Manaois")
    user2 = auth_register_v2("homer@gmail.com", "homersimpson11", "Homer", "Simpson")

    chan_id = channels_create_v2(user1['token'], "Test_1", True).get('channel_id')

    channel_join_v2(user2['token'], chan_id)

    return [chan_id, user1, user2]

@pytest.fixture
def dm_test():
    clear_v1()
    user1 = auth_register_v2("elvin@gmail.com", "elvinmanaois11", "Elvin", "Manaois")
    user2 = auth_register_v2("homer@gmail.com", "homersimpson11", "Homer", "Simpson")

    u_ids = [user2['auth_user_id'], ]

    dm_id = dm_create_v1(user1['token'], u_ids).get('dm_id')

    return [dm_id, user1, user2]

def test_invalid_token(channel_test):
    invalid_token = -1
    with pytest.raises(AccessError):
        assert notifications_get_v1(invalid_token)

def test_tagged_channel_message(channel_test):
    token = channel_test[1]['token']
    chan_id = channel_test[0]
    msg = "@homersimpson Hello World!"
    message_send_v1(token, chan_id, msg)
    
    user_2_token = channel_test[2]['token']
    notification = notifications_get_v1(user_2_token)

    assert notification

    user_handle = "elvinmanaois"
    chan_name = "Test_1"
    notification_msg = f"{user_handle} tagged you in {chan_name}: {msg[:20]}"
    assert notification['notifications'][0] == {
        'channel_id': chan_id,
        'dm_id': -1,
        'notification_message': notification_msg,
    }

def test_tagged_dm_message(dm_test):
    token = dm_test[1]['token']
    dm_id = dm_test[0]
    msg = "@elvinmanaois Hello "

    user_2_token = dm_test[2]['token']
    message_send_dm_v1(user_2_token, dm_id, msg)
    
    notification = notifications_get_v1(token)

    assert notification

    user_handle = "homersimpson"
    dm_name = "elvinmanaois, homersimpson"
    notification_msg = f"{user_handle} tagged you in {dm_name}: {msg[:20]}"
    assert notification['notifications'][0] == {
        'channel_id': -1,
        'dm_id': dm_id,
        'notification_message': notification_msg,
    }

def test_reacted_channel_message(channel_test):
    token = channel_test[1]['token']
    channel_id = channel_test[0]
    msg = "Hello World!"
    msg_id = message_send_v1(token, channel_id, msg).get('message_id')
    react_id = 1

    user_2_token = channel_test[2]['token']
    message_react_v1(user_2_token, msg_id, react_id)
    
    notification = notifications_get_v1(token)

    assert notification

    user_handle = "homersimpson"
    chan_name = "Test_1"
    notification_msg = f"{user_handle} reacted to your message in {chan_name}"
    assert notification['notifications'][0] == {
        'channel_id': channel_id,
        'dm_id': -1,
        'notification_message': notification_msg,
    }

def test_reacted_dm_message(dm_test):
    token = dm_test[1]['token']
    dm_id = dm_test[0]
    msg = "Hello World!"
    msg_id = message_send_dm_v1(token, dm_id, msg).get('message_id')
    react_id = 1

    user_2_token = dm_test[2]['token']
    message_react_v1(user_2_token, msg_id, react_id)

    notification = notifications_get_v1(token)

    assert notification

    user_handle = "homersimpson"
    dm_name = "elvinmanaois, homersimpson"
    notification_msg = f"{user_handle} reacted to your message in {dm_name}"
    assert notification['notifications'][0] == {
        'channel_id': -1,
        'dm_id': dm_id,
        'notification_message': notification_msg,
    }

def test_channel_join(channel_test):
    token = channel_test[1]['token']
    chan_id = channel_test[0]
    new_user = auth_register_v2("florenz@gmail.com", "akwjdnwa123", "florenz", "fulo")

    channel_invite_v2(token, chan_id, new_user['auth_user_id'])
    new_token = new_user['token']

    notification = notifications_get_v1(new_token)
    assert notification
    
    user_handle = "elvinmanaois"
    chan_name = "Test_1"
    
    notification_msg = f"{user_handle} added you to {chan_name}"
    assert notification['notifications'][0] == {
        'channel_id': chan_id,
        'dm_id': -1,
        'notification_message': notification_msg,
    }