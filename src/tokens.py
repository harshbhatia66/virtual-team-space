import hashlib
import jwt
import os.path
import pickle

'''
----------------------------------------------------
                    Password Hashing
----------------------------------------------------
'''

def hash(input_string):
    """Hashes the input string with sha256

    Args:
        input_string ([string]): The input string to hash

    Returns:
        string: The hexidigest of the encoded string
    """
    return hashlib.sha256(input_string.encode()).hexdigest()

'''
----------------------------------------------------
                    Token Creation
----------------------------------------------------
'''

SESSION_TRACKER = 0
SECRET = 'ANT'

# Checks local database for latest data if exist
if os.path.exists('database/session_tracker.p'):
    SESSION_TRACKER = pickle.load(open('database/session_tracker.p', 'rb'))

def generate_new_session_id():
    """Generates a new sequential session ID

    Returns:
        number: The next session ID
    """
    global SESSION_TRACKER

    SESSION_TRACKER += 1

    # Saves currect session id to local save file
    with open('database/session_tracker.p', 'wb') as FILE:
            pickle.dump(SESSION_TRACKER, FILE)

    return SESSION_TRACKER

def reset_session_id():
    global SESSION_TRACKER
    SESSION_TRACKER = 0
    # Saves currect session id to local save file
    with open('database/session_tracker.p', 'wb') as FILE:
            pickle.dump(SESSION_TRACKER, FILE)


def generate_jwt(auth_user_id, session_id=None):
    """Generates a JWT using the global SECRET

    Args:
        auth_user_id ([auth_user_id]): The user's specific user id
        handle_str ([string]): The users' unique combined first and last name
        session_id ([string], optional): The session id, if none is provided will
                                         generate a new one. Defaults to None.

    Returns:
        string: A JWT encoded string
    """
    if session_id is None:
        session_id = generate_new_session_id()
    return jwt.encode({'auth_user_id': auth_user_id, 'session_id': session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
    """Decodes a JWT string into an object of the data

    Args:
        encoded_jwt ([string]): The encoded JWT as a string

    Returns:
        Object: An object storing the body of the JWT encoded string
    """
    return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
