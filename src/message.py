from tabnanny import check
from unittest import result
from blinker import receiver_connected
from pickle import FALSE
from threading import Thread, ThreadError
from src.unique_id import unique_msg_id
from tabnanny import check
from src.channels import channels_list_v2
from src.data_store import data_store
from src.dm import dm_list_v1
from src.error import InputError, AccessError
from src.other import get_id_from_token, check_owner, check_message_sender, check_dm_owner, check_user_id
from src.notification import tagging, reacted_notification
import time

from extra_features import pet_bot


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    """
    Send a message from the authorised user 
    to the channel specified by channel_id automatically at a specified time 
    in the future.

    Args:
        token (string): A registered user's token
        dm_id (int): The dm id for the message is in
        message (string): user message
        time_sent (int): specified time in the future to when the message will be sent

    Raises:
        AccessError: token is not an authorised user
        InputError: Invalid channel id
        AccessError: user is not a member
        InputError: invalid message length
        InputError: invalid time_sent

    Returns:
        message_id (int) : unique message id
    """
    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    if not check_user_id(auth_user_id):
        raise AccessError("Invalid Token")
    
    # Validates channel_id
    dms = data['dms']
    if dm_id not in dms:
        raise InputError("Invalid channel_id")
    
    # Checks if auth_user is a non member
    channel = dms.get(dm_id)
    all_members = channel.get('members')
    if auth_user_id not in all_members:
        raise AccessError("User non-member")
    
    # Checks the length of the message
    msg_len = len(message)
    if msg_len < 1 or msg_len > 1000:
        raise InputError("Invalid message length")
    
    # Checks for time_sent
    curr_time = int(time.time())
    if time_sent < curr_time:
        raise InputError("Invalid Time Sent")
    
    def task():
        curr_time = int(time.time())
        while curr_time != time_sent:
            curr_time = int(time.time())
        else:
            global msg_id
            msg_id = message_send_dm_v1(token, dm_id, message).get('message_id')
            
    t1 = Thread(target=task)
    
    try:
        t1.start()
        t1.join()
    except ThreadError:
        print("Thread Error")

    return {
        'message_id': msg_id
    }

def message_sendlater_v1(token, channel_id, message, time_sent):
    """
    Send a message from the authorised user to the DM specified by dm_id automatically at a specified time in the future.

    Args:
        token (string): A registered user's token
        channel_id (int): The channel id for the message is in
        message (string): user message
        time_sent (int): specified time in the future to when the message will be sent

    Raises:
        AccessError: token is not an authorised user
        InputError: Invalid channel id
        AccessError: user is not a member
        InputError: invalid message length
        InputError: invalid time_sent

    Returns:
        message_id (int) : unique message id
    """
    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    if not check_user_id(auth_user_id):
        raise AccessError("Invalid Token")
    
    # Validates channel_id
    channels = data['channels']
    if channel_id not in channels:
        raise InputError("Invalid channel_id")
    
    # Checks if auth_user is a non member
    channel = channels.get(channel_id)
    all_members = channel.get('all_members')
    if auth_user_id not in all_members:
        raise AccessError("User non-member")
    
    # Checks the length of the message
    msg_len = len(message)
    if msg_len < 1 or msg_len > 1000:
        raise InputError("Invalid message length")
    
    # Checks for time_sent
    curr_time = int(time.time())
    if time_sent < curr_time:
        raise InputError("Invalid Time Sent")
    
    msg_id = 0

    def task():
        curr_time = int(time.time())
        while curr_time != time_sent:
            curr_time = int(time.time())
        else:
            global msg_id
            msg_id = message_send_v1(token, channel_id, message).get('message_id')
            
    t1 = Thread(target=task)
    
    try:
        t1.start()
        t1.join()
    except ThreadError:
        print("Thread Error")

    return {
        'message_id': msg_id
    }


