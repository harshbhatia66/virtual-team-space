import pytest

from src.auth import auth_register_v2
from src.user import user_profile_v1
from src.error import AccessError, InputError
from src.other import clear_v1

@pytest.fixture
def setup():
    clear_v1()
    user1 = auth_register_v2('elvin@gmail.com', 'akwjdhaw123', 'Elvin', 'Manaois')
    user2 = auth_register_v2('bobdabuilder@gmail.com', 'awdjnawkdn1123124', 'Bob', 'Builder')

    return [user1, user2]

def test_invalid_token(setup):
    invalid_token = -1
    u_id = setup[1]['auth_user_id']

    with pytest.raises(AccessError):
        assert user_profile_v1(invalid_token, u_id)

def test_invalid_u_id(setup):
    token = setup[0]['token']
    invalid_u_id = -1

    with pytest.raises(InputError):
        assert user_profile_v1(token, invalid_u_id)

def test_valid_profile(setup):
    token = setup[0]['token']
    u_id = setup[1]['auth_user_id']

    details = {
        'user': {
            'u_id': 1002,
            'email': "bobdabuilder@gmail.com",
            'name_first': 'Bob',
            'name_last': 'Builder',
            'handle_str': 'bobbuilder',
            'profile_img_url': ""
        },
    }

    assert user_profile_v1(token, u_id) == details
