import pytest

from src.auth import auth_register_v2
from src.user import user_all_v1
from src.error import AccessError
from src.other import clear_v1

# TODO:
@pytest.fixture
def init():
    clear_v1()
    token = auth_register_v2('elvin@gmail.com', 'pasfsjnef', 'Elvin', 'Manaois').get('token')
    return token

def test_invalid_token(init):
    invalid_token = -1
    with pytest.raises(AccessError):
        assert user_all_v1(invalid_token)

def test_valid_user_all(init):
    token = init
    assert user_all_v1(token)

# TODO: Add when admin/permission is added
# def test_user_remove(init):
#     token = init
#     new_user = auth_register_v2('kAWJbnd@gmail.com', "adjkawnd123", 'wadf', 'awdadwad')
    
#     user_remove(token, new_user['auth_user_id'])

#     assert user_all_v1(token)
