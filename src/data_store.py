'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

import os.path
import pickle

initial_object = {
    'users': {},
    'channels': {},
    'dms': {},
    'standups': {},
} 

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def get_saved_data(self):
        self.__store = pickle.load(open('database/datastore.p', 'rb'))

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')

        # Persist saves into datastore.p everytime a data is changed and set
        with open('database/datastore.p', 'wb') as FILE:
            pickle.dump(store, FILE)

        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()

# Checks if datastore.p exists, thus applies current data into server
if os.path.exists('database/datastore.p'):
    data_store.get_saved_data()