def message_unpin_v1(token, message_id):
    '''
        Given a message within a channel or DM, remove its mark as pinned.

        Arguments:
            token (string) - A registered user's token
            message_id (int) - The ID of an existing message

        Exceptions:
            InputError Occurs when:
                    -> message_id is not a valid message within a channel or DM that the authorised user has joined
                    -> the message is not already pinned
            AccessError Occurs when:
                    -> message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
                    -> token does not represent a valid auth user

        Return Values:
            {}
    '''    
    
    # Given a message within a channel or DM, mark it as "unpinned".
    data = data_store.get()
    users = data['users']

    
    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invalid user") 
    
    # Traverse through this helper function, but use data store to actually modify data
    channels = channels_list_v2(token).get('channels')
    dms = dm_list_v1(token).get('dms')

    # Data store of the channels
    channels_data = data['channels']
    
    # Data store of the dms
    dms_data = data['dms']
    
    message_found = 0
    
    message_unpinned = 0
    
    for channel in channels:
        channel_messages = channels_data[channel['channel_id']]['messages']
        
        for msg in channel_messages:

            # If we loop through and found our message
            if msg['message_id'] == message_id:
                message_found = 1

            # We can remove message if user is the channel owner 
            if message_found and check_owner(auth_user_id, channels_data[channel['channel_id']]):
                if msg['is_pinned'] == False:
                    
                    raise InputError("Message already unpinned")    
                else:
                    msg['is_pinned'] = False
                    
                message_unpinned = 1
                break
        
    for dm in dms:
        dm_messages = dms_data[dm['dm_id']]['messages']
        
        for msg in dm_messages:

            if msg['message_id'] == message_id:
                message_found = 1
                
            if message_found and check_dm_owner(auth_user_id, dms_data[dm['dm_id']]):
                if msg['is_pinned'] == False:
                    raise InputError("Message already unpinned")    
                else:
                    msg['is_pinned'] = False
                    
                message_unpinned = 1
                break
        
    if message_found == 0:
        raise InputError("Message not found in users channels")
    
    elif message_unpinned == 0:
        raise AccessError("Unauthorised access to unpin message")

    data_store.set(data)
    
    return {}

def message_pin_v1(token, message_id):
    '''
        Given a message within a channel or DM, mark it as pinned.

        Arguments:
            token (string) - A registered user's token
            message_id (int) - The ID of an existing message

        Exceptions:
            InputError Occurs when:
                    -> message_id is not a valid message within a channel or DM that the authorised user has joined
                    -> the message is already pinned
            AccessError Occurs when:
                    -> message_id refers to a valid message in a joined channel/DM and the authorised user does not have owner permissions in the channel/DM
                    -> token does not represent a valid auth user

        Return Values:
            {}
    '''  
    
    # Given a message within a channel or DM, mark it as "pinned".
    data = data_store.get()
    users = data['users']

    
    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invald user") 
    
    # Traverse through this helper function, but use data store to actually modify data
    channels = channels_list_v2(token).get('channels')
    dms = dm_list_v1(token).get('dms')

    # Data store of the channels
    channels_data = data['channels']
    
    # Data store of the dms
    dms_data = data['dms']
    
    message_found = 0
    
    message_pinned = 0
    
    for channel in channels:
        channel_messages = channels_data[channel['channel_id']]['messages']
        
        for msg in channel_messages:

            # If we loop through and found our message
            if msg['message_id'] == message_id:
                message_found = 1

            # We can remove message if user is the channel owner 
            if message_found and check_owner(auth_user_id, channels_data[channel['channel_id']]):
                if msg['is_pinned'] == True:
                    #
                    raise InputError("Message already Pinned")    
                else:
                    print("hi")
                    msg['is_pinned'] = True
                    
                message_pinned = 1
                break
        
    for dm in dms:
        dm_messages = dms_data[dm['dm_id']]['messages']
        
        for msg in dm_messages:

            if msg['message_id'] == message_id:
                message_found = 1
                
            if message_found and check_dm_owner(auth_user_id, dms_data[dm['dm_id']]):
                if msg['is_pinned'] == True:
                    raise InputError("Message already Pinned")    
                else:
                    msg['is_pinned'] = True
                    
                message_pinned = 1
                break
        
    if message_found == 0:
        raise InputError("Message not found in users channels")
    
    elif message_pinned == 0:
        raise AccessError("Unauthorised access to pin message")

    data_store.set(data)
    
    return {}



