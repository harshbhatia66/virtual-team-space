import pytest
from src import data_store

from src.auth import auth_login_v2, auth_register_v2
from src.error import InputError
from src.other import clear_v1

''' 
----------------------------------------------------
    Test Functions for Logging into the account 
----------------------------------------------------
'''

@pytest.fixture
def login():
    clear_v1()
    email = 'chelseaarezo@ad.unsw.edu.au'
    password = 'P@ssword1111'
    name_first = 'Chelsea'
    name_last = 'Arezo'
    return [email, password, name_first, name_last]

# Tests for a valid user login
def test_valid_login_id(login):
    reg_result = auth_register_v2(login[0], login[1], login[2], login[3]).get('auth_user_id')
    log_result = auth_login_v2(login[0], login[1]).get('auth_user_id')

    assert reg_result == log_result

# Tests for an invalid user email
def test_invalid_user_email(login):
    auth_register_v2(login[0], login[1], login[2], login[3])
    invalid_email = 'abc'
    with pytest.raises(InputError):
        assert auth_login_v2(invalid_email, login[1])

# Tests for an invalid password
def test_invalid_password(login):
    auth_register_v2(login[0], login[1], login[2], login[3])
    invalid_password = '1234'
    with pytest.raises(InputError):
        assert auth_login_v2(login[0], invalid_password)
        
