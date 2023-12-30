import re
from src import config
from src.unique_id import unique_img_id
from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import get_id_from_token, check_user_id, jpg_check
from io import BytesIO
from PIL import Image
import requests
from src.other import get_id_from_token, check_user_id
from src.channels import channels_list_v2
from src.dm import dm_list_v1
from src.user_stats_store import CHANNEL_JOINED, DMS_JOINED, MESSAGE_SENT, CHANNEL_EXIST, DMS_EXIST, MESSAGE_EXIST
from src.user_stats_store import get_channels_list, get_dm_list

import time

def users_stats_v1(token):
    """ Fetches the required statistics about the use of UNSW Seams.

    Args:
        token (string): A registered user's token

    Exceptions:
        N/A 

    Returns:
        {workspace_stats }: Dictionary of shape 
                        {
                            channels_exist: [{num_channels_exist, time_stamp}], 
                            dms_exist: [{num_dms_exist, time_stamp}], 
                            messages_exist: [{num_messages_exist, time_stamp}], 
                            utilization_rate
                        }
    """
    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald user")

    num_channels_exist = len(data['channels'])
    num_dms_exist = len(data['dms'])

    num_msgs = 0

    for chan in data['channels'].values():
        num_msgs += len(chan.get('messages'))

    for dm in data['dms'].values():
        num_msgs += len(dm.get('messages'))


    num_users = len(data['users'])

    users = data['users']
    active_users = [user['u_id'] for user in users.values() \
                if len(get_channels_list(user['u_id'])) > 0 or len(get_dm_list(user['u_id'])) > 0]

    num_active_users = len(active_users)

    utilization_rate = 0.0
    if num_users != 0:
        utilization_rate = float(num_active_users / num_users)

    time_stamp = int(time.time())

    global CHANNEL_EXIST, DMS_EXIST, MESSAGE_EXIST
    CHANNEL_EXIST.append({'num_channels_exist': num_channels_exist, 'time_stamp': time_stamp})
    DMS_EXIST.append({'num_dms_exist': num_dms_exist, 'time_stamp': time_stamp})
    MESSAGE_EXIST.append({'num_messages_exist': num_msgs, 'time_stamp': time_stamp})
    
    return {
        'workspace_stats': {
            'channels_exist': CHANNEL_EXIST, 
            'dms_exist': DMS_EXIST, 
            'messages_exist': MESSAGE_EXIST, 
            'utilization_rate': utilization_rate
        }
    }

def user_stats_v1(token):
    """ Fetches the required statistics about this user's use of UNSW Seams.

    Args:
        token (string): A registered user's token

    Exceptions:
        N/A 

    Returns:
        {user_stats}: Dictionary of shape 
                        {
                            channels_joined: [{num_channels_joined, time_stamp}],
                            dms_joined: [{num_dms_joined, time_stamp}], 
                            messages_sent: [{num_messages_sent, time_stamp}], 
                            involvement_rate 
                        }
    """
    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald user")

    # Getting channels joined
    channels = [chan['channel_id'] for chan in channels_list_v2(token).get('channels')]
    num_channels_joined = len(channels)

    # User dms joined
    dms = [dm['dm_id'] for dm in dm_list_v1(token).get('dms')]
    num_dms_joined = len(dms)
    
    # User messages sent
    chan_msgs = [m['message_id'] for chan_id in channels for m in data['channels'][chan_id]['messages'] if m['u_id'] == auth_user_id]
    dm_msgs = [m['message_id'] for dm_id in dms for m in data['dms'][dm_id]['messages'] if m['u_id'] == auth_user_id]
    
    num_messages_sent = len(chan_msgs) + len(dm_msgs)

    # Seams Overall stats
    num_channels = len(data['channels'])
    num_dms = len(data['dms'])
    
    num_msgs = 0
    for chan in data['channels'].values():
        num_msgs += len(chan.get('messages'))

    for dm in data['dms'].values():
        num_msgs += len(dm.get('messages'))

    user_involment = 0.0

    total_user_joined = sum([num_channels_joined, num_dms_joined, num_messages_sent])
    total_seams_stats = sum([num_channels, num_dms, num_msgs])

    if total_seams_stats != 0:
        user_involment = float(total_user_joined / total_seams_stats)

    print(f"{num_channels_joined, num_dms_joined, num_messages_sent}")

    print(f"{total_user_joined} / {total_seams_stats} = {user_involment}")

    time_stamp = int(time.time())
    
    global CHANNEL_JOINED
    global DMS_JOINED
    global MESSAGE_SENT

    CHANNEL_JOINED.append({'num_channels_joined': num_channels_joined, "time_stamp": time_stamp})
    DMS_JOINED.append({'num_dms_joined': num_dms_joined, "time_stamp": time_stamp})
    MESSAGE_SENT.append({'num_messages_sent': num_messages_sent, "time_stamp": time_stamp})

    return {
        'user_stats': {
            'channels_joined': CHANNEL_JOINED,
            'dms_joined': DMS_JOINED,
            'messages_sent': MESSAGE_SENT,
            'involvement_rate': user_involment
        }
    }
