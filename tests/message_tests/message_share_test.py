import pytest
import string
import random
from src.auth import auth_register_v2
from src.message import message_send_dm_v1, message_share_v1, message_send_v1
from src.channels import channels_create_v2
from src.dm import dm_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def init():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert") 
    user3 = auth_register_v2("chelseaarezo@gmail.com", "Boomer10", "Chelsea", "Arezo")   
    u_ids = [user2['auth_user_id']]
    dm1 = dm_create_v1(user1['token'], u_ids)
    
    channel1 = channels_create_v2(user1['token'], "test_channel1", True)
    channel2 = channels_create_v2(user3['token'], "test_channel2", True)
    message_id = message_send_v1(user1['token'], channel1['channel_id'], "freedom")
    message_id2 = message_send_v1(user3['token'], channel2['channel_id'], "freedom2")
    return [user1, user2, dm1, channel1, user3, message_id, channel2, message_id2]

def test_message_share_to_channel(init):
    token = init[0]['token']
    og_message_id = init[5]['message_id']
    message = "hello" + "freedom"
    channel_id = init[3]['channel_id']
    dm_id = -1
    assert message_share_v1(token, og_message_id, message, channel_id, dm_id)

def test_message_share_to_dm(init):
    token = init[0]['token']
    og_message_id = init[5]['message_id']
    message = "hello" + "freedom"
    channel_id = -1
    dm_id = init[2]['dm_id']
    assert message_share_v1(token, og_message_id, message, channel_id, dm_id)
    
def test_invalid_dm_id(init):
    token = init[0]['token']
    og_message_id = init[5]['message_id']
    message = "hello" + "freedom"
    channel_id = init[3]['channel_id']
    dm_id = 0
    with pytest.raises(InputError):
        assert message_share_v1(token, og_message_id, message, channel_id, dm_id)

def test_invalid_channel_id(init):
    token = init[0]['token']
    og_message_id = init[5]['message_id']
    message = "hello" + "freedom"
    channel_id = 0
    dm_id = init[2]['dm_id']
    with pytest.raises(InputError):
        assert message_share_v1(token, og_message_id, message, channel_id, dm_id)

def test_both_invalid_ids(init):
    token = init[0]['token']
    og_message_id = init[5]['message_id']
    message = "hello" + "freedom"
    channel_id = init[3]['channel_id']
    dm_id = init[2]['dm_id']
    with pytest.raises(InputError):
        assert message_share_v1(token, og_message_id, message, channel_id, dm_id)

def test_both_negative_ids(init):
    token = init[0]['token']
    og_message_id = init[5]['message_id']
    message = "hello" + "freedom"
    channel_id = -1
    dm_id = -1
    with pytest.raises(InputError):
        assert message_share_v1(token, og_message_id, message, channel_id, dm_id)


def test_invalid_og_message_id(init):
    token = init[0]['token']
    og_message_id = -5
    message = "hello" + "freedom"
    channel_id = -1
    dm_id = init[2]['dm_id']
    with pytest.raises(InputError):
        assert message_share_v1(token, og_message_id, message, channel_id, dm_id)

def test_empty_message_share(init):
    token = init[0]['token']
    og_message_id = init[5]['message_id']
    message = ""
    new_message = "freedom" + message
    channel_id = -1
    dm_id = init[2]['dm_id']
    assert message_share_v1(token, og_message_id, new_message, channel_id, dm_id)

def test_message_over_1000(init):
    token = init[0]['token']
    og_message_id = init[5]['message_id']
    channel_id = -1
    dm_id = init[2]['dm_id']
    invalid_message = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(1005))
    with pytest.raises(InputError):
        assert message_share_v1(token, og_message_id, invalid_message, channel_id, dm_id)

def test_invalid_token(init):
    invalid_token = -1
    og_message_id = init[5]['message_id']
    message = "hello" + "freedom"
    channel_id = init[3]['channel_id']
    dm_id = -1
    with pytest.raises(AccessError):
        assert message_share_v1(invalid_token, og_message_id, message, channel_id, dm_id)
        
def test_unauthorised_user(init):
    unauthorised_user = init[4]['token']
    og_message_id = init[7]['message_id']
    message = "hello" + "freedom2"
    channel_id = -1
    dm_id = init[2]['dm_id']
    with pytest.raises(AccessError):
        assert message_share_v1(unauthorised_user, og_message_id, message, channel_id, dm_id)