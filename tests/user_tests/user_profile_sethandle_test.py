import pytest

from src.auth import auth_register_v2
from src.user import user_profile_v1, user_profile_sethandle_v1
from src.error import AccessError, InputError
from src.other import clear_v1

@pytest.fixture
def setup():
    clear_v1()

    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    token1 = user1['token']
    u_id1 = user1.get('auth_user_id')
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert").get('token')
    
    return [token1, user2, u_id1]

# Test for
# Input error when length of handle_str is not between 3 and 20 characters inclusive
# Input error when handle_str contains characters that are not alphanumeric
# Input error when the handle is already used by another user
# Access error when incorrect token/ user
# Input error when changing handle to the previous same handle

def test_invalid_token(setup):
    invalid_token = -1

    with pytest.raises(AccessError):
        assert user_profile_sethandle_v1(invalid_token, "test")

def test_invalid_strlen1(setup):

    with pytest.raises(InputError):
        assert user_profile_sethandle_v1(setup[0], "Vi")

def test_invalid_strlen2(setup):

    with pytest.raises(InputError):
        assert user_profile_sethandle_v1(setup[0], "Rascaldoesnotdreamofbunnygirlsenpai")

def test_handle_taken(setup):

    user_profile_sethandle_v1(setup[0], "test")

    with pytest.raises(InputError):
        assert user_profile_sethandle_v1(setup[1], "test")

def test_changing_to_same_handle(setup):

    user_profile_sethandle_v1(setup[0], "erenyeager")

    with pytest.raises(InputError):
        assert user_profile_sethandle_v1(setup[0], "erenyeager")

def test_alphanumeric(setup):
    with pytest.raises(InputError):
        assert user_profile_sethandle_v1(setup[0], "@ttack")

# Check for successful handle change
def test_handle_success(setup):

    user_profile_sethandle_v1(setup[0], "AttackTitan")

    handle = user_profile_v1(setup[0], setup[2]).get('user')['handle_str']

    print(handle)

    assert handle == "AttackTitan"
