import pytest
import src.admin as Admin
from src.admin import user_permission_change_v1

from src.auth import auth_register_v2
from src.error import InputError, AccessError
from src.other import clear_v1

@pytest.fixture
def init():
    clear_v1()
    user1 = auth_register_v2("elvin@gmail.com", "awkjdn2314", "Elvin", "Manaois")
    user2 = auth_register_v2("bobdabuilder@yahoo.com", "awdmabw21314", "Bob", "DaBuilder")

    return [user1, user2]

def test_invalid_token(init):
    invalid_token = -1
    u_id = init[1]["auth_user_id"]
    permission_id = Admin.OWNER
    with pytest.raises(AccessError):
        assert user_permission_change_v1(invalid_token, u_id, permission_id)

def test_invalid_u_id(init):
    token = init[0]['token']
    invalid_id = -1
    permission_id = Admin.OWNER
    with pytest.raises(InputError):
        assert user_permission_change_v1(token, invalid_id, permission_id)

def test_u_id_only_global_owner(init):
    token = init[0]['token']
    only_u_id = init[0]['auth_user_id']
    permission_id = Admin.OWNER

    with pytest.raises(InputError):
        assert user_permission_change_v1(token, only_u_id, permission_id)

def test_u_id_only_global_owner_demoted(init):
    token = init[0]['token']
    only_u_id = init[0]['auth_user_id']
    permission_id = Admin.MEMBER

    with pytest.raises(InputError):
        assert user_permission_change_v1(token, only_u_id, permission_id)

def test_invalid_permission_id(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    invalid_id = -1

    with pytest.raises(InputError):
        assert user_permission_change_v1(token, u_id, invalid_id)
    
def test_same_level_permission(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    perm_id = Admin.MEMBER

    with pytest.raises(InputError):
        assert user_permission_change_v1(token, u_id, perm_id)

def test_auth_user_not_global_owner(init):
    new_user = auth_register_v2("awdjba@gmail.com", "awdjn232344", "awdjn", "awdjbb")
    token = init[1]['token']
    u_id = new_user['auth_user_id']
    perm_id = Admin.OWNER

    with pytest.raises(AccessError):
        assert user_permission_change_v1(token, u_id, perm_id)

def test_valid_permission_change(init):
    token = init[0]['token']
    u_id = init[1]['auth_user_id']
    perm_id = Admin.OWNER

    user_permission_change_v1(token, u_id, perm_id)

def test_nonowner_cant_change_permissions(init):
    with pytest.raises(AccessError):
        user_permission_change_v1(init[1]['token'], init[0]['auth_user_id'], Admin.MEMBER)