import pytest
from src.auth import auth_register_v2
from src.dm import dm_leave_v1, dm_create_v1, dm_details_v1
from src.error import AccessError, InputError
from src.other import clear_v1
 
@pytest.fixture
def test_users():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")
    user3 = auth_register_v2("thisworldiscruel@gmail.com", "alsobeautiful!1!", "Mikasa", "Ackerman")

    users = {
        'u_1': user1,
        'u_2': user2,
        'u_3': user3,
    }
    return users

def test_invalid_dm_id(test_users):
    user_token = test_users['u_1']['token']
    fake_dm = 'this_dm_is_invalid'
    with pytest.raises(InputError):
        assert dm_leave_v1(user_token, fake_dm)

def test_invalid_user(test_users):
    user_token = test_users['u_1']['token']
    valid_id = test_users['u_2']['auth_user_id']
    u_ids = [valid_id, ]
    dm_res = dm_create_v1(user_token, u_ids)
    with pytest.raises(AccessError):
        assert dm_leave_v1('this_user_does_not_exist', dm_res['dm_id'])
    
# ASSUMPTION THAT DM_LEAVE RAISES INPUT BEFORE ACCESS
def test_both_invalid():
    invalid_user = 'this_user_is_invalid'
    fake_dm = 'this_dm_is_invalid'
    with pytest.raises(InputError):
        assert dm_leave_v1(invalid_user, fake_dm)


def test_leave(test_users):
    user_token = test_users['u_1']['token']
    user_id1 = test_users['u_2']['auth_user_id']
    user_id2 = test_users['u_3']['auth_user_id']
    u_ids = [user_id1, user_id2]
    dm_res = dm_create_v1(user_token, u_ids)

    dm_leave_v1(user_token, dm_res['dm_id'])
    current_members = dm_details_v1(test_users['u_3']['token'], dm_res['dm_id'])

    assert current_members == {
        'name': 'arminarlert, erenyaeger, mikasaackerman',
        'members': [
                {
                    'u_id': test_users['u_2']['auth_user_id'],
                    'email': "areourenemies@gmail.com",
                    'name_first': 'Armin', 
                    'name_last': 'Arlert',
                    'handle_str': 'arminarlert',
                    'profile_img_url': ""
                },
                {
                    'u_id': test_users['u_3']['auth_user_id'],
                    'email' : "thisworldiscruel@gmail.com",
                    'name_first' : 'Mikasa',
                    'name_last' : 'Ackerman',
                    'handle_str': 'mikasaackerman',
                    'profile_img_url': ""
                },
        ]
    }
    
def test_leave_dm_when_not_member(test_users):
    user_token = test_users['u_1']['token']
    user_id2 = test_users['u_2']['auth_user_id']
    user_id3 = test_users['u_3']['auth_user_id']
    u_ids = [user_id2, user_id3]
    dm_res = dm_create_v1(user_token, u_ids)

    new_user = auth_register_v2("akjwdn@gmail.com", "ajkwlnd", "awjdn", "awkjdnawd")

    with pytest.raises(AccessError):
        dm_leave_v1(new_user['token'], dm_res['dm_id'])