import pytest

from src.auth import auth_register_v2
from src.channels import channels_create_v2, channels_listall_v2
from src.error import AccessError
from src.other import clear_v1


'''
----------------------------------------------------
    Test Functions for channels_list_v2()
----------------------------------------------------
'''
@pytest.fixture
def register_users_channels():
    clear_v1()

    # Creating User and initialising Channel attributes
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    is_public = True
    not_public = False

    # Make some channels for testing
    channel1 = channels_create_v2(user1['token'], name= "test_channel1", is_public= is_public)
    channel2 = channels_create_v2(user2['token'], name= "test_channel2", is_public= not_public)
    channel3 = channels_create_v2(user1['token'], name= "test_channel3", is_public= is_public)

    return [user1['token'], user2['token'], channel1, channel2, channel3]


def test_channels_listall_withprivate(register_users_channels):

    user1_output = channels_listall_v2(register_users_channels[0])

    expected_result = {

        'channels': [
            {
            'channel_id': register_users_channels[2].get('channel_id'),
            'name': 'test_channel1',
            },
             {
            'channel_id': register_users_channels[3].get('channel_id'),
            'name': 'test_channel2',
            },    
            {
            'channel_id': register_users_channels[4].get('channel_id'),
            'name': 'test_channel3',
            },       
        ]
    }
    
    assert user1_output == expected_result

def test_channels_listall_invaliduser(register_users_channels):
    invalid_id = 'aaa'
    with pytest.raises(AccessError):
        assert channels_listall_v2(invalid_id)
