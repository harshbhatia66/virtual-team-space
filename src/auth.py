from ast import In
from cgitb import reset
import re
import smtplib, ssl

import src.tokens as Token
import src.admin as Admin
from src.data_store import data_store
from src.other import get_id_from_token, check_user_id, random_code
from src.unique_id import unique_auth_id
from src.error import InputError, AccessError


# First User ID
FIRST_USER_ID = 1001
N = 8

def auth_passwordreset_reset_v1(reset_code, new_password):
    '''
        Given a reset code for a user, set that user's new password to the password provided.

        Arguments:
            reset_code (string) - A random string containing eight letters/numbers
            new_password (string) - New password that is updated in the data store

        Exceptions:
            N/A

        Return Values:
            {}
    '''

    store = data_store.get()
    users = store['users']
    curr_user = None
    if len(new_password) < 6:
        raise InputError("Password is less than 6 characters long")
    for user in users.values():
        if reset_code == user.get('reset_code'):
            curr_user = user
            break 

    if curr_user == None:  
        raise InputError("Invalid reset code")
    
    curr_user.update({'password': Token.hash(new_password)})
    curr_user.pop('reset_code')
    print(curr_user)
    data_store.set(store)

def auth_passwordreset_request_v1(email):
    '''
        Sends an email containing a reset code for when a user forgets their password.

        Arguments:
            email (string) - A registered authorised user's email

        Exceptions:
            N/A

        Return Values:
            {}
    '''

    store = data_store.get()
    users = store['users']
    for user in users.values():
        if user['email'] == email:
            reset_code = random_code(N)
            sender_email = "T17BANT@gmail.com"
            sender_password = "COMP1531"
            receiver_email = email
            port = 465
            message = f"""\
            Subject: Password Reset Request\n
            
            Hi There!, \n
            Here is the requested password reset code.
            \n

            {reset_code}

            \n
            Kind regards,\n
            T17BANT Seams :)\n
            """
            
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, message)

            print(user)
            user.update({"reset_code": reset_code})
            data_store.set(store)
            
            return

def auth_logout_v1(token):

    '''
    Given an active token, invalidates the token to log the user out.

    Arguements:
        token (string) - authorisation hash

    Exceptions:
        N/A

    Return values:
        {}
    '''
    

    store = data_store.get()
    auth_user_id = get_id_from_token(token)
    if not check_user_id(auth_user_id):
        raise AccessError("Invalid User ID")
    
    user = store['users'].get(auth_user_id)
    
    encoded_jwt = Token.decode_jwt(token)
    session_id = encoded_jwt['session_id']
    lst = user.get('session_list')
    lst.remove(session_id)

    data_store.set(store)

def auth_login_v2(email, password):
    '''
    Given a registered user's email and password, returns their `auth_user_id` value.

    Arguements:
        email (string) - user email address
        password (string) - user password used on register

    Exceptions:
        InputError - Occurs when:
                        -> email does not belong to a user
                        -> password is incorrect

    Return values:
        Return <auth_user_id> (int) - the authorised user id of the given email
        Return <token> (string) - authorisation hash
    '''
    
    store = data_store.get()
    curr_pass = Token.hash(password)
    for user in store['users'].values():
        # Check if login is valid
        if user['email'] == email:
            print(user['password'], curr_pass)
            if user.get('password') == curr_pass:
                # Gets all the user details for jwt payload
                auth_user_id = user['u_id']
                session_list = user['session_list']

                new_session_id = Token.generate_new_session_id()
                session_list.append(new_session_id)

                new_token = Token.generate_jwt(auth_user_id, new_session_id)

                return {
                    'token': new_token,
                    'auth_user_id': auth_user_id,
                }
            else:
                # Invalid password
                raise InputError("Invalid Password")
    # Invalid email
    raise InputError("Invalid Email")

def auth_register_v2(email, password, name_first, name_last):
    '''
    auth_register_v2() creates a new account for a user given a following set of user info.
    Additionally function generates a handle from the concatentation of the first and last name

    Arguments:
        email (string) - a valid user email address with the proper characters
        password (string) - a valid unique password with more than 6 characters
        name_first (string) - user first name
        name_last (string) - user last name

    Exceptions:
        InputError - Occurs when:
                        -> email is not a valid email
                        -> email address already being used
                        -> length of password is less than 6 characters
                        -> length of name_first and name_last is not between 1 to 50

    Return Values:
        Returns <auth_user_id> if all user details are unique
        Returns <token> if user details are valid
    '''

    store = data_store.get()

    # Checks for Invalid Email Inputs
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(regex, email):
        raise InputError("Invalid email")
        

    # Checks for Invalid Password
    if len(password) < 6:
        raise InputError("Invalid pasword")

    # Checks for invalid name
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("Invalid name")

    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Invalid name")

    # Checks for duplicate emails
    for user in store['users'].values():
        if user['email'] == email:
            raise InputError("Email duplicate")

    # Creates user handle
    handle_str = (name_first + name_last).lower()

    # Checks if user handle exceed 20 characters
    if len(handle_str) > 20:
        handle_str = handle_str[:20]

    # Checks if user handles exists and other taken handles
    same_handle = 0
    for user in store['users'].values():
        if handle_str == user['handle_str'][:20]:
            same_handle += 1

    # Checks if same_handle has values in it showing theres repeated handles
    if same_handle > 0:
        # concatenate the new unique handle_str with the amount of same handles
        handle_str += str(same_handle)

    # Creates a new account
    new_id = unique_auth_id.get()

    # Initilises a new session list to validify tokens
    session_id = Token.generate_new_session_id()

    # Creates a new token
    new_token = Token.generate_jwt(new_id, session_id)
    
    # Hashes the password
    new_password = Token.hash(password)

    # Initialises user as a normal member who do not have any owner's permissions
    permission_id = Admin.MEMBER

    # If new user is the very first user registered
    if new_id == FIRST_USER_ID:
        permission_id = Admin.OWNER

    # Initialises the data structure for the account into a dictionary
    new_account = {
        new_id: {
            'u_id': new_id,
            'email': email,
            'password': new_password,
            'name_first': name_first,
            'name_last': name_last,
            'handle_str': handle_str,
            'session_list': [session_id],
            'permission_id': permission_id,
            'profile_img_url': "",
            'is_removed': False,
            'notifications': [],
        },
    }

    # Stores new value into account
    store['users'].update(new_account)

    data_store.set(store)

    return {
        'token': new_token,
        'auth_user_id': new_id,
    }
