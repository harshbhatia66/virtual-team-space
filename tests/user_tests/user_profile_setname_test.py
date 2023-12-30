import pytest

from src.auth import auth_register_v2
from src.user import user_profile_setname_v1
from src.error import AccessError, InputError
from src.other import clear_v1

@pytest.fixture
def user():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user1_first = "Eren"
    user1_last = "Yaegar"
    return [user1, user1_first, user1_last]

def test_valid_user(user):
    user_1 = user[0]
    valid_token = user_1['token']
    valid_name_first = user[1]
    valid_name_last = user[2]
    user_profile_setname_v1(valid_token, valid_name_first, valid_name_last)

def test_invalid_token(user):
    invalid_token = -1
    valid_name_first = user[1]
    valid_name_last = user[2]
    with pytest.raises(AccessError):
        assert user_profile_setname_v1(invalid_token, valid_name_first, valid_name_last)


def test_invalid_name_first(user):
    user_1 = user[0]
    valid_token = user_1['token']
    invalid_name_first_50 = "abcdefgjienfnfkdjsnvsdjnvfsjdfnjsfjwehfwuhfjsdfnjknfvsjkfbnjfbcsdfsf"
    invalid_name_first_1 = ""
    valid_name_last = user[2]
    with pytest.raises(InputError):
        assert user_profile_setname_v1(valid_token, invalid_name_first_50, valid_name_last)
        assert user_profile_setname_v1(valid_token, invalid_name_first_1, valid_name_last)


def test_invalid_name_last(user):
    user_1 = user[0]
    valid_token = user_1['token']
    valid_name_first = user[1]
    invalid_name_last_50 = "abcdefgjienfnfkdjsnvsdjnvfsjdfnjsfjwehfwuhfjsdfnjknfvsjkfbnjfbcsdfsf"
    invalid_name_last_1 = ""
    with pytest.raises(InputError):
        assert user_profile_setname_v1(valid_token, valid_name_first, invalid_name_last_50)
        assert user_profile_setname_v1(valid_token, valid_name_first, invalid_name_last_1)
