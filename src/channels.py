from src.data_store import data_store
from src.unique_id import unique_channel_id
from src.error import AccessError, InputError
from src.other import get_id_from_token, check_user_id


def channels_list_v2(token):

    '''
    Takes a user token and returns all the channels they are a part of, including private ones.

    Arguments:
        Token - A hash for a registered user's id

    Exceptions:
        N/A

    Return Values:
        Returns a dictionary of dictionaries containing all the channels the provided user is a part of.
            example {
                Channel1 { channel details }
            }
'''

    auth_user_id = get_id_from_token(token)

    user_channels = []
    store = data_store.get()

    if not check_user_id(auth_user_id):
        raise AccessError("Invalid User")

    for channel in store['channels'].values():
        if auth_user_id in channel['all_members']:
            channel_to_add = {
                'channel_id': channel['channel_id'],
                'name': channel['name']
            }
            user_channels.append(channel_to_add)

    return {'channels': user_channels}


def channels_listall_v2(token):

    '''
        Takes a registered user's token and returns all channels currently existing, including private ones.

        Arguments:
            token (string) - A hash for a registered user's ID

        Exceptions:
            N/A

        Return Values:
            Returns a dictionary of dictionaries containing all the channels.
                example {
                    Channel1 { channel details }
                }
    '''

    
    auth_user_id = get_id_from_token(token)

    user_channels = []
    store = data_store.get()

    if not check_user_id(auth_user_id):
        raise AccessError("Invalid User")

    for channel in store['channels'].values():
            channel_to_add = {
                'channel_id': channel['channel_id'],
                'name': channel['name']
            }
            user_channels.append(channel_to_add)
    return {'channels': user_channels}


def channels_create_v2(token, name, is_public):

    '''
        Creates a channel, and adds the auth_user as a owner and global member

        Arguments:
        token (string)  - The hash of an authorised user that is a member of the channel
        name (string)       - The channel name of the new channel 
        is_public (boolean) - A true or false statement whether the new channel is going to be public or private

        Exceptions:
        InputError - length of name is less than 1 or more than 20 characters

        Return Value: 
        Returns channel_id on a valid token, name (between 1 and 20 characters) and an is_public value
    '''

    store = data_store.get()
    # Assuming that the auth_user_id is correct and is within in the database
    users = store['users']

    # Check for invalid name
    if len(name) < 1 or len(name) > 20:
        raise InputError("Invalid name")

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invald user")
        
    # Creating the new channel id
    new_channel_id = unique_channel_id.get()

    new_channel = {
        new_channel_id: {
            'channel_id': new_channel_id,
            'name': name,
            'owner_members': [auth_user_id, ],
            'all_members': [auth_user_id, ],
            'is_public': is_public,
            'messages' : [],
        }
    }

    # Adding and storing new channel into the data store    
    store['channels'].update(new_channel)
    data_store.set(store)
    
    new_channel = store['channels']

    print(new_channel)

    return {
        'channel_id': new_channel_id
    }
