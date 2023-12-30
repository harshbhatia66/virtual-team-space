import pytest

from src.auth import auth_register_v2, auth_logout_v1, auth_passwordreset_request_v1
from src.error import AccessError
from src.other import clear_v1
from src import config

@pytest.fixture
def login():
    clear_v1()
    email = "andacrossthesea@gmail.com"
    password = "TATAKAE!1!"
    name_first = "Eren"
    name_last = "Yaeger"
    return [email, password, name_first, name_last]

def test_valid_request(login):
    email = login[0]
    token = auth_register_v2(login[0], login[1], login[2], login[3]).get('token')
    auth_logout_v1(token)
    auth_passwordreset_request_v1(email)