def message_react_v1(token, message_id, react_id):
    
    '''
        Given a message within a channel or DM, react to it.

        Arguments:
            token (string) - A registered user's token
            message_id (int) - The ID of an existing message
            react_id (int) - The ID of a react

        Exceptions:
            InputError Occurs when:
                    -> message_id is not a valid message within a channel or DM that the authorised user has joined
                    -> react_id is not a valid react ID
                    -> the message already contains a react with ID react_id from the authorised user
            AccessError Occurs when:
                    -> token does not represent a valid auth user

        Return Values:
            {}
    '''  
    
    if react_id not in [1]:
        raise InputError("React id not valid")
        
    data = data_store.get()
    users = data['users']

    
    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invald user") 
    
    # Traverse through this helper function, but use data store to actually modify data
    channels = channels_list_v2(token).get('channels')
    dms = dm_list_v1(token).get('dms')

    # Data store of the channels
    channels_data = data['channels']
    
    # Data store of the dms
    dms_data = data['dms']
    
    message_found = 0
    
    message_reacted = 0
    
    reacts = []
    
    
    
    for channel in channels:
        channel_messages = channels_data[channel['channel_id']]['messages']
        
        for msg in channel_messages:

            # If we loop through and found our message
            if msg['message_id'] == message_id:
                message_found = 1
                reacts = msg['reacts']
                
                # Check if the react id is already contained in the list
                # if not then create a new dictionary for the react id and insert into list
                
                for react in reacts:
                    
                    # If reactid already exists then we can just append the user
                    if react['react_id'] == react_id:
                        
                        # Check if user hasn't already reacted to the message
                        if auth_user_id in react['u_ids']:
                            raise InputError("User already reacted to message")
                        
                        react['u_ids'].append(auth_user_id)
                        react['is_this_user_reacted'] = True
                        message_reacted = 1
                        
                if message_reacted == 0:
                    # create a new dictionary and append
                    react_dict = {'react_id': react_id,
                                'u_ids': [auth_user_id],
                                'is_this_user_reacted': True,
                                }
                    reacts.append(react_dict)
                    message_reacted = 1
        
            if message_reacted:
                break
                
    for dm in dms:
        dm_messages = dms_data[dm['dm_id']]['messages']
        
        for msg in dm_messages:
            
            if msg['message_id'] == message_id:
                message_found = 1
                reacts = msg['reacts']
                
                # Check if the react id is already contained in the list
                # if not then create a new dictionary for the react id and insert into list
                
                for react in reacts:
                    
                    # If reactid already exists then we can just append the user
                    if react['react_id'] == react_id:
                        
                        # Check if user hasn't already reacted to the message
                        if auth_user_id in react['u_ids']:
                            raise InputError("User already reacted to message")
                        
                        react['u_ids'].append(auth_user_id)
                        react['is_this_user_reacted'] = True
                        message_reacted = 1
                        
                if message_reacted == 0:
                    # create a new dictionary and append
                    react_dict = {'react_id': react_id,
                                'u_ids': [auth_user_id],
                                'is_this_user_reacted': True,
                                }
                    reacts.append(react_dict)
                    message_reacted = 1
                
            if message_reacted:
                break
            
            
                    
    if message_found == 0:
        raise InputError("Message not found in users channels/dms")
    
    elif message_reacted == 0:
        raise AccessError("Unauthorised access to react to message")

    # Notifies user msg
    reacted_notification(auth_user_id, message_id)
                    
    data_store.set(data)
    
    return {} 


def message_unreact_v1(token, message_id, react_id):
    '''
        Given a message within a channel or DM, react to it.

        Arguments:
            token (string) - A registered user's token
            message_id (int) - The ID of an existing message
            react_id (int) - The ID of a react

        Exceptions:
            InputError Occurs when:
                    -> message_id is not a valid message within a channel or DM that the authorised user has joined
                    -> react_id is not a valid react ID
                    -> the message already contains a react with ID react_id from the authorised user
            AccessError Occurs when:
                    -> token does not represent a valid auth user

        Return Values:
            {}
    '''      
    
    # Traversing through the messages to find the message id
    
    if react_id not in [1]:
        raise InputError("React id not valid")
        
    data = data_store.get()
    users = data['users']

    
    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invald user") 
    
    # Traverse through this helper function, but use data store to actually modify data
    channels = channels_list_v2(token).get('channels')
    dms = dm_list_v1(token).get('dms')

    # Data store of the channels
    channels_data = data['channels']
    
    # Data store of the dms
    dms_data = data['dms']
    
    message_found = 0
    
    message_unreacted = 0
    
    reacts = []
    
    for channel in channels:
        channel_messages = channels_data[channel['channel_id']]['messages']
        
        for msg in channel_messages:

            # If we loop through and found our message
            if msg['message_id'] == message_id:
                message_found = 1
                reacts = msg['reacts']
                
                
            for react in reacts:
                
                if react['react_id'] == react_id:
                    
                    # Check if user already reacted to the message
                    if auth_user_id not in react['u_ids']:
                        raise InputError("User hasn't reacted to message with given react_id")
                    
                    # remove the user from the reacts
                    react['u_ids'].remove(auth_user_id)
                    react['is_this_user_reacted'] = False
                    message_unreacted = 1
                    
            if message_unreacted:
                break
            
                
    for dm in dms:
        dm_messages = dms_data[dm['dm_id']]['messages']
        
        for msg in dm_messages:
            
            if msg['message_id'] == message_id:
                message_found = 1
                reacts = msg['reacts']
                
                # Check if the react id is already contained in the list
                # if not then create a new dictionary for the react id and insert into list
                
            for react in reacts:
                
                # If reactid already exists then we can just append the user
                if react['react_id'] == react_id:
                    
                    # Check if user already reacted to the message
                    if auth_user_id not in react['u_ids']:
                        raise InputError("User hasn't reacted to message with given react_id")
                    
                    # removing user from reacts
                    react['u_ids'].remove(auth_user_id)
                    react['is_this_user_reacted'] = False
                    message_unreacted = 1
                    
            if message_unreacted:
                break
            
            
                    
    if message_found == 0:
        raise InputError("Message not found in users channels/dms")
    
    elif message_unreacted == 0:
        raise InputError("User never reacted with given react id")
                    
    data_store.set(data)

    return {} 
    

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
        Shares an existing message with a message id to an existing channel (if dm_id is -1) or dm (if channel_id is -1) with an optional message attached.

        Arguments:
            token (string) - A registered user's token
            og_message_id (int) - ID of the original message
            message (string) - Optional message in addition to the shared message
            channel_id (int) - The ID of an existing channel
            dm_id (int) - The ID of an existing dm

        Exceptions:
            InputError occurs when:
                    -> both channel_id and dm_id are invalid
                    -> neither channel_id nor dm_id are -1
                    -> og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
                    -> length of message is more than 1000 characters
            AccessError occurs when:
                    -> the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the 
                       authorised user has not joined the channel or DM they are trying to share the message to
        Return Values:
            { shared_message_id } - a unique id for each message that is shared/sent
    '''

    store = data_store.get()
    auth_user_id = get_id_from_token(token)
    
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid User")
    
    if channel_id == -1 and dm_id == -1:
        raise InputError("Invalid input")
    
    if channel_id != -1 and dm_id != -1:
        raise InputError("Neither channel_id or dm_id were -1")

    if len(message) > 1000:
        raise InputError("Message length needs to be under 1000 characters")

    channels = channels_list_v2(token).get('channels')
    dms = dm_list_v1(token).get('dms')


    channels_data = store['channels']
    dms_data = store['dms']
    channelsID = channels_data.get(channel_id)
    dmsID = dms_data.get(dm_id)
    
    message_found = 0
    shared_message = ""
    for channel in channels:
        channel_messages = channels_data[channel['channel_id']]['messages']
        for msg in channel_messages:
            if msg['message_id'] == og_message_id:
                message_found = 1
            if message_found:
                shared_message = message + msg['message']
                break
     
    for dm in dms:
        dm_messages = dms_data[dm['dm_id']]['messages']
        for msg in dm_messages:
            if msg['message_id'] == og_message_id:
                message_found = 1
                shared_message = message + msg['message']
                break
            else:
                message_found = 0

    if message_found == 0:
        raise InputError("Message not found")

    if dm_id == -1:
        if channel_id != -1 and channel_id not in store['channels']:
            raise InputError("Invalid Channel ID")
        if auth_user_id not in channelsID['all_members']:
            raise AccessError("Authorised User Only")
        shared_message_id = message_send_v1(token, channel_id, shared_message).get('message_id')
    if channel_id == -1:
        if dm_id != -1 and dm_id not in store['dms']:
            raise InputError("Invalid DM ID")
        if auth_user_id not in dmsID['members']:
            raise AccessError("Authorised User Only")
        shared_message_id = message_send_dm_v1(token, dm_id, shared_message).get('message_id')

    data_store.set(store)
    
    return {
        'shared_message_id': shared_message_id
    }
    
def search_v1(token, query_str):
    '''
        Searches all messages user is a part of for a given string, and returns a list of all the messages that
        contain said string.

        Arguments:
            token (string)      - A registered user's token
            query_str (string)  - A keyword to be looked for.

        Exceptions:
            InputError occurs when:
                    -> length of query_str exceeds 1000
            AccessError occurs when:
                    -> token is invalid

        Return Values:
            { messages } - a dictionary containing a list 'messages' of all the messages containing the query_str in channels
                           that the user is a part of.
    '''

    length = len(str(query_str))
    if length < 1 or length > 1000:
        raise InputError("Invalid Query")

    data = data_store.get()
    channels = data["channels"]
    dms = data["dms"]

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    result = { 'messages': []}
    
    for channel in channels:
        c = channels.get(channel)
        members = c.get('all_members')
        if auth_user_id in members:
            messages = c.get('messages')
            for post in messages:
                msg = post['message']
                if query_str in msg:
                    result['messages'].append(post)

    for dm in dms:
        d = dms.get(dm)
        members = d.get('members')
        if auth_user_id in members:
            messages = d.get('messages')
            for dm_message in messages:
                msg = dm_message['message']
                if query_str in msg:
                    result['messages'].append(dm_message)

    return result

def message_send_v1(token, channel_id, message):

    '''
        Sends a message from the authorised user (token) to the channel specified by channel_id.

        Arguments:
            token (string) - A registered user's token
            channel_id (int) - The ID of an existing channel
            message (string) - a message that is associated with a valid channel_id

        Exceptions:
            InputError Occurs when:
                    -> channel_id does not refer to a valid channel
                    -> length of message is less than 1 or over 1000 characters
            AccessError Occurs when:
                    -> channel_id is valid and the authorised user is not a member of the channel

        Return Values:
            { message_id } - a unique id for each message that is sent
    '''

    data = data_store.get()

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if not check_user_id(auth_user_id):
        raise AccessError("Invald user")

    # Checks for input error - valid channel_id
    if channel_id not in data['channels']:
        raise InputError("Invalid Channel ID")

    msg_len = len(message)
    if msg_len < 1 or msg_len > 1000:
        raise InputError("Invalid Messages")

    # Gets the list of all members in the channel
    channel = data['channels'].get(channel_id)
    all_members = channel.get('all_members')

    # Checks if user is not a member of channel
    if auth_user_id not in all_members:
        raise AccessError("Invalid Auth User")

    # Checks for any tagged user/s
    if '@' in message:
        channel = data['channels'].get(channel_id)
        chan_name = channel.get('name')
        tagging(auth_user_id, channel_id, -1, chan_name, message)

    # Pet Bot features
    pet_bot.activate_pet_bot(channel_id, message)
    
    if pet_bot.check_pet_bot_active(channel_id):
        message = pet_bot.main_game(auth_user_id, channel_id, message)

    message_id = unique_msg_id.get()
    u_id = auth_user_id

    # Getting the current time
    time_created = int(time.time())

    new_message = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_sent': time_created,
        'reacts': [],
        'is_pinned': False,
    }

    messages = channel.get('messages')

    messages.append(new_message)
    
    data_store.set(data)

    return {
        'message_id': message_id,
    }

def message_send_dm_v1(token, dm_id, message):

    '''
        Sends a message from authorised_user (token) to the DM specified by dm_id.

        Arguments:
            token (string) - A registered user's token
            dm_id (int) - The ID of an existing DM
            message (string) - a message that is associated with a valid dm_id

        Exceptions:
            InputError occurs when:
                    -> dm_id does not refer to a valid DM
                    -> length of message is less than 1 or over 1000 characters
            AccessError occurs when:
                    -> dm_id is valid and the authorised user is not a member of the DM

        Return Values:
            { message_id } - a unique id for each message that is sent
    '''

    data = data_store.get()
    users = data['users']

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invald user")

    dms = data['dms']
    if dm_id not in dms:
        raise InputError("Invalid dms")

    msg_len = len(message)
    if msg_len < 1 or msg_len > 1000:
        raise InputError("Invalid Messages")
    
    curr_dm = dms.get(dm_id)
    u_ids = curr_dm.get('members')

    if auth_user_id not in u_ids:
        raise AccessError('User ID not a member of DM')
    
    # Checks for any tagged user/s
    if '@' in message:
        dm = data['dms'].get(dm_id)
        dm_name = dm.get('name')
        tagging(auth_user_id, -1, dm_id, dm_name, message)

    message_id = unique_msg_id.get()
    u_id = auth_user_id

    # Getting the current time
    time_created = int(time.time())

    new_message = {
        'message_id': message_id,
        'u_id': u_id,
        'message': message,
        'time_sent': time_created,
        'reacts': [],
        'is_pinned': False,
    }

    messages = curr_dm.get('messages')

    messages.append(new_message)

    data_store.set(data)

    return {
        'message_id': message_id,
    }

def message_edit_v1(token, message_id, message):

    '''
        Given a message, update its text with new text. If the new message is an empty string, the message is deleted.

        Arguments:
            token (string) - A registered user's token
            message_id (int) - The ID of an existing DM
            message (string) - message associated with message_id

        Exceptions:
            InputError occurs when:
                    -> length of message is less than 1 or over 1000 characters
                    -> message_id does not refer to a valid message within a channel/DM that the authorised user has joined
            AccessError occurs when message_id refers to a valid message in a joined channel/DM and none of the following are true:
                    -> the message was sent by the authorised user
                    -> the authorised user has owner permissions in the channel/DM

        Return Values:
            {} 
    '''


    # Traverse throught the messages list until we find out message id - implement as an helper functions
    # Just given a message id and token, so have no access to which channel
    # We can go through the users channels tho, still might be expensive to search through but at least a bit quicker
    data = data_store.get()
    users = data['users']

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    if auth_user_id not in users:
        raise AccessError("Invald user") 

    msg_len = len(message)
    if msg_len > 1000:
        raise InputError("Invalid Messages")

    message_edited = 0
    message_found = 0
    
    if message == "":
        message_remove_v1(token, message_id)
        return {}

    # Traverse through this helper function, but use data store to actually modify data
    channels = channels_list_v2(token).get('channels')
    dms = dm_list_v1(token).get('dms')

    # Data store of the channels
    channels_data = data['channels']
    
    # Data store of the dms
    dms_data = data['dms']

    for channel in channels:
        channel_messages = channels_data[channel['channel_id']]['messages']
        
        for msg in channel_messages:

            # If we loop through and found our message
            if msg['message_id'] == message_id:
                message_found = 1

            # We can edit message if user is the sender and or a global owner
            if message_found and check_message_sender(auth_user_id, msg):
                msg['message'] = message
                message_edited = 1
                break

            # We can remove message if user is the channel owner 
            elif message_found and check_owner(auth_user_id, channels_data[channel['channel_id']]):
                msg['message'] = message
                message_edited = 1
                break
    
    for dm in dms:
        dm_messages = dms_data[dm['dm_id']]['messages']
        
        for msg in dm_messages:
            print(message_id)
            print(msg)
            if msg['message_id'] == message_id:
                message_found = 1
                
            
            if message_found and check_message_sender(auth_user_id, msg):
                msg['message'] = message
                message_edited = 1
                break
            
            elif message_found and check_dm_owner(auth_user_id, dms_data[dm['dm_id']]):
                msg['message'] = message
                message_edited = 1
                break
            
    if message_found == False:
        raise InputError("Message not found in users channels")

    elif message_edited == False:
        raise AccessError("Unauthorised access to edit message")

    data_store.set(data)

    return {}

def message_remove_v1(token, message_id):

    '''
        Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.

        Arguments:
            token (string) - A registered user's token
            dm_id (int) - The ID of an existing DM

        Exceptions:
            InputError occurs when:
                    -> dm_id does not refer to a valid DM
            AccessError occurs when:
                    -> dm_id is valid and the authorised user is not the original DM creator
                    -> dm_id is valid and the authorised user is no longer in the DM

        Return Values:
            {} 
    '''

    data = data_store.get()
    users = data['users']
    print(token)

    # Gets the user id from token
    auth_user_id = get_id_from_token(token)

    # Checks if auth user id exists
    
    print(auth_user_id)
    if auth_user_id not in users:
        raise AccessError("Invalid user") 

    message_removed = 0
    message_found = 0

    # Traverse through this helper function, but use data store to actually modify data
    channels = channels_list_v2(token).get('channels')
    dms = dm_list_v1(token).get('dms')

    # Data store of the channels
    channels_data = data['channels']
    
    # Data store of the dms
    dms_data = data['dms']
    
    for channel in channels:
        channel_messages = channels_data[channel['channel_id']]['messages']
        for msg in channel_messages:

            # If we loop through and found our message
            if msg['message_id'] == message_id:
                message_found = 1

            
            # We can remove message if user is the sender
            if message_found and check_message_sender(auth_user_id, msg):
                channel_messages.remove(msg)
                message_removed = 1
                break

            # We can remove message if user is the channel owner
            elif message_found and check_owner(auth_user_id, channels_data[channel['channel_id']]):
                channel_messages.remove(msg)
                message_removed = 1
                break
            
    for dm in dms:
        dm_messages = dms_data[dm['dm_id']]['messages']
        print(dm_messages)
        
        for msg in dm_messages:
            print(message_id)
            print(msg)
            if msg['message_id'] == message_id:
                message_found = 1
                
            print(message_found)
            
            if message_found and check_message_sender(auth_user_id, msg):
                dm_messages.remove(msg)
                message_removed = 1
                break
            
            elif message_found and check_dm_owner(auth_user_id, dms_data[dm['dm_id']]):
                dm_messages.remove(msg)
                message_removed = 1
                break
                
            
    if message_found == False:
        raise InputError("Message not found in users channels")

    elif message_removed == False:
        raise AccessError("Unauthorised access to remove message")

    data_store.set(data)

    return {}
