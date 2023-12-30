import pytest

from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_details_v2
from src.error import InputError, AccessError
from src.other import clear_v1


'''
----------------------------------------------------
    Test Functions for channel_details_v2()
----------------------------------------------------
'''

# Input Error
# - channel_id does not refer to a valid channel

# Access Error
# - channel_id is vaild
# - the authorised user is not a member of the channel

@pytest.fixture
def init():
    clear_v1()

    # Creating User and initialising Channel attributes
    user = {
        'email': "elvin@gmail.com",
        'pass': "p@55worD123",
        'first': "Elvin",
        'last': "Manaois",
    }
    
    auth_user = auth_register_v2(user['email'], user['pass'], user['first'], user['last'])
    user.update({'auth_user': auth_user})

    channel_name = 'test_1'
    is_public = True

    # Creates Temporary Channel
    channel_id = channels_create_v2(user['auth_user']['token'], channel_name, is_public).get('channel_id')

    channel = {
        'channel_id': channel_id,
        'name': channel_name,
        'is_public': is_public,
    }

    return [user, channel]

# A valid channels_detail function
def test_valid_initial_channel_detail(init):

    details = {
        'name': init[1]['name'],
        'is_public': init[1]['is_public'],
        'owner_members': [
                {
                    'u_id': init[0]['auth_user']['auth_user_id'],
                    'email': init[0]['email'],
                    'name_first': init[0]['first'],
                    'name_last': init[0]['last'],
                    'handle_str': (init[0]['first'] + init[0]['last']).lower(),
                    'profile_img_url': ""
                }
            ],
            'all_members': [
            {
                'u_id': init[0]['auth_user']['auth_user_id'],
                'email': init[0]['email'],
                'name_first': init[0]['first'],
                'name_last': init[0]['last'],
                'handle_str': (init[0]['first'] + init[0]['last']).lower(),
                'profile_img_url': ""
            }
        ],
    }

    assert channel_details_v2(init[0]['auth_user']['token'], init[1]['channel_id']) == details

# Invalid channel_id 
def test_invalid_channel_id(init):
    valid_token = init[0]['auth_user']['token']

    # Only one channel has been created so there is no channel 10
    invalid_channel_id = 10   

    with pytest.raises(InputError):
        assert channel_details_v2(valid_token, invalid_channel_id)

# Invalid Access Error
def test_invalid_user_id(init):
    # Created a new user not authorised in current channel
    invalid_user = auth_register_v2("elon@gmail.com", "H@ppyT1me123", "Elon", "Musk")

    valid_channel_id = init[1]['channel_id']

    with pytest.raises(AccessError):
        assert channel_details_v2(invalid_user['token'], valid_channel_id)

def test_invalid_token(init):
    invalid_token = -1
    with pytest.raises(AccessError):
        assert channel_details_v2(invalid_token, init[1]['channel_id'])