from pickletools import pystring
import pytest
from src.auth import auth_register_v2
from src.dm import dm_details_v1, dm_create_v1
from src.error import AccessError, InputError
from src.other import clear_v1
 
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

def test_invalid_dm_id(init):
    user_token = init['u_1']['token']
    fake_dm = 'this_dm_is_invalid'
    with pytest.raises(InputError):
        assert dm_details_v1(user_token, fake_dm)

def test_invalid_user(init):
    user_token = init['u_1']['token']
    valid_id = init['u_2']['auth_user_id']
    u_ids = [valid_id, ]
    dm_res = dm_create_v1(user_token, u_ids)
    with pytest.raises(AccessError):
        assert dm_details_v1('this_user_does_not_exist', dm_res['dm_id'])
    
# ASSUMPTION THAT DM_DETAILS RAISES INPUT BEFORE ACCESS
def test_both_invalid():
    invalid_user = 'this_user_is_invalid'
    fake_dm = 'this_dm_is_invalid'
    with pytest.raises(InputError):
        assert dm_details_v1(invalid_user, fake_dm)


def test_details(init):
    user_token = init['u_1']['token']
    valid_id = init['u_2']['auth_user_id']
    u_ids = [valid_id, ]
    dm_res = dm_create_v1(user_token, u_ids)

    details_result = dm_details_v1(user_token, dm_res['dm_id'])

    assert details_result == {
        'name': 'arminarlert, erenyaeger',
        'members': [
                {
                    'u_id': init['u_1']['auth_user_id'],
                    'email' : "andacrossthesea@gmail.com",
                    'name_first' : 'Eren',
                    'name_last' : 'Yaeger',
                    'handle_str': 'erenyaeger',
                    'profile_img_url': ""
                },

                {
                    'u_id': init['u_2']['auth_user_id'],
                    'email': "areourenemies@gmail.com",
                    'name_first': 'Armin', 
                    'name_last': 'Arlert',
                    'handle_str': 'arminarlert',
                    'profile_img_url': ""
                },
   
        ]
    }

def test_non_member_not_successful(init):
    user_token = init['u_1']['token']
    valid_id = init['u_2']['auth_user_id']
    u_ids = [valid_id, ]
    dm_res = dm_create_v1(user_token, u_ids)
    
    new_user = auth_register_v2("akjwdn@gmail.com", "ajkwlnd", "awjdn", "awkjdnawd")

    with pytest.raises(AccessError):
        assert dm_details_v1(new_user['token'], dm_res['dm_id'])
