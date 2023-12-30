import pytest

from src.auth import auth_login_v2, auth_register_v2
from src.error import InputError
from src.other import clear_v1

from src import config

# Invalid Email
# Duplicate Email
# Password Checks
# First Name Checks
# Last Name Checks
# Empty Fields

@pytest.fixture
def user():
    clear_v1()
    email = 'elvinmanaois@ad.unsw.edu.au'
    password = 'P@ssword1111'
    name_first = 'Elvin'
    name_last = 'Manaois'

    return [email, password, name_first, name_last]

''' 
----------------------------------------------------
    Test Functions for Registering the account 
----------------------------------------------------
'''

# A valid Registration to test when the function works
def test_valid_register(user):
    reg_return = auth_register_v2(user[0], user[1], user[2], user[3])
    auth_user_id1 = reg_return['auth_user_id']

    login_return = auth_login_v2(user[0], user[1])
    auth_user_id2 = login_return['auth_user_id']

    assert auth_user_id1 == auth_user_id2

def test_different_registers(user):
    reg1 = auth_register_v2(user[0], user[1], user[2], user[3])
    reg2 = auth_register_v2("florenzmanaois@gmail.com", "thisisapassawd", "Yes", "Hello")

    assert reg1 != reg2

# Invalid Email Test
def test_register_invalid_email(user):
    invalid_email = 'abc'

    with pytest.raises(InputError):
        assert auth_register_v2(invalid_email, user[1], user[2], user[3])

# Duplicate Email Test
def test_register_duplicate_email(user):
    auth_register_v2(user[0], user[1], user[2], user[3])
    with pytest.raises(InputError):
       assert auth_register_v2(user[0], user[1], user[2], user[3])

# Password Checks
def test_register_invalid_pass(user):
    invalid_pass = '1234'
    with pytest.raises(InputError):
        assert auth_register_v2(user[0], invalid_pass, user[2], user[3])

# First name length 1 -  50 characters inclusive
def test_register_invalid_name_first(user):
    invalid_name_50 = 'Advsvsldkvjsdsdfkjsndfksjdnfksjdnfksjdnfsdfasdfasdfasdwd'
    invalid_name_1 = ""
    with pytest.raises(InputError):
        assert auth_register_v2(user[0], user[1], invalid_name_50, user[3])
        assert auth_register_v2(user[0], user[1], invalid_name_1, user[3])

# Last name length 1 - 50 characters inclusive
def test_register_invalid_name_last(user):
    invalid_name_50 = 'Advsvsldkvjsdsdfkjsndfksjdnfksjdnfksjdnfsdfasdfasdfaswdwdd'
    invalid_name_1 = ""

    with pytest.raises(InputError):
        assert auth_register_v2(user[0], user[1], user[2], invalid_name_50) 
        assert auth_register_v2(user[0], user[1], user[2], invalid_name_1) 

# Tests for valid handle_str with more than 20 characters
def test_handle_str_over_20_chars(user):
    name_first = "awdknawlkdnawlkdnakwjndaw"
    name_last = "awkjldnawkjdnawkjdnawkjdn"

    assert auth_register_v2(user[0], user[1], name_first, name_last)

# Tests for two different registered account with the same name
def test_handle_str_duplicate(user):
    auth_register_v2(user[0], user[1], user[2], user[3])
     
    # Creates new user
    new_email = "Iamrandomman@yahoo.com"
    new_pass = "ksjdnfawdawd123123"

    # Registers new user with the same names
    assert auth_register_v2(new_email, new_pass, user[2], user[3])

# Tests for two different registered account with the same name over 20 characters
def test_handle_str_duplicate_over_20_chars(user):
    name_first = "awdnhawkjdhawkdjhawdkjhd"
    name_last = "awdjknhawkjdnakwjdnawkjdna"
    auth_register_v2(user[0], user[1], name_first, name_last)

    # Creates new user
    new_email = "Iamrandomman@yahoo.com"
    new_pass = "ksjdnfawdawd123123"

    # Registers new user with the same names
    assert auth_register_v2(new_email, new_pass, name_first, name_last)
