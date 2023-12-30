import copy
from src import admin as Admin
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import get_id_from_token, check_user_id
from src.notification import invited_notification
from src.standup import standup_active_v1

def channel_invite_v2(token, channel_id, u_id):

    '''
    Invites a user with ID u_id to join a channel with ID channel_id. 
    Once invited, the user is added to the channel immediately.
    In both public and private channels, all members are able to invite users.

    Arguments:
        token (string) - authorisation hash of user
        channel_id (integer) - an existing channel's ID that the provided auth_user_id is a part of
        u_id (integer) - another registered user's ID who is not in the channel provided

    Exceptions:
        InputError - Occurs when:
                        -> channel_id is invalid- i.e. not found in the stored channels
                        -> u_id is invalid- i.e. not found in stored users
        AccessError - Occurs when:
                        -> token is not a member of the channel listed with channel_id
                        -> token is invalid- i.e. not found in stored users

    Return Values: 
        {}
'''

    store = data_store.get()

    # Checks if channel_id is a valid channel
    if channel_id not in store['channels']:
        raise InputError("Invalid Channel ID")

    # Gets the channel data from channel_id
    channel = store['channels'].get(channel_id)

    # Checks if auth user ID's is valid
    auth_user_id = get_id_from_token(token)
    if not check_user_id(auth_user_id):
        assert AccessError("Invalid Authorised User")

    # Checks if user ID's are valid
    if not check_user_id(u_id):
        raise InputError("Invalid user")

    # Checks if user's member status
    if auth_user_id in channel['all_members']:
        if u_id in channel['all_members']:
            raise InputError("Already in member in channel")
        else:
            channel['all_members'].append(u_id)
    else:
        raise AccessError("Invalid Member")

    # Notifies invited user
    chan_name = channel.get('name')
    invited_notification(auth_user_id, u_id, channel_id=channel_id, name=chan_name)

    data_store.set(store)


def channel_details_v2(token, channel_id):

    '''
    Provides basic details about the user_id's specified channel 

    Arguements:
        token (string) = authorisation hash of user
        channel_id (int) = a valid channel id created from channels create

    Exceptions:
        InputError - Occurs when:
                        -> channel_id is not a valid channel
                        
        AccessError - Occurs when:
                        -> channel_id is valid but auth_user_id is not a member of the channel

    Return Values:
        Returns <name> (string) - name of channel
        Returns <is_public> (Bool) - status Bool of channel whether its private or public
        Returns <owner_members> (List) - list of all owner members and their user details
        Returns <all_members> (List) - List of all members and their user details
'''

    # Gets the data from the data storage
    data = data_store.get()
    
    # Initilises the channel variables
    details = {}
    name = ''
    owner_members = []
    all_members = []
    is_public = True

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # checks if user exists -> returns False if token does not exist
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid User")

    # Input Error - invalid channel_id
    if data['channels'].get(channel_id) == None:
        # print('No Channels')
        raise InputError("Invalid channel_id")
    
    # Access Error - Valid channel_id but auth_id is not a member
    channel = dict(data['channels'].get(channel_id))

    # Checks if user is already a membe
    if auth_user_id not in channel['all_members']:
        raise AccessError("User ID not a member")
    
    name = channel['name']
    is_public = channel['is_public']
    
    for member in channel['owner_members']:
        user_tmp = data['users'].get(member)

        details = {
        'u_id': user_tmp['u_id'],
        'email': user_tmp['email'],
        'name_first': user_tmp['name_first'],
        'name_last': user_tmp['name_last'],
        'handle_str': user_tmp['handle_str'],
        'profile_img_url': user_tmp['profile_img_url'],
        }

        owner_members.append(details)

    for member in channel['all_members']:
        user_tmp = data['users'].get(member)

        details = {
        'u_id': user_tmp['u_id'],
        'email': user_tmp['email'],
        'name_first': user_tmp['name_first'],
        'name_last': user_tmp['name_last'],
        'handle_str': user_tmp['handle_str'],
        'profile_img_url': user_tmp['profile_img_url'],
        }

        all_members.append(details)

    details = {
        'name': name,
        'is_public': is_public,
        'owner_members': owner_members,
        'all_members': all_members,
    }

    return details


def channel_messages_v2(token, channel_id, start):

    '''
    Returns up to 50 messages from a channel the auth_user is a member of

    Arguments:
      token (string)     - Authorisation has of user id
      channel_id (int)   - The channel id which the user is a member of 
      start (int)        - Start is an index which loads messages. 0 being the most recent message index, all the way to the oldest message index.

    Exceptions:
      InputError:  - Occurs when channel_id does not refer to a valid channel
                   - Occurs when start is greater than the total number of messages in the channel
                   - Occurs when user_id does not refer to a valid user
                   - Occurs when start is a negative value
                   - Occurs when start is not an integer
      AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel

    Return Value:
    Returns {'messages' = [...], 'start' = start, 'end' = start + 50} on a valid channel_messages_v1(token, channel_id, start)
'''

    data = data_store.get()

    auth_user_id = get_id_from_token(token)

    # Check for invalid channel id
    if data['channels'].get(channel_id) == None:
        print('Channel not found')
        raise InputError("Invalid channel_id")

    # Check for valid user id
    if data['users'].get(auth_user_id) == None:
        print('User ID not found')
        raise AccessError("Invalid user_id")
    
    channel = dict(data['channels'].get(channel_id))

    # Check whether the auth user is a member of the channel
    if auth_user_id not in channel['all_members']:
        print("Not a member")
        raise AccessError("User ID not a member of channel")
    
    # Check if the start variable is a positive integer 
    if start < 0:
        print("Incorrect input: please enter a postive integer")
        raise InputError("Invalid data_type")

    # Check if the start index is greater than the total messages in channel
    total_messages = len(channel['messages'])
    
    if start > total_messages:
        print("Invalid input: index exceeds total messages")
        raise InputError("Invalid index")

    # Assign the end variable the array[] value, which would be 50 + start (50 messages all together)
    end = start + 50

    # Get and copy the indexed messages into an array
    chan_msgs = copy.copy(channel['messages'])
    chan_msgs.reverse()
    indexed_messages = chan_msgs[start : end]
    # If the end is greater than the total messages reassign end to -1
    # Coverage here because no case where it end is less than total messages, since messages haven't been polluted
    if end >= total_messages:
        end = -1

    return {
        'messages': indexed_messages,
        'start': start,
        'end': end
    }



def channel_join_v2(token, channel_id):

    '''
        Given a channel_id of a channel that the auth_user can join, adds them to that channel

        Arguements:
            token (string) - authorised user token hash
            channel_id (int) - valid unqiue channel id 

        Exceptions:
            InputError - Occurs when:
                            -> channel_id is not a valid channel
                            -> authorised user is already a member

            AccessError - Occurs when:
                            -> channel_id refers to a channel that is private and the authorised user
                            is not a member yet
        Return values:
            {}
    '''

    data = data_store.get()
    
    # Checks if channel_id is a valid channel
    if channel_id not in data['channels']:
        raise InputError("Invalid Channel ID")
    
   # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # checks if user exists -> returns None if token does not exist
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid Auth User")

    # Checks if authorised user is already a member or in the owner members
    channel = data['channels'].get(channel_id)
    all_members = channel.get('all_members')
    owner_members = channel.get('owner_members')

    if auth_user_id in owner_members:
        raise InputError("Authorised User already a owner member")
    elif auth_user_id in all_members:
        raise InputError("Authorised User already a all member")

    # Checks the status of the channel whether its pulic or private
    # if private, auth user cannot join unless invited
    status = channel['is_public']

    user = data['users'].get(auth_user_id)
    if not status and user['permission_id'] != Admin.OWNER:
        raise AccessError("Invalid channel access")

    # After all testing has been done
    # Validates User and Channel
    # User can join the channel
    all_members.append(auth_user_id)
    
    data_store.set(data)

# Channel Leave
def channel_leave_v1(token, channel_id):
    data = data_store.get()

    # Converts token to auth_id
    auth_user_id = get_id_from_token(token)
    
    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald user")

    # Checks for input error - valid channel_id
    if channel_id not in data['channels']:
        raise InputError("Invalid Channel ID")
    
    channel = data['channels'].get(channel_id)

    # Gets the list of all members in the channel
    all_members = channel.get('all_members')
    
    # Checks if user is not a member of channel
    if auth_user_id not in all_members:
        raise AccessError("Invalid Auth User")

    # Checks if user started a standup
    if standup_active_v1(token, channel_id)['is_active']:
        stand_up = data['standups']
        chan_stand_up = stand_up.get(channel_id)
        u_starter = chan_stand_up['started_by']
        if auth_user_id == u_starter:
            raise InputError("User started a standup")

    # Removes user from the list
    all_members.remove(auth_user_id)

    owner_members = channel.get('owner_members')

    if auth_user_id in owner_members:
        owner_members.remove(auth_user_id)

    data_store.set(data)

def channel_addowner_v1(token, channel_id, u_id):
    # Appending user_ids into the owners key in channel id
    data = data_store.get()
    users = data['users']
    channels = data['channels']

    # Checks if channel_id is a valid channel
    if channel_id not in channels:
        raise InputError("Invalid Channel ID")

    channel = channels.get(channel_id)

    all_members = channel.get('all_members')

    owner_members = channel.get('owner_members')

    # Converts token to auth_id
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald user")

    # Checks for auth_user permissions
    user = users.get(auth_user_id)
    if auth_user_id not in owner_members and user['permission_id'] != Admin.OWNER:
        raise AccessError("User does not have authorised access")
        
    if auth_user_id not in all_members:
        raise AccessError("User is not a member of the channel")

    # Checks if u_id exists
    if u_id not in users:
        raise InputError("Invald user")

    if u_id not in all_members:
        raise InputError("User is not a member of the channel")

    if u_id in owner_members:
        raise InputError("User is already owner member")

    owner_members.append(u_id)
      
    data_store.set(data)

    return {}

def channel_removeowner_v1(token, channel_id, u_id):
    # Appending user_ids into the owners key in channel id
    data = data_store.get()
    users = data['users']
    channels = data['channels']

    # Checks if channel_id is a valid channel
    if channel_id not in channels:
        raise InputError("Invalid Channel ID")

    channel = channels.get(channel_id)

    all_members = channel.get('all_members')

    owner_members = channel.get('owner_members')

    # Converts token to auth_id
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invald user")

    # Checks if u_id exists
    if u_id not in users:
        raise InputError("Invald user")

    if u_id not in all_members:
        raise InputError("User is not a member of the channel")

    user = users.get(auth_user_id)
    if auth_user_id not in owner_members and user['permission_id'] != Admin.OWNER:
        raise AccessError("User does not have authorised access")

    if u_id not in owner_members:
        raise InputError("User is already not an owner member")

    if auth_user_id not in all_members:
        raise AccessError("User is not a member of the channel")

    # Check if user is only member

    if len(owner_members) == 1 and u_id in owner_members:
        raise InputError("User is the only owner of the channel")

    owner_members.remove(u_id)
      
    data_store.set(data)

    return {}
