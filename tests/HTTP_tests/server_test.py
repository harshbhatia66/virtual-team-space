import requests
import json
from src import config

''' 
----------------------------------------------------
    Test HTTP Server for echo function
----------------------------------------------------
'''

def test_echo():
    '''
    A simple test to check echo
    '''
    resp = requests.get(config.url + 'echo', params={'data': 'hello'})
    assert json.loads(resp.text) == {'data': 'hello'}

def test_echo_except():

    resp = requests.get(config.url + 'echo', params={'data': 'echo'})
    assert resp.status_code == 400