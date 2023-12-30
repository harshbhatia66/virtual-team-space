import pytest
from src.auth import auth_register_v2
from src.dm import dm_create_v1
from src.error import InputError, AccessError
from src.other import clear_v1


''' 
----------------------------------------------------
    Test Functions for DMs 
----------------------------------------------------
'''

@pytest.fixture
def init():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    
    users = {
        'u_1': user1,
        'u_2': user2,
    }
    return users

# Creates dm_id if all details are valid
def test_valid_dm(init):
    user_token = init['u_1']['token']
    valid_id = init['u_2']['auth_user_id']
    u_ids = [valid_id, ]
    dm_res = dm_create_v1(user_token, u_ids) 
    assert dm_res['dm_id'] == 1

# Invalid token test
def test_invalid_token(init):
    invalid_token = -1
    valid_id = init['u_1']['auth_user_id']
    u_ids = [valid_id, ]
    with pytest.raises(AccessError):
        assert dm_create_v1(invalid_token, u_ids)

# Invalid u_id test
def test_invalid_u_id(init):
    user_token = init['u_1']['token']
    invalid_id = -1
    invalid_u_ids = [invalid_id, ]
    with pytest.raises(InputError):
        assert dm_create_v1(user_token, invalid_u_ids)

# Duplicate u_id in u_ids test
def test_duplicate_u_id(init):
    user_token = init['u_1']['token']
    dup_id = 1002
    duplicate_u_ids = [dup_id, dup_id]
    with pytest.raises(InputError):
        assert dm_create_v1(user_token, duplicate_u_ids)

# Tests if owner of dm is in list of u_ids
def test_owner_in_u_ids(init):
    user_token = init['u_1']['token']
    invalid_id = init['u_1']['auth_user_id']
    reg = [invalid_id, ]

    with pytest.raises(InputError):
        assert dm_create_v1(user_token, reg)
