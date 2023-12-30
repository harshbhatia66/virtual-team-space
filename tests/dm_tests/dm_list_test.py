import pytest

from src.error import AccessError
from src.auth import auth_register_v2
from src.dm import dm_list_v1, dm_create_v1
from src.other import clear_v1

@pytest.fixture
def init():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    user2 = auth_register_v2("areourenemies@gmail.com", "tatakae!1!", "Armin", "Arlert")

    u_ids = [user2['auth_user_id']]
    
    dm = dm_create_v1(user1['token'], u_ids)
    
    return [user1, u_ids, dm]

# Tests for valid details, returns list of dms
def test_valid_dm(init):
    user1_token = init[0]['token']

    res = {
        'dms': [
            {
                'dm_id': 1,
                'name': 'arminarlert, erenyaeger'
            },
        ]
    }
    assert dm_list_v1(user1_token) == res


def test_valid_dm_list(init):
    token = init[0]['token']

    dm_list_v1(token)

def test_invalid_token(init):
    invalid_token = -1 
    with pytest.raises(AccessError):
        assert dm_list_v1(invalid_token)
