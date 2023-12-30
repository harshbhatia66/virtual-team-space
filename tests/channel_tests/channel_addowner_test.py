import pytest

from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_addowner_v1, channel_join_v2, channel_details_v2
from src.error import InputError, AccessError
from src.other import clear_v1
from tests.helper_test import check_user_is_channel_owner

'''
----------------------------------------------------
    Test Functions for channel_addowner
----------------------------------------------------
'''

# Input Error
# - channel_id does not refer to a valid channel

# Access Error
# - channel_id is vaild
# - the authorised user is not a member of the channel

@pytest.fixture
def setup():
    clear_v1()
    # Create users and a channel to populate some messages

    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = auth_register_v2("ilovemyredscarf@gmail.com", "Ereh1LY!", "Mikasa", "Ackerman")
    user4 = auth_register_v2("euthanasia@gmail.com", "M0nkeEE!", "Zeke", "Yaeger")

    channel_id = channels_create_v2(user1['token'], 'The Sea', True).get('channel_id')

    channel_join_v2(user2['token'], channel_id)

    channel_join_v2(user3['token'], channel_id)


    return [channel_id, user1, user2, user3, user4]

# Make user with user id u_id an owner of the channel.
# Input - { token, channel_id, u_id }, where token is the auth user who has owner permissions and can add owner

# Invalid channel_id 
def test_invalid_channel_id(setup):

    
    invalid_channel_id = -1   

    u_id = setup[2]['auth_user_id']

    with pytest.raises(InputError):
        assert channel_addowner_v1(setup[1]['token'], invalid_channel_id, u_id)

def test_invalid_token(setup):
    invalid_token = -1

    u_id = setup[2]['auth_user_id']

    with pytest.raises(AccessError):
        assert channel_addowner_v1(invalid_token, setup[0], u_id)

def test_invalid_u_id(setup):

    # Assume auth_user_id should never be a negative value or less than 1000
    invalid_u_id = -1

    with pytest.raises(InputError):
        assert channel_addowner_v1(setup[1]['token'], setup[0], invalid_u_id)

def test_invalid_member(setup):

    u_id_notmember = setup[4]['auth_user_id']

    with pytest.raises(InputError):
        assert channel_addowner_v1(setup[1]['token'], setup[0], u_id_notmember)

def test_already_owner(setup):

    owner_id = setup[1]['auth_user_id']

    with pytest.raises(InputError):
        assert channel_addowner_v1(setup[1]['token'], setup[0], owner_id)
    
def test_unauthorised_access(setup):

    u_id = setup[3]['auth_user_id']

    with pytest.raises(AccessError):
        assert channel_addowner_v1(setup[2]['token'], setup[0], u_id)

# Valid channel, however token/ auth user does not exist in channel
def test_unauthorised_token(setup):

    u_id = setup[2]['auth_user_id']

    with pytest.raises(AccessError):
        assert channel_addowner_v1(setup[4]['token'], setup[0], u_id)

# Valid test
def test_successful_addowner(setup):

    u_id = setup[2]['auth_user_id']
    channel_addowner_v1(setup[1]['token'], setup[0], u_id)

    # Use the channel details function to check if owner has been added

    owner_members = channel_details_v2(setup[1]['token'], setup[0]).get('owner_members')

    status = False

    if check_user_is_channel_owner(owner_members, u_id):
        status = True
    
    assert status == True

def test_global_owner_member_can_addowner(setup):
    new_channel = channels_create_v2(setup[2]['token'], "Test", True).get('channel_id')

    channel_join_v2(setup[1]['token'], new_channel)
    channel_join_v2(setup[3]['token'], new_channel)
    channel_addowner_v1(setup[1]['token'], new_channel, setup[3]['auth_user_id'])

def test_non_member_cannot_add_owner(setup):
    new_channel = channels_create_v2(setup[2]['token'], "Test", True).get('channel_id')

    channel_join_v2(setup[3]['token'], new_channel)

    with pytest.raises(AccessError):
        channel_addowner_v1(setup[1]['token'], new_channel, setup[3]['auth_user_id'])

def test_global_owner_non_member_cant_addowner_private(setup):
    new_channel = channels_create_v2(setup[2]['token'], "Test", False).get('channel_id')

    with pytest.raises(AccessError):
        channel_addowner_v1(setup[1]['token'], new_channel, setup[1]['auth_user_id'])

def test_global_owner_non_member_cant_addowner_public(setup):
    new_channel = channels_create_v2(setup[2]['token'], "Test", True).get('channel_id')

    with pytest.raises(AccessError):
        channel_addowner_v1(setup[1]['token'], new_channel, setup[1]['auth_user_id'])