def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    '''
        Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end).

        Arguments:
            token (string) - A registered user's token
            img_url (string) - A web address of a jpg/jpeg file
            x_start (int) - Coordinate point x_start
            y_start (int) - Coordinate point y_start
            x_end (int) - Coordinate point x_end
            y_end (int) - Coordinate point y_end

        Exceptions:
            InputError occurs when:
                    -> img_url returns an HTTP status other than 200, or any other errors occur when attempting to retrieve the image
                    -> any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
                    -> x_end is less than or equal to x_start or y_end is less than or equal to y_start
                    -> image uploaded is not a JPG
        Return Values:
            {} 
    '''

    data = data_store.get()
    
    auth_user_id = get_id_from_token(token)
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid user")
    if not jpg_check(img_url):
        raise InputError("Not a jpg or jpeg file")

    response = requests.get(img_url)
    if response.status_code != 200:
        raise InputError("Status code not 200")

    image = Image.open(BytesIO(response.content))

    width, height = image.size

    if x_start < 0 or x_end < 0 or y_start < 0 or y_end < 0:
        raise InputError("Invalid dimensions")
    if x_start > x_end or y_start > y_end:
        raise InputError("Invalid dimensions")
    if x_start > width or x_end > width:
        raise InputError("Invalid dimensions")
    if y_start > height or y_end > height:
        raise InputError("Invalid dimensions")
    
    new_image = image.crop((x_start, y_start, x_end, y_end))

    img_id = unique_img_id.get()
    profile_img_url = config.url + f"imgurl/{img_id}.jpeg"
    new_image.save(f"database/static/{img_id}.jpeg")

    user = data['users'].get(auth_user_id)
    user.update({'profile_img_url': profile_img_url})

    data_store.set(data)

    return {}

def user_profile_setname_v1(token, name_first, name_last):

    '''
        Takes a user's token, the user's name_first and name_last, which updates the user's name in the data store.

        Arguments:
            token (string) - A hash registered authorised user's ID
            name_first (string) - String of a user's first name
            name_last (string) - String of a user's last name

        Exceptions:
            InputError -> length of name_first is not between 1 and 50 characters inclusive
                       -> length of name_last is not between 1 and 50 characters inclusive
        Return Values:
            {}
    '''

    print(name_first)
    data = data_store.get()
    users = data['users']
    auth_user_id = get_id_from_token(token)
    if not check_user_id(auth_user_id):
        raise AccessError("Invald user") 

    if len(name_first) < 1:
        raise InputError("Invalid name_first")
    if len(name_first) > 50:
        raise InputError("Invalid name_first")

    if len(name_last) < 1:
            raise InputError("Invalid name_last")
    if len(name_last) > 50:
        raise InputError("Invalid name_last")
    
    user = users.get(auth_user_id)
    user.update({'name_first': name_first})
    user.update({'name_last': name_last})

    data_store.set(data)


def user_all_v1(token):

    '''
        Returns a list of all users and their associated details.

        Arguments:
            token (string) - A hash for registered authorised user's ID

        Exceptions:
            N/A
            
        Return Values:
            { users } - List of dictionaries, where each dictionary contains a user's u_id, email, name_first, name_last, handle_str
    '''

    data = data_store.get()
    users = data['users']
    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald user")

    all_users = []

    for user in users.values():
        if user['name_first'] == 'Removed' and user['name_last'] == 'user':
            continue
        user_tmp = user

        details = {
        'u_id': user_tmp['u_id'],
        'email': user_tmp['email'],
        'name_first': user_tmp['name_first'],
        'name_last': user_tmp['name_last'],
        'handle_str': user_tmp['handle_str'],
        'profile_img_url': user_tmp['profile_img_url'],
        }
        all_users.append(details)

    return {
        'users': all_users,
    } 

def user_profile_v1(token, u_id):

    '''
        For a valid user, returns information about their user_id, email, first name, last name, and handle.

        Arguments:
            token (string) - A hash for registered authorised user's ID
            u_id (int) - A user's ID

        Exceptions:
            InputError -> u_id does not refer to a valid user
            
        Return Values:
            { users } - List of dictionaries, where each dictionary contains a user's u_id, email, name_first, name_last, handle_str
    '''


    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid user")
    
    # checks if u_id is not a valid user
    if not check_user_id(u_id):
        raise InputError("Invalid user")

    user = data['users'].get(u_id)

    details = {
        'u_id': user['u_id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str'],
        'profile_img_url': user['profile_img_url'],
    }

    data_store.set(data)

    return {
        'user': details,
    }

def user_profile_sethandle_v1(token, handle_str):

    '''
        Update the authorised user's handle (i.e. display name)

        Arguments:
            token (string) - A hash for registered authorised user's ID
            handle_str (string) - A user's username

        Exceptions:
            InputError -> length of handle_str is not between 3 and 20 characters inclusive
                       -> handle_str contains characters that are not alphanumeric
                       -> the handle is already used by another user
            
        Return Values:
            {}
    '''

    data = data_store.get()

    users = data['users']

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)
    
    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invalid user")

    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError("handle_str length is not between 3 and 20 characters")

    if not handle_str.isalnum():
        raise InputError("handle_str is not alphanumeric")
    
    if users[auth_user_id]['handle_str'] == handle_str:
        raise InputError("handle_str entered is the same as current handle_str")

    # Check for duplicate handle string
    for user in users:
        if handle_str == users[user]['handle_str']:
            raise InputError("Handle already exists")

    # Changing handle str

    users[auth_user_id]['handle_str'] = handle_str

    data_store.set(data)

    return {}

def user_profile_setemail_v1(token, email):

    '''
        Takes a user token and an email and changes the user's current email to the new one given.

        Arguments:
            email (string) - a valid user email address with the proper characters
            token (string) - the user's token.

        Exceptions:
            InputError - Occurs when:
                            -> email is not a valid email
                            -> email address already being used

        Return Values:
            {}
    '''

    data = data_store.get()
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald user")
            
    # Checks for Invalid Email Inputs
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(regex, email):
        raise InputError("Invalid email")

    all_users = data['users']

    #Check for duplicate emails
    for uid in all_users.values():
        if uid['email'] == email:
            raise InputError("Email already in use")

    user = all_users[auth_user_id]
    user['email'] = email

    data_store.set(data)
