from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import get_id_from_token, check_user_id, get_global_owners

# Permission IDs
OWNER = 1
MEMBER = 2


def user_remove_v1(token, u_id):

    '''
    Given a user by their u_id, remove them from the Seams including all channels/DMs, 
    and will not be included in the list of users returned by users/all.

    Arguements:
        token (string) - authorisation hash
        u_id (int) - registered user id

    Exceptions:
        InputError - u_id does not refer to a valid user,
                   - u_id refers to a user who is the only global owner
        AccessError - the authorised user is not a global owner

    Return values:
        {}
    '''
    
    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald User Access")

    # Checks if u_id exists
    if not check_user_id(u_id):
        raise InputError("Invalid User ID")

    # Collects all the global owners
    owners = get_global_owners()

    # Checks if auth_user is not a global owner
    if auth_user_id not in owners:
        raise AccessError("User is not a global owner")

    # Checks if u_id is the only global owner
    if u_id in get_global_owners():
        if len(owners) <= 1:
            raise InputError("User is the only global owner")
    
    channels = data['channels']
    dms = data['dms']

    # Removes user from all channels and dms
    for channel in channels.values():
        owners = channel.get('owner_members')
        all_mems = channel.get('all_members')
        if u_id in owners or u_id in all_mems:
            # Changes contents of messages to 'Removed user'    
            messages = channel['messages']
            for msg in messages:
                if msg['u_id'] == u_id:
                    msg.update({'message': 'Removed user'})
            try: 
                channel['owner_members'].remove(u_id)
            except:
                print("Not in owners")
            
            channel['all_members'].remove(u_id)

    
    for dm in dms.values():
        if u_id in dm['members']:
            # Changes contents of messages to 'Removed user'    
            for msg in dm['messages']:
                if msg['u_id'] == u_id:
                    msg.update({'message': 'Removed user'})

            dm['members'].remove(u_id)

    # Changes user name_first and name_last
    user = data['users'].get(u_id)
    user.update({'name_first': 'Removed'})
    user.update({'name_last': 'user'})

    # Updates the user's current status
    user.update({'is_removed': True})


    # Deletes the user's email and handle
    user.update({"email": ""})
    user.update({"handle_str": ""})
    
    print(user)

    data_store.set(data)



def user_permission_change_v1(token, u_id, permission_id):

    '''
    Given a user by their user ID, set their permissions to new permissions described by permission_id.

    Arguements:
        token (string) - authorisation hash
        u_id (int) - registered user id 
        permission_id (int) - id that represents if the user is an owner or member

    Exceptions:
        InputError - u_id does not refer to a valid user,
                   - u_id refers to a user who is the only global owner and they are being demoted to a user
                   - permission_id is invalid
                   - the user already has the permissions level of permission_id
        AccessError - the authorised user is not a global owner

    Return values:
        {}
    '''

    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald User Access")

    # Checks if u_id exists
    if not check_user_id(u_id):
        raise InputError("Invalid User ID")

    # Collects all the global owners
    owners = get_global_owners()

    # Checks if auth user is not an owner
    if auth_user_id not in owners:
        raise AccessError("User is non global owner")

    # Checks if u_id is the only global owner and is being changed to member
    if u_id in get_global_owners():
        if len(owners) <= 1 and permission_id == MEMBER:
            raise InputError("User is the only global owner")
    
    # Checks if new permission_id is invalid
    invalid_ids = [OWNER, MEMBER]
    if permission_id not in invalid_ids:
        raise InputError("Invalid permission ID")
    
    # Checks if u_id is already the level of persmission_id
    user = data['users'].get(u_id)
    if user['permission_id'] == permission_id:
        raise InputError(f"User already {permission_id} level")
    
    # Checks if authorised user is not a global owner
    auth_user = data['users'].get(auth_user_id)
    if auth_user['permission_id'] != OWNER:
        raise AccessError("Auth User not a global owner")

    # Updates the current permission id
    user.update({'permission_id': permission_id})

    data_store.set(data)
