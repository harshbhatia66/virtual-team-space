from atexit import register
from dataclasses import dataclass
import pytest

from src.auth import auth_register_v2
from src.channel import channel_join_v2
from src.channels import channels_create_v2, channels_list_v2
from src.error import InputError, AccessError
from src.other import clear_v1

'''
----------------------------------------------------
    Test Functions for channel_join_v2()
----------------------------------------------------
'''

# The function takes in a auth_user_id and a channel_id
# No return, void function

# Input Error
# - channel_id does not refer to a valid channel
# - the authorised user is already a member of the channel

# Access Error
# - channel_id refers to a channel that is 'private
#   and the authoriased user is not already a channek member
#   and is NOT a global owner


# Initalise the user and channel
@pytest.fixture
def init():
    clear_v1()

    user = {
        'email': 'elvin@gmail.com',
        'pass': 'NowWatchMeWhip',
        'first': 'Elvin',
        'last': 'Manaois',
    }

    auth_user = auth_register_v2(user['email'], user['pass'], user['first'], user['last'])
    user.update({'auth_user': auth_user})

    channel = {
        'name': 'test_1',
        'is_public': True,
    }
    
    channel_val = channels_create_v2(user['auth_user']['token'], channel['name'], channel['is_public'])
    channel_id = channel_val.get('channel_id')
    channel.update({'channel_id': channel_id})

    return [user, channel]
    

# Test invalid token
def test_invalid_token(init):
    invalid_token = 'awd'
    with pytest.raises(AccessError):
        assert channel_join_v2(invalid_token, init[1]['channel_id'])

# Checks whether the channel_id does not refer to a valid channel
def test_invalid_channel_id(init):
    invalid_channel_id = 10
    with pytest.raises(InputError):
        assert channel_join_v2(init[0]['auth_user']['token'], invalid_channel_id)
    
# Check whether the auth user is already an owner member of the channel
def test_user_owner_member(init):
    with pytest.raises(InputError):
        assert channel_join_v2(init[0]['auth_user']['token'], init[1]['channel_id'])

def test_user_member(init):
    channel_id = init[1]['channel_id']
    new_user = auth_register_v2("yessir@yahoo.com", "thisiadnwwd", "Yes", "No")

    channel_join_v2(new_user['token'], channel_id)

    with pytest.raises(InputError):
        assert channel_join_v2(new_user['token'], channel_id)

# Checks the channel if its private if so will trigger an Acces Error
def test_private_access(init):
    # Creates new user that isn't in the channel
    auth_id = auth_register_v2("yes@gmail.com", "thisisapass123", "Yes", "No")
    new_token = auth_id.get('token')

    # New User 2
    user2 = auth_register_v2("akjwdn@gmail.com", "alwdnaw", "akjwdn", "oawkndawd")
    user2_token = user2.get('token')

    # Creates new channel and changes the status of the channel to private
    channel_name = "test_2"
    is_public = False
    new_channel_id = channels_create_v2(new_token, channel_name, is_public).get('channel_id')

    with pytest.raises(AccessError):
        assert channel_join_v2(user2_token, new_channel_id)


def test_valid_join(init):
    # Get the public channel_id new user will join too
    channel_id = init[1]['channel_id']

    # Creates new user that isn't in the channel
    auth_user = auth_register_v2("yes@gmail.com", "thisisapass123", "Yes", "No")
    
    # Attempt to join the new user to a public channel
    channel_join_v2(auth_user['token'], channel_id)

    channels = channels_list_v2(auth_user['token']).get('channels')
    
    is_member = False

    for channel in channels:
        if channel_id == channel['channel_id']:
            is_member = True

    assert is_member == True