import pytest

from src.auth import auth_register_v2
from src.user import user_all_v1, user_profile_setemail_v1
from src.error import AccessError, InputError
from src.other import clear_v1

@pytest.fixture
def users():
    clear_v1()
    user1 = auth_register_v2("thisworldiscruel@gmail.com", "tatakae!1!", "Mikasa", "Ackerman")
    user2 = auth_register_v2("butistillloveyou@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    users = {
        'u_1': user1,
        'u_2': user2,
    }
    return users

def test_duplicate_email(users):
    user_token = users['u_1']['token']
    dupe_email = "butistillloveyou@gmail.com"
    with pytest.raises(InputError):
        assert user_profile_setemail_v1(user_token, dupe_email)

def test_invalid_email(users):
    user_token = users['u_1']['token']
    not_email = "this_is_not_an_email"
    with pytest.raises(InputError):
        assert user_profile_setemail_v1(user_token, not_email)

def test_setemail(users):
    user_token = users['u_1']['token']
    new_email = "butitisbeautiful@gmail.com"
    user_profile_setemail_v1(user_token, new_email)

    assert user_all_v1(user_token) == {
        'users' : [
                {
                    'u_id': users['u_1']['auth_user_id'],
                    'email': "butitisbeautiful@gmail.com",
                    'name_first': 'Mikasa', 
                    'name_last': 'Ackerman',
                    'handle_str': 'mikasaackerman',
                    'profile_img_url': ""
                },
                {
                    'u_id': users['u_2']['auth_user_id'],
                    'email' : "butistillloveyou@gmail.com",
                    'name_first' : 'Eren',
                    'name_last' : 'Yaeger',
                    'handle_str': 'erenyaeger',
                    'profile_img_url': ""
                },
        ]
    }
