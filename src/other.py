from dataclasses import dataclass
from this import d
import jwt
import random
import string
import requests
from src.data_store import Datastore, data_store
from src.error import AccessError
from src.data_store import data_store
import src.tokens as Token
from src.unique_id import unique_auth_id, unique_channel_id, unique_dm_id, unique_msg_id
from src.user_stats_store import CHANNEL_JOINED, DMS_JOINED, MESSAGE_SENT, CHANNEL_EXIST, DMS_EXIST, MESSAGE_EXIST

def clear_v1():
    """
    Clears the data for testing
    """
    store = data_store.get()
    store['users'] = {}
    store['channels'] = {}
    store['dms'] = {}
    store['standups'] = {}
    
    data_store.set(store)

    # Resets the Unique ID
    unique_auth_id.reset()
    unique_auth_id.set_start_point(1000)
    
    unique_channel_id.reset()
    unique_dm_id.reset()
    unique_msg_id.reset()

    # Resets Session Tracker
    Token.reset_session_id()

    global CHANNEL_JOINED, DMS_JOINED, MESSAGE_SENT
    CHANNEL_JOINED.clear()
    DMS_JOINED.clear()
    MESSAGE_SENT.clear()

    global CHANNEL_EXIST, DMS_EXIST, MESSAGE_EXIST
    CHANNEL_EXIST.clear()
    DMS_EXIST.clear()
    MESSAGE_EXIST.clear()

def check_user_id(u_id):
    """
    Checks if user is valid

    Args:
        u_id (int): unique auth_id from user

    Returns:
        Bool: Returns true if user exists. Returns false if user does not
    """
    status = False

    if u_id == None:
        return status

    data = data_store.get()

    if u_id in data['users']:
        status = True
    
        # Checks if user has been removed
        user = data['users'].get(u_id)
        if user['is_removed']:
            status = False

    return status

#
def get_id_from_token(token):
    """
    Finds the affiliated ID from the given token

    Args:
        token (string): A generated jwt token, with encoded values for encryption/security

    Returns:
        u_id (int): The u_id the token is affiliated with. Returns None if token is invalid
    """

    data = data_store.get()
    
    auth_user_id = None
    
    try:
        decoded_user = Token.decode_jwt(token)
    except:
        return auth_user_id
    
    for user in data['users'].values():
        if validate_user(user, decoded_user):
            auth_user_id = user['u_id']
    
    return auth_user_id

def validate_user(user, details):
    """
    Validates the user comparing the user details with the details from the token

    Args:
        user (dict): A dictionary of with user's details
        details (dict): A dictionary of the attributes given by the token

    Returns:
        Bool: Returns True if if auth_user_id and session_id is in user. Returns False if not
    """

    status = True
    auth_user_id = details['auth_user_id']
    session_id = details['session_id']

    if auth_user_id != user['u_id']:
        status = False
    
    if session_id not in user['session_list']:
        status = False
    
    return status

def get_global_owners():
    """
    Gets all global owner and stores it in a list

    Returns:
        list: An array of u_ids 
    """

    data = data_store.get()
    users = data['users']

    owners = []
    
    for user in users.values():
        if user['permission_id'] == 1:
            owners.append(user['u_id'])

    return owners
    
# creator is a string name of the dm initiator
# other is a list of names of whom the user will send the dm to
def get_dm_name(creator, other):
    """
    Generates the name of all members of the created dm

    Args:
        creator (dict): A dictionary of the user creator's details
        other (list): A list of dictionary of all users' details

    Returns:
        string: A string sorted alphabetically with proper space and commas
    """

    data = data_store.get() 
    users = data['users']
    creator_user = users.get(creator)
    creator_name = str(creator_user['name_first'] + creator_user['name_last']).lower()

    other_names = []

    for i in other:
        user = users.get(i)
        other_name = str(user['name_first'] + user['name_last']).lower()
        other_names.append(other_name)

    names = []
    names.append(creator_name)
    names += other_names
    names.sort()
    
    str_name = ""

    for name in names:
        str_name += str(name) + ", "

    str_name = str_name[:-2]

    return str_name

def check_dm_id(dm_id):
    """
    Checks if dm id is valid

    Args:
        dm_id (int): A unique id given to a created dm

    Returns:
        Bool: Returns True if the ID is valid and False if the ID is invalid.
    """

    data = data_store.get()
    dms = data['dms']

    if dm_id in dms:
        return True
    else:
        return False

def check_owner(user, channel):
    """
    checks if user is an owner of a channel

    Args:
        user (int): Details of a particular user
        channel (dict): Details of a particular channel

    Returns:
        Bool: Returns True if user is found in the list of owner members. Returns False if not.
    """
    data = data_store.get()
    curr_user = data['users'].get(user)
    
    status = False

    owner_members = channel['owner_members']
    if user in owner_members:
        status = True

    if curr_user['permission_id'] == 1:
        status = True

    return status

def check_dm_owner(user, dm):
    """
    Checks if user is an owner of a dm

    Args:
        user (int): the u_id of a user
        dm (dict): details of a given dm

    Returns:
        Bool: Returns true if user is owner. returns false if not.
    """
    data = data_store.get()
    account = data['users'][user]

    status = False
    if user is dm['owner']:
        status = True

    if account['permission_id'] == 1:
        status = True
    return status

def check_message_sender(user, message):
    """
    Checks if the given user is the sender of the given message

    Args:
        user (int): The u_id of the user
        message (dict): Details of the message

    Returns:
        _type_: _description_
    """
    
    status = False
    message_sender = message['u_id']
    if message_sender == user:
        status = True
    return status

def random_code(N):
    reset_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))
    return reset_code

def jpg_check(img_url):
    if ".jpg" in img_url or ".jpeg" in img_url:
        return True
    return False
    
