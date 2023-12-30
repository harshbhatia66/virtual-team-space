import pytest
from src.auth import auth_register_v2
from src.dm import dm_remove_v1, dm_create_v1, dm_list_v1, dm_leave_v1
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
        assert dm_remove_v1(user_token, fake_dm)

def test_invalid_user(test_users):
    user_token = test_users['u_1']['token']
    user_id1 = test_users['u_2']['auth_user_id']
    user_id2 = test_users['u_3']['auth_user_id']
    u_ids = [user_id1, user_id2]
    dm_res = dm_create_v1(user_token, u_ids)
    with pytest.raises(AccessError):
        assert dm_remove_v1('this_user_does_not_exist', dm_res['dm_id'])

def test_not_owner(test_users):
    owner_token = test_users['u_1']['token']
    user_id1 = test_users['u_2']['auth_user_id']
    user_id2 = test_users['u_3']['auth_user_id']
    u_ids = [user_id1, user_id2]
    dm_res = dm_create_v1(owner_token, u_ids)

    user_token = test_users['u_2']['token']
    with pytest.raises(AccessError):
        assert dm_remove_v1(user_token, dm_res['dm_id'])

def test_remove(test_users):
    owner_token = test_users['u_1']['token']
    user_id1 = test_users['u_2']['auth_user_id']
    user_id2 = test_users['u_3']['auth_user_id']
    u_ids = [user_id1, user_id2]
    dm_res = dm_create_v1(owner_token, u_ids)
    dm_remove_v1(owner_token, dm_res['dm_id'])

    assert dm_list_v1(owner_token) == {'dms': []}

def test_owner_nonmember_cannot_remove_dm(test_users):
    owner_token = test_users['u_1']['token']
    user_id1 = test_users['u_2']['auth_user_id']
    user_id2 = test_users['u_3']['auth_user_id']
    u_ids = [user_id1, user_id2]
    dm_res = dm_create_v1(owner_token, u_ids)

    dm_leave_v1(owner_token, dm_res.get('dm_id'))

    with pytest.raises(AccessError):
        dm_remove_v1(owner_token, dm_res.get('dm_id'))