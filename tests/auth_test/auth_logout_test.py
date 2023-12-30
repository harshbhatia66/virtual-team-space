import pytest

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1
from src.error import AccessError
from src.other import clear_v1
from src import config

@pytest.fixture
def login():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    users = {
        'u_1': user1,
    }   
    return users

def test_valid_logout(login):
    active_token = login['u_1']['token']
    auth_logout_v1(active_token)

def test_invalid_token(login):
    invalid_token = -1
    with pytest.raises (AccessError):
        assert auth_logout_v1(invalid_token)
