import pytest

from src.auth import auth_register_v2
from src.channels import channels_create_v2, channels_list_v2
from src.channel import channel_invite_v2
from src.error import InputError, AccessError
from src.other import clear_v1


@pytest.fixture
def init():
    clear_v1()

    # Creating User and initialising Channel attributes
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = auth_register_v2("jasonderulo@gmail.com", "t3hee1023", "Jason", "Derulo")
    
    is_public = True
    not_public = False

    # Make some channels for testing
    chan_1 = channels_create_v2(user1['token'], "test_channel1", is_public)
    chan_2 = channels_create_v2(user2['token'], "test_channel2", not_public)
    chan_3 = channels_create_v2(user3['token'], "test_channel3", is_public)

    users = {
        'u_1': user1,
        'u_2': user2,
        'u_3': user3,
    }

    chan_ids = { 
        'chan_1': chan_1.get('channel_id'), 
        'chan_2': chan_2.get('channel_id'), 
        'chan_3': chan_3.get('channel_id'),
    }
    
    return [users, chan_ids]

# Test for a valid channel_invite function
def test_channel_valid(init):
    users = init[0]
    user_2 = users['u_2']['auth_user_id']
    user_1 = users['u_1']['token']
    channel_id = init[1]['chan_1']
    
    # User 1 invites user 2 to channel 1
    channel_invite_v2(user_1, channel_id, user_2)

    # Checks if user 2 is now a member of channel 1
    # assert check_user_is_member(user_2, channel_id) == True

# INPUT ERRORS 

# test invalid channel_id
def test_invalid_channel_id(init):
    users = init[0]
    user_2 = users['u_2']['auth_user_id']
    user_1 = users['u_1']['token']

    invalid_channel_id = -1

    with pytest.raises(InputError):
        assert channel_invite_v2(user_1, invalid_channel_id, user_2)


# test invalid auth_user_id
def test_invalid_auth_user_id(init):

    users = init[0]
    user_2 = users['u_2']['auth_user_id']
    channel_id = init[1]['chan_1']

    # Assume auth_user_id should never be a negative value or less than 1000
    invalid_auth_user_id = -1

    with pytest.raises(AccessError):
        assert channel_invite_v2(invalid_auth_user_id, channel_id, user_2)

# test invalid u_id
def test_invalid_u_id(init):

    users = init[0]
    user_1 = users['u_1']['auth_user_id']
    channel_id = init[1]['chan_1']

    # Assume u_id should never be a negative value or less than 1000
    invalid_u_id = -1

    with pytest.raises(InputError):
        assert channel_invite_v2(user_1, channel_id, invalid_u_id)

# test invite someone who is already in
def test_invalid_invite(init):

    users = init[0]
    user_1 = users['u_1']['token']
    channel_id = init[1]['chan_1']

    # Assume that user 1 is already a member of channel 1
    invalid_invite = users['u_1']['auth_user_id']

    with pytest.raises(InputError):
        assert channel_invite_v2(user_1, channel_id, invalid_invite)

# authorised user is not in the channel (AccessError)
def test_invalid_authurisor(init):
    users = init[0]
    user_1 = users['u_1']['auth_user_id']
    user_2 = users['u_2']['auth_user_id']

    # user 1 is not in channel 2
    channel_id = init[1]['chan_3']

    invalid_authurisor = user_1

    with pytest.raises(AccessError):
        assert channel_invite_v2(invalid_authurisor, channel_id, user_2)
