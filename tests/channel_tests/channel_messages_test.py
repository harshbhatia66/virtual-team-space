import pytest

from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.error import InputError, AccessError
from src.other import clear_v1
from src.channel import channel_messages_v2
from src.message import message_send_v1


# Testing:
# Check if user is a member of the channel
# Check for valid channel id
# Check for valid user id
# Check that the start variable is an integer 
# Check that the start index is greater than the total messages in channel
# Simulate an example where function is executed correctly 
# Check if end value is -1 when oldest message is reached


@pytest.fixture
def messages_test():
    clear_v1()

    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")

    channel_id = channels_create_v2(user1['token'], 'The Sea', True).get('channel_id')

    return [user1['token'], user2['token'], channel_id]

# Check if channel id exists
def test_invalid_channel_id(messages_test):
    invalid_channel_id = 10
    start = 0
    with pytest.raises(InputError):
        assert channel_messages_v2(messages_test[0], invalid_channel_id, start)

# Check for valid user id
def test_invalid_user_id(messages_test):
    user_id = 5
    start = 0
    
    with pytest.raises(AccessError):
        assert channel_messages_v2(user_id, messages_test[2], start)        

# Check whether the auth user is a member of the channel
def test_channel_member(messages_test):
    start = 0
    with pytest.raises(AccessError):
        assert channel_messages_v2(messages_test[1], messages_test[2], start)

# Check if the start variable is a positive integer 
def test_negative_start(messages_test):
    with pytest.raises(InputError):
        assert channel_messages_v2(messages_test[0], messages_test[2], -1)

# Check if the start index is greater than the total messages in channel
def test_max_start(messages_test):
    with pytest.raises(InputError):
        assert channel_messages_v2(messages_test[0], messages_test[2], 60)

# Check if end value is -1 when oldest message is reached
def test_negative_end(messages_test):
    # Newly created channel so expected 0 channel messages, this means that we've indexed and no more mesages to return
    end = channel_messages_v2(messages_test[0], messages_test[2], 0).get('end')
    assert end == -1

# Check if function working through a simulated return
def test_working_function(messages_test):
    # Newly created channel so expected 0 channel messages

    channel_messages = {
        'messages': [],
        'start': 0,
        'end': -1,
    }

    assert channel_messages == channel_messages_v2(messages_test[0], messages_test[2], 0)

def test_under_fifty_messages_sent(messages_test):
    msg_ids = [message_send_v1(messages_test[0], messages_test[2], "Yessir")['message_id'] for x in range(10)]

    ch_msgs = channel_messages_v2(messages_test[0], messages_test[2], 0)

    assert ch_msgs['start'] == 0
    assert ch_msgs['end'] == -1
    assert msg_ids[::-1] == [m['message_id'] for m in ch_msgs['messages']]

def test_over_fifty_messages_sent(messages_test):
    msg_ids = [message_send_v1(messages_test[0], messages_test[2], "Yessir")['message_id'] for x in range(51)]
    msg_ids.reverse()

    ch_msgs = channel_messages_v2(messages_test[0], messages_test[2], 0)

    assert ch_msgs['start'] == 0
    assert ch_msgs['end'] == 50
    assert msg_ids[0:50] == [m['message_id'] for m in ch_msgs['messages']]