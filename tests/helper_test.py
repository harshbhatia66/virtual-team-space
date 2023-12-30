def delete_empty_string(channel_messages, msg, message):
    """
    Deletes empty string messages

    Args:
        channel_messages (list): Contains a list of dictionary of all messages in a dm/channel
        msg (dict): contains details of a particular message 
        message (string): contains the string message
    """

    if message == "":
        channel_messages.remove(msg)
    

def check_user_is_channel_member(all_members, u_id):
    """
    Checks if user is a member of a channel

    Args:
        all_members (list): A list of u_id/s of members in a channel
        u_id (int): A unique user id

    Returns:
        Bool: Returns true if user exists in the list. Returns false if not.
    """

    status = False

    for member in all_members:
        if member['u_id'] == u_id:
            status = True
            break
    return status

def check_user_is_channel_owner(owner_members, u_id):
    """
    Checks if user is an owner of a channel

    Args:
        all_members (list): A list of u_id/s of owners in a channel
        u_id (int): A unique user id

    Returns:
        Bool: Returns true if user exists in the list. Returns false if not.
    """

    status = False

    for member in owner_members:
        if member['u_id'] == u_id:
            status = True
            break
    return status