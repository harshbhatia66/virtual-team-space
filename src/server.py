from crypt import methods
import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src import config

from src.auth import auth_login_v2, auth_register_v2, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.user import user_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_sethandle_v1, user_profile_setemail_v1, user_stats_v1
from src.user import user_stats_v1, users_stats_v1, user_profile_uploadphoto_v1
from src.channel import channel_details_v2, channel_join_v2, channel_invite_v2, channel_messages_v2, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.dm import dm_create_v1, dm_list_v1, dm_messages_v1, dm_details_v1, dm_leave_v1, dm_remove_v1
from src.admin import user_remove_v1, user_permission_change_v1
from src.message import message_send_v1, message_send_dm_v1, message_remove_v1, message_edit_v1, search_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src.message import message_sendlater_v1, message_sendlaterdm_v1, message_share_v1
from src.notification import notifications_get_v1
from src.standup import standup_active_v1, standup_send_v1, standup_start_v1

from src.echo import echo
from src.other import clear_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example 1
@APP.route("/echo", methods=['GET'])
def call_echo():
    data = request.args.get('data')
    
    res = echo(data)

    return dumps({
        'data': res
    })

# Clear v1
@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()

    return dumps({})

# Auth Login
@APP.route("/auth/login/v2", methods=['POST'])
def login():
    data = request.get_json()                                 
    email = data['email']
    password = data['password']

    result = auth_login_v2(email, password)

    return dumps(result)

# Auth Register
@APP.route("/auth/register/v2", methods=['POST'])
def register():
    data = request.get_json()   
    email = data['email']
    password = data['password']
    name_first = data['name_first']
    name_last = data['name_last']

    result = auth_register_v2(email, password, name_first, name_last)

    return dumps(result)

# Channels Create
@APP.route("/channels/create/v2", methods=['POST'])
def create_new_channel():
    data = request.get_json()
    token = data['token']
    name = data['name']
    is_public = bool(data['is_public'])

    channel = channels_create_v2(token, name, is_public)

    return dumps(channel)

# Channels List 
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    token = request.args.get('token')
    lst = channels_list_v2(token)

    return dumps(lst)

# Channels Listall
@APP.route("/channels/listall/v2", methods=['GET'])
def channels_list_all():
    token = request.args.get('token')
    lst = channels_listall_v2(token)

    return dumps(lst)

# Channel Invite
@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    
    channel_invite_v2(token, channel_id, u_id)

    return dumps({})

# Channel Join
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])

    channel_join_v2(token, channel_id)

    return dumps({})
    
# Channel Details
@APP.route("/channel/details/v2", methods=['GET'])
def get_channel_details():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    details = channel_details_v2(token, channel_id)
    
    return dumps(details)

# Channel Messages
@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    token = request.args.get('token')
    chan_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    msg = channel_messages_v2(token, chan_id, start)

    return dumps(msg)

# Channel Leave
@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']

    channel_leave_v1(token, channel_id)

    return dumps({})

# Channel Add Owner
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    token = data['token']
    chan_id = int(data['channel_id'])
    u_id = int(data['u_id'])

    channel_addowner_v1(token, chan_id, u_id)

    return dumps({})

# Channel Remove Owner
@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])

    channel_removeowner_v1(token, channel_id, u_id)

    return dumps({})

# Auth Logout
@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    data = request.get_json()
    token = data['token']

    auth_logout_v1(token)
    
    return dumps({})

# DM Create
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    token = data['token']    
    u_ids = list(map(int, data['u_ids'])) # -> ["1", "2", "3"] -> [1,2,3]
    dm_id = dm_create_v1(token, u_ids)
    
    return dumps(dm_id)

# DM List
@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')

    lst = dm_list_v1(token)
    
    return dumps(lst)

# DM Messages
@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))

    messages = dm_messages_v1(token, dm_id, start)

    return dumps(messages)

# DM Details
@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    details = dm_details_v1(token, dm_id)

    return dumps(details)

# DM Leave
@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    token = data['token']
    dm_id = int(data['dm_id'])

    dm_leave_v1(token, dm_id)
    return dumps({})

# DM Remove
@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    token = data['token']
    dm_id = int(data['dm_id'])

    dm_remove_v1(token, dm_id) 
    return dumps({})

# User Profile Setname
@APP.route("/user/profile/setname/v1", methods=["PUT"])
def user_profile_setname():
    data = request.get_json()    
    token = data['token']
    name_first = data['name_first']
    name_last = data['name_last']
    
    user_profile_setname_v1(token, name_first, name_last)
    
    return dumps({})

# User Profile Sethandle
@APP.route("/user/profile/sethandle/v1", methods=["PUT"])
def user_profile_sethandle():
    data = request.get_json()    
    token = data['token']
    handle_str = data['handle_str']
    
    user_profile_sethandle_v1(token, handle_str)
    
    return dumps({})

# User All
@APP.route("/users/all/v1", methods=['GET'])
def user_all():
    token = request.args.get('token')
    
    users = user_all_v1(token)

    return dumps(users)

# User Profile
@APP.route("/user/profile/v1", methods=["GET"])
def user_profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))

    profile = user_profile_v1(token, u_id)

    return dumps(profile)

# User Profile Setemail
@APP.route("/user/profile/setemail/v1", methods=["PUT"])
def set_user_email():
    data = request.get_json()
    token = data['token']
    email = data['email']

    user_profile_setemail_v1(token, email)
    return dumps({})

# Admin Change User Permission
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def change_user_permission():
    data = request.get_json()
    token = data['token']
    u_id = int(data['u_id'])
    perm_id = int(data['permission_id'])

    user_permission_change_v1(token, u_id, perm_id)

    return dumps({})

# Admin User Remove
@APP.route("/admin/user/remove/v1", methods=["DELETE"])
def admin_user_remove():
    data = request.get_json()
    token = data['token']
    u_id = int(data['u_id'])
    
    user_remove_v1(token, u_id)

    return dumps({})

# Message Send
@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    msg = data['message']

    message = message_send_v1(token, channel_id, msg)

    return dumps(message)

# Message Send DMS
@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddms():
    data = request.get_json()
    token = data['token']
    dm_id = int(data['dm_id'])
    msg = data['message']

    message = message_send_dm_v1(token, dm_id, msg)

    return dumps(message)

# Message Edit
@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    data = request.get_json()
    token = data['token']
    msg_id = int(data['message_id'])
    msg = data['message']

    message_edit_v1(token, msg_id, msg)
    return dumps({})

# Message Remove
@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    data = request.get_json()
    token = data['token']
    msg_id = int(data['message_id'])

    message_remove_v1(token, msg_id) 
    return dumps({})

# Notifications Get
@APP.route("/notifications/get/v1", methods=['GET'])
def notifications():
    token = request.args.get('token')

    return dumps(notifications_get_v1(token))

# Search
@APP.route("/search/v1", methods=['GET'])
def search():
    token = request.args.get('token')
    query_str = request.args.get('query_str')

    search_result = search_v1(token, query_str)
    return dumps(search_result)

# Message Share
@APP.route("/message/share/v1", methods=['POST'])
def message_share():
    data = request.get_json()
    token = data['token']
    og_message_id = int(data['og_message_id'])
    message = data['message']
    channel_id = int(data['channel_id'])
    dm_id = int(data['dm_id'])
    shared_message_id = message_share_v1(token, og_message_id, message, channel_id, dm_id)
    return dumps(shared_message_id)

# Message React
@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    react_id = data['react_id']
    
    react = message_react_v1(token, message_id, react_id)
    return dumps(react)

# Message Unreact
@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    react_id = data['react_id']
    
    unreact = message_unreact_v1(token, message_id, react_id)
    return dumps(unreact)

# Message Pin
@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    pin = message_pin_v1(token, message_id)
    
    return dumps(pin)

# Message Unpin
@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    unpin = message_unpin_v1(token, message_id)
    
    return dumps(unpin)

# Message Send Later
@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    data = request.get_json()
    token = data['token']
    chan_id = int(data['channel_id'])
    message = data['message']
    time_sent = int(data['time_sent'])

    return dumps(message_sendlater_v1(token, chan_id, message, time_sent))

# Message Send Later DM
@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm():
    data = request.get_json()
    token = data['token']
    chan_id = int(data['dm_id'])
    message = data['message']
    time_sent = int(data['time_sent'])

    return dumps(message_sendlaterdm_v1(token, chan_id, message, time_sent))
# Standup Start
@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    length = int(data['length'])
    
    return dumps(standup_start_v1(token, channel_id, length))

# Standup Active
@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():

    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    return dumps(standup_active_v1(token, channel_id))

# Standup Active
@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():

    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    msg = data['message']


    return dumps(standup_send_v1(token, channel_id, msg))

# Auth Password Reset Request
@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def passwordreset_request():
    data = request.get_json()
    email = data['email']

    auth_passwordreset_request_v1(email)

    return dumps({})

# Auth Password Reset
@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def passwordreset_reset():
    data = request.get_json()
    reset_code = data['reset_code']
    new_password = data['new_password']

    auth_passwordreset_reset_v1(reset_code, new_password)

    return dumps({})

# User Prof ile Upload Photo
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto():
    data = request.get_json()
    token = data['token']
    img_url = data['img_url']
    x_start = int(data['x_start'])
    x_end = int(data['x_end'])
    y_start = int(data['y_start'])
    y_end = int(data['y_end'])
    user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)
    return dumps({})
    
# User Stats
@APP.route("/user/stats/v1", methods=['GET'])
def user_stats():
    token = request.args.get('token')

    return dumps(user_stats_v1(token))

# Users Stats
@APP.route("/users/stats/v1", methods=['GET'])
def users_stats():
    token = request.args.get('token')
    return dumps(users_stats_v1(token))

# Uploads photos to the server
@APP.route("/imgurl/<path:filename>")
def send_image_js(filename):

    return send_from_directory('../database/static', filename)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
