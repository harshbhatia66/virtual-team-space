import pytest

from src.auth import auth_login_v2, auth_register_v2
from src.channels import channels_create_v2
from src.error import AccessError, InputError
from src.other import clear_v1

# Testing for:
# Correct auth_user_id
# Correct name length
# Duplicate names

# Creating users and logging in to simulate a channels creation
# Assuming that users have been created successfully

@pytest.fixture
def user():
    clear_v1()
    email = 'ErenYeager@ad.unsw.edu.au'
    password = 'il0veFreedom'
    first_name = 'Eren'
    last_name = 'Yeager'

    auth_register_v2(email, password, first_name, last_name)

    return [email, password, first_name, last_name]

# Testing invalid name lengths
def test_channels_name_len_1(user):
    # User logs in for user_id key
    user_id = auth_login_v2(user[0], user[1])
    auth_token = user_id['token']
    with pytest.raises(InputError):
        assert channels_create_v2(auth_token, '', False)

# Testing invalid name lengths
def test_channels_name_len_20(user):
    # User logs in for user_id key
    user_id = auth_login_v2(user[0], user[1])
    auth_token = user_id['token']
    with pytest.raises(InputError):
        assert channels_create_v2(auth_token, 'longerthanthgwentycharacters', True)

# Testing invalid auth_user_id
def test_invalid_token(user):
    with pytest.raises(AccessError):
        assert channels_create_v2(-1, 'literallyanything', True)

def test_valid_channel_create(user):
    user_id = auth_login_v2(user[0], user[1])
    auth_token = user_id['token']
    assert channels_create_v2(auth_token, 'Cool Channel', True)

def test_valid_channel_create_1_character(user):
    user_id = auth_login_v2(user[0], user[1])
    auth_token = user_id['token']
    assert channels_create_v2(auth_token, '1', True)

def test_valid_channel_create_20_character(user):
    user_id = auth_login_v2(user[0], user[1])
    auth_token = user_id['token']
    assert channels_create_v2(auth_token, 'qwertyuioplkjhgfdsaz', True)
