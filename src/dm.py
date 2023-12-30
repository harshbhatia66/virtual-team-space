import copy
from src.error import InputError, AccessError
from src.data_store import data_store
from src.unique_id import unique_dm_id
from src.other import check_user_id, get_dm_name, get_id_from_token, check_dm_id
from src.notification import invited_notification

def dm_messages_v1(token, dm_id, start):

    '''
        Takes a user's token and a dm_id that they are a part of and returns a dictionary 
        of messages as well as the indexes of start to end (start + 50).

        Arguments:
            token (string) - A registered user's token
            dm_id (int) - The ID of an existing DM
            start (int) - first index of message

        Exceptions:
            InputError  -> Occurs when dm_id does not refer to an existing DM   
            AccessError -> Occurs when dm_id is valid and the authorised user is not a member of the DM
            

        Return Values:
        A dictionary containing three values:
            'messages'   : List of dictionaries, where each dictionary contains types { message_id, u_id, message, time_sent }
            'start'      : first index of message
            'end'        : end index of message
    '''

    data = data_store.get()
    dms = data['dms']
    auth_user_id = get_id_from_token(token)
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid user")
    if dm_id not in dms:
        raise InputError("Invalid dm_id")
    
    dm = dms.get(dm_id)
    if auth_user_id not in dm['members']:
        raise AccessError("Not a member of DM")
    
    if start < 0:
        raise InputError("Invalid data_type")

    dm_length = len(dm['messages'])
    if start > dm_length:
        raise InputError("Invalid index")

    end = start + 50

    dm_msgs = copy.copy(dm['messages'])
    dm_msgs.reverse()
    index = dm_msgs[start : end]

    if end >= dm_length:
        end = -1

    return {
        'messages': index,
        'start': start,
        'end': end
    }


def dm_list_v1(token):

    '''
        Takes a user's token and returns the list of DMs that the user is a member of.

        Arguments:
            token (string) - A registered user's token

        Exceptions:
            N/A

        Return Values:
        A dictionary containing:
            'dms'   : a dictionary including dm_id and name
    '''

    data = data_store.get()
    dms = data['dms']
    auth_user_id = get_id_from_token(token)
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid user")
    
    user_dms = []  
    for dm in dms.values():
        if auth_user_id in dm['members']:
            dm_list = {
                'dm_id': dm.get('dm_id'),
                'name': dm.get('name'),
            }
            user_dms.append(dm_list)

    return {'dms': user_dms}

def dm_create_v1(token, u_ids):

    '''
        Takes a authorised user's token and a list of u_ids and create a dm returning a new dm_id.

        Arguments:
            token (string) - A registered authorised user's token
            u_ids (int) - a list of users id

        Exceptions:
            InputError -> Occurs when any u_id in u_ids does not refer to a valid user
                       -> There are duplicate 'u_id's in u_ids

        Return Values:
        A dictionary containing:
            'dm_id'   : the id of the newly created dm
    '''

    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid user")

    # Checks for valid u_id
    for u_id in u_ids:
        if not check_user_id(u_id):
            raise InputError("Invalid User ID")
    
    # Checks if creator auth_user_id is in u_ids
    if auth_user_id in u_ids:
        raise InputError("Invalid User IDs")

    dup_list = []
    for i in u_ids:
        if i not in dup_list:
            dup_list.append(i)
        else:
            raise InputError("Duplicate User ID")

    new_dm_id = unique_dm_id.get()
    name = get_dm_name(auth_user_id, u_ids) 
    messages = []
    members = [auth_user_id, ]
    members += u_ids

    print(members)

    new_dm = {
        new_dm_id: {
            'dm_id': new_dm_id,
            'name': name,
            'owner': auth_user_id,
            'messages': messages,
            'members': members,
        }
    }

    data['dms'].update(new_dm)
    data_store.set(data)
    
    # Notifies all users added to the dm
    for u in u_ids:
        invited_notification(auth_user_id, u, dm_id=new_dm_id, name=name)

    return {
        'dm_id': new_dm_id,
    }


def dm_details_v1(token, dm_id):

    '''
        Takes a user's token and a dm_id that they are a part of and prints
        some basic details regarding the dm, such as member information and name.

        Arguments:
            token (string) - A registered user's token

        Exceptions:
            InputError -> Occurs when dm_id does not refer to an existing DM
            AccessError -> Occurs when dm_id is valid and the authorised user is not a member of the DM

        Return Values:
        A dictionary containing two values:
            'name'      : a string containing the DM name
            'members'   : a list of dictionaries containing basic but not private information on all members
    '''

    data = data_store.get()
    all_dms = data['dms']

    #Check that the user and the DM are both valid
    if not check_dm_id(dm_id):
        raise InputError("Invalid dm_id")

    auth_user_id = get_id_from_token(token)

    if not check_user_id(auth_user_id):
        raise AccessError("Invalid user")

    dm = all_dms[dm_id]

    if auth_user_id not in dm['members']:
        raise AccessError("User non member")

    #Generate a list of members to be printed
    member_return = []
    users = data['users']
    for person in dm['members']:
        uid = users[person]
        member_to_append = {
            'u_id'      :   uid['u_id'],
            'email'     :   uid['email'],
            'name_first':   uid['name_first'],
            'name_last' :   uid['name_last'],
            'handle_str':   uid['handle_str'],
            'profile_img_url': uid['profile_img_url'],
        }
        member_return.append(member_to_append)

    return {
        'name': dm['name'],
        'members': member_return
    }


def dm_leave_v1(token, dm_id):

    '''
        Takes a user's token and a dm_id that they are a part of and removes
        them as a memeber of the dm.

        Arguments:
            token (string) - A registered user's token

        Exceptions:
            InputError -> Occurs when dm_id does not refer to an existing DM
            AccessError -> Occurs when dm_id is valid and the authorised user is not a member of the DM

        Return Values: N/A
    '''

    data = data_store.get()
    all_dms = data['dms']

    #Check that the user and the DM are both valid
    if not check_dm_id(dm_id):
        raise InputError("Invalid dm_id")

    auth_user_id = get_id_from_token(token)
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid user")

    #Remove User from Members
    dm = all_dms[dm_id]

    # Checks for non members
    if auth_user_id not in dm['members']:
        raise AccessError("User non member")

    dm['members'].remove(auth_user_id)

    data_store.set(data)

def dm_remove_v1(token, dm_id):

    '''
        Takes a user's token and a dm_id. Provided they are the owner of that DM, the DM will be deleted.

        Arguments:
            token (string) - A registered user's token
            dm_id (int) - The ID of an existing DM

        Exceptions:
            InputError Occurs when:
                    -> dm_id does not refer to an existing DM
            AccessError Occurs when:
                    -> dm_id is valid and the authorised user is not the owner of this DM
                    -> dm_id is valid but the user does not exist

        Return Values: N/A
    '''

    data = data_store.get()
    all_dms = data['dms']

    #Check that the user and the DM are both valid
    if not check_dm_id(dm_id):
        raise InputError("Invalid dm_id")

    auth_user_id = get_id_from_token(token)
    
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid user")

    dm = all_dms[dm_id]

    if dm['owner'] != auth_user_id or auth_user_id not in dm['members']:
        raise AccessError("DM can only be removed by creator")

    all_dms.pop(dm_id)

    data_store.set(data)

