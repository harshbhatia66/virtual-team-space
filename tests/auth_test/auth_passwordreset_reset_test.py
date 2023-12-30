import pytest

from src.auth import auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.error import AccessError, InputError
from src.other import clear_v1, random_code
from src import config

@pytest.fixture
def login():
    clear_v1()
    email = "andacrossthesea@gmail.com"
    password = "TATAKAE!1!"
    name_first = "Eren"
    name_last = "Yaeger"
    return [email, password, name_first, name_last]

def test_invalid_code(login):
    email = login[0]
    invalid_code = -1
    new_password = "COMP1531"
    auth_passwordreset_request_v1(email)
    with pytest.raises(InputError):
        assert auth_passwordreset_reset_v1(invalid_code, new_password)

def test_invalid_password(login):
    email = login[0]
    N = 8
    reset_code = random_code(N)
    invalid_password = "C"
    auth_passwordreset_request_v1(email)
    with pytest.raises(InputError):
        assert auth_passwordreset_reset_v1(reset_code, invalid_password)