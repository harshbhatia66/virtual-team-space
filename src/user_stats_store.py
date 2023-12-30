from src.data_store import data_store

CHANNEL_JOINED = []
DMS_JOINED = []
MESSAGE_SENT = []

CHANNEL_EXIST = []
DMS_EXIST = []
MESSAGE_EXIST = []

# Users Stats helpersw
def get_channels_list(u_id):
    user_channels = []
    store = data_store.get()

    for channel in store['channels'].values():
        if u_id in channel['all_members']:
            user_channels.append(channel['channel_id'])

    return user_channels


def get_dm_list(u_id):
    data = data_store.get()
    dms = data['dms']
    
    user_dms = []  
    for dm in dms.values():
        if u_id in dm['members']:
            user_dms.append(dm['dm_id'])

    return user_dms