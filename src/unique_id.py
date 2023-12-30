import pickle
import os.path

class UniqueID:
    def __init__(self, type):
        self.__type = type
        self.__id = 0

    def set_start_point(self, start):
        self.__id = start

    def get(self):
        self.__id += 1  

        # Persist saves into datastore.p everytime a data is changed and set
        with open(f"database/{self.__type}_id.p", 'wb') as FILE:
            pickle.dump(self.__id, FILE)
            
        return self.__id

    def get_saved_data(self):
        self.__id = pickle.load(open(f"database/{self.__type}_id.p", 'rb'))

    def reset(self):
        self.__id = 0
        
        # Persist saves into datastore.p everytime a data is changed and set
        with open(f"database/{self.__type}_id.p", 'wb') as FILE:
            pickle.dump(self.__id, FILE)

global unique_auth_id
unique_auth_id = UniqueID("auth")
unique_auth_id.set_start_point(1000)

global unique_channel_id
unique_channel_id = UniqueID("channel")

global unique_dm_id
unique_dm_id = UniqueID("dm")

global unique_msg_id
unique_msg_id = UniqueID("message")

global unique_img_id
unique_img_id = UniqueID("img")

# Checks if *_id.p exists, thus applies current data into server

if os.path.exists('database/auth_id.p'):
    unique_auth_id.get_saved_data()

if os.path.exists('database/channel_id.p'):
    unique_channel_id.get_saved_data()

if os.path.exists('database/dm_id.p'):
    unique_dm_id.get_saved_data()

if os.path.exists('database/message_id.p'):
    unique_msg_id.get_saved_data()

if os.path.exists('database/img_id.p'):
    unique_img_id.get_saved_data()