from src.data_store import data_store
from src.error import AccessError
from src.other import get_id_from_token, check_user_id

def notifications_get_v1(token):

    '''
        Return the user's most recent 20 notifications, ordered from most recent to least recent.
        
        Arguments:
            token (string) - A registered user's token

        Return Values:
            { notifications }
        
            A list of dictionaries, where each dictionary contains types
                    { 
                        channel_id,
                        dm_id,
                        notification_message
                    } 
                where channel_id is the id of the channel that the event happened in
                and is -1 if it is being sent to a DM. dm_id is the DM that the event
                happened in, and is -1 if it is being sent to a channel.
                Notification_message is a string of the following format for each
                trigger action:
                    -> tagged: "{Users handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
                    -> reacted message: "{Users handle} reacted to your message in {channel/DM name}"
                    -> added to a channel/DM: "{Users handle} added you to {channel/DM name}"
    '''

    data = data_store.get()

    auth_user_id = get_id_from_token(token)

    if not check_user_id(auth_user_id):
        raise AccessError("Invalid User")
    
    user = data['users'].get(auth_user_id)

    notifications = user.get('notifications')
    
    notifications.reverse()
    
    print(notifications)

    return {
        'notifications': notifications,
    }

def create_notification(auth_user_id, channel_id, dm_id, notification_message):
    '''
        Creates a notification with the given parameters.

        Arguments:
            auth_user_id            - A registered user's token
            channel_id              - The ID of an existing channel
            dm_id                   - a message that is associated with a valid channel_id
            notification_message    - message describing what the notification was for.

        Return Values:
            {}
    '''
    data = data_store.get()
    user = data['users'].get(auth_user_id)

    notification = {
        'channel_id': channel_id,
        'dm_id': dm_id,
        'notification_message': notification_message,
    }

    user['notifications'].append(notification)

    data_store.set(data)

def get_u_id_from_user_handle(handle_str) -> int:
    """
    Gets u id from a user handle

    Args:
        handle_str (string): a user handle

    Returns:
        u_id (int) : authorise user id
    """
    data = data_store.get()
    users = data['users']
    u_id = None
    
    u_id = [u['u_id'] for u in users.values() if u['handle_str'] == handle_str]

    if len(u_id) == 0:
        u_id = None
    else:
        u_id = u_id[0]

    return u_id

def tagging(auth_user_id, channel_id, dm_id, name, message):
    """
    Parses a message with an @ symbol to identify tagged users

    Args:
        auth_user_id (int): authorised user id
        channel_id (int): channel id
        dm_id (int): dm id
        name (string): channel/dm name
        message (string): user message
    """
    handle_strs = []
    msg = message
    msg = msg.split(" ")

    msg = [m[m.find("@"):] for m in msg if '@' in m]

    if len(msg) > 0:
        msg = ''.join(msg)
        handle_strs = msg[1:].split("@")

    handle_strs = list(dict.fromkeys(handle_strs))

    if len(handle_strs) == 0:
        return
    
    u_ids = []

    for handle in handle_strs:
        u_id = get_u_id_from_user_handle(handle)
        if u_id != None:
            u_ids.append(u_id)
    
    for u_id in u_ids:
        if check_user_active_member(u_id, channel_id, dm_id):
            tagged_user_notification(auth_user_id, u_id, channel_id, dm_id, name, message)

# TODO: Tagging notifications
def tagged_user_notification(auth_user_id, u_id, channel_id, dm_id, name, msg):
    """
    Creates a notification for a tagged user

    Args:
        auth_user_id (int): authorised user id
        u_id (int) : specified authorised user id
        channel_id (int): channel id
        dm_id (int): dm id
        name (string): channel/dm name
        message (string): user message
    """
    data = data_store.get()
    users = data['users']
    user_1 = users.get(auth_user_id)

    user_1_handle = user_1.get('handle_str')

    notification_msg = f"{user_1_handle} tagged you in {name}: {msg[:20]}"

    create_notification(u_id, channel_id, dm_id, notification_msg)

def get_ids_from_msg_id(msg_id):
    """
    Gets all the needed id from a message id

    Args:
        msg_id (int): unique message id

    Returns:
        ids (tuple) : returns the user id, channel id/dm id
    """
    data = data_store.get()
    channels = data['channels']
    dms = data['dms']

    chan_id = -1
    dm_id = -1
    u_id = None
    for chan in channels.values():
        for msg in chan['messages']:
            if msg['message_id'] == msg_id:
                chan_id = chan.get('channel_id')
                u_id = msg.get('u_id')
                break

    if chan_id != -1:
        return (u_id, chan_id, dm_id)

    for dm in dms.values():
        for msg in dm['messages']:
            if msg['message_id'] == msg_id:
                dm_id = dm.get('dm_id')
                u_id = msg.get('u_id')
                break

    return (u_id, chan_id, dm_id)

# Checks if user is a member
def check_user_active_member(u_id, channel_id, dm_id):
    """
    Checks if user is active

    Args:
        u_id (int): authorised user id
        channel_id (int): channel id
        dm_id (int): dm id

    Returns:
        bool : returns true if user is an active member of a specified channel/dm
    """
    data = data_store.get()
    
    status = False

    if channel_id != -1:
        channel = data['channels'].get(channel_id)
        members = channel.get('all_members')
        if u_id in members:
            status = True
    else:
        dm = data['dms'].get(dm_id)
        members = dm.get('members')
        if u_id in members:
            status = True

    return status

# TODO: Reacted
def reacted_notification(auth_user_id, msg_id):
    """
    creates a react notification

    Args:
        auth_user_id (int): authorised user
        msg_id (int): specific message 
    """
    data = data_store.get()
    users = data['users']
    user_1 = users.get(auth_user_id)
    user_1_handle = user_1.get('handle_str')

    u_id, channel_id, dm_id = get_ids_from_msg_id(msg_id)

    if not check_user_active_member(u_id, channel_id, dm_id):
        return

    # Gets the Channel/DM name
    name = ""
    if channel_id != -1:
        name = data['channels'].get(channel_id).get('name')
    else:
        name = data['dms'].get(dm_id).get('name')

    notification_msg = f"{user_1_handle} reacted to your message in {name}"

    create_notification(u_id, channel_id, dm_id, notification_msg)

# TODO: Channel/DM added
def invited_notification(auth_user_id=-1, u_id=-1, channel_id=-1, dm_id=-1, name=""):
    """
    Creates a notification for when a user gets invited or added to a channel/dm

    Args:
        auth_user_id (int, optional): authorised user. Defaults to -1.
        u_id (int, optional): authorised user. Defaults to -1.
        channel_id (int, optional): channel id. Defaults to -1.
        dm_id (int, optional): dm id. Defaults to -1.
        name (str, optional): channel/dm name. Defaults to "".
    """
    data = data_store.get()
    users = data['users']
    user_1 = users.get(auth_user_id)
    user_1_handle = user_1.get('handle_str')

    notification_msg = f"{user_1_handle} added you to {name}"

    create_notification(u_id, channel_id, dm_id, notification_msg)