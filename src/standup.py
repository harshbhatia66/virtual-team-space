from http.client import LENGTH_REQUIRED
from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import get_id_from_token, check_user_id
from threading import Thread, ThreadError
from src.message import message_send_v1
import time

def standup_send_v1(token, channel_id, message):
    '''
        Sending a message to get buffered in the standup queue, assuming a standup
        is currently active. @ tags are not parsed as proper tags when
        sending to standup/send.

        Arguments:
            token (string)      - A registered user's token
            channel_id (int)    - The Channel ID for the standup to be started in
            message (string)    - The message to be sent in the standup.

        Exceptions:
            InputError occurs when:
                    -> channel_id does not refer to a valid channel
                    -> length of message is over 1000 characters
                    -> an active standup is not currently running in the channel
            AccessError occurs when:
                    -> token is invalid
                    -> channel_id is valid and the authorised user is not a member of the channel

        Return Values:
           {}
    '''  

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

    status = standup_active_v1(token, channel_id)
    if status['is_active'] == False:
        raise InputError("No Standups Active in Channel")
    
    #If everything is as it should be, add it to the list of messages in the standup.
    users = data['users']
    standups = data['standups']

    msg_to_send = users[auth_user_id]['handle_str'] + ": " + message + "\n"
    standups[channel_id]['queue'].append(msg_to_send)

    data_store.set(data)
    
    return {}


def standup_active_v1(token, channel_id):

    '''
        Starts a standup in the given channel, that lasts a given length. 
        During this time, all messages sent to this channel will instead 
        be buffered through a standup queue to be sent at the end of the
        standup in one message from the person who started it.

        Arguments:
            token (string)      - A registered user's token
            channel_id (int)    - The Channel ID for the standup to be started in

        Exceptions:
            InputError occurs when:
                    -> channel_id does not refer to a valid channel
                    -> length is a negative integer
                    -> an active standup is already running in the channel
            AccessError occurs when:
                    -> token is invalid
                    -> channel_id is valid and the authorised user is not a member of the channel

        Return Values:
           { is_active } - if channel has an active standup
           { time_finish } - the time that the standup is set to finish.
    '''  

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
    
    standups = data['standups']

    if channel_id in standups:
        return {
        'is_active': True,
        'time_finish': standups[channel_id]['time_finish'],
        }
    
    else:
        return {
            'is_active': False,
            'time_finish': None
        }

    
def standup_start_v1(token, channel_id, length):
    '''
        Starts a standup in the given channel, that lasts a given length. 
        During this time, all messages sent to this channel will instead 
        be buffered through a standup queue to be sent at the end of the
        standup in one message from the person who started it.

        Arguments:
            token (string)      - A registered user's token
            channel_id (int)    - The Channel ID for the standup to be started in
            length (int)        - Amount of seconds the standup will last for.

        Exceptions:
            InputError occurs when:
                    -> channel_id does not refer to a valid channel
                    -> length is a negative integer
                    -> an active standup is currently running in the channel
            AccessError occurs when:
                    -> token is invalid
                    -> channel_id is valid and the authorised user is not a member of the channel

        Return Values:
           { time_finish } - the time that the standup is set to finish.
    '''    
    
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
    
    # Checks if length is valid
    if length < 0:
        raise InputError("Invalid standup length")

    status = standup_active_v1(token, channel_id)
    if status['is_active'] == True:
        raise InputError("Standup already active")

    # Getting the current time
    current_time = int(time.time())
    time_finish = current_time + length

    new_standup = {
        channel_id: {
            'time_finish': time_finish,
            'channel': channel_id,
            'started_by': auth_user_id,
            'queue': []
            }
    }
    
    data['standups'].update(new_standup)
    data_store.set(data)

    def task():
        curr_time = int(time.time())
        while curr_time != time_finish:
            curr_time = int(time.time())
        else:
            final_message = ""
            msg_queue = data['standups'][channel_id].get('queue')
            for message in msg_queue:
                final_message = final_message + message

            if final_message != "":
                message_send_v1(token, channel_id, final_message)

            data['standups'].pop(channel_id)
            
    t1 = Thread(target=task)
    
    try:
        t1.start()
    except ThreadError:
        print("Thread Error")

    return {
        'time_finish': time_finish,
    }