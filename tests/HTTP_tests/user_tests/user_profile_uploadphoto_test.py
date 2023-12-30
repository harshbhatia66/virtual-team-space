import pytest
import requests
import json
from src import config
from requests import get
from io import BytesIO
from PIL import Image


def clear():
    response = requests.delete(config.url + 'clear/v1')
    
    assert response.status_code == 200

def create_user(email, password, name_first, name_last):
    response = requests.post(config.url + "auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last
    })

    assert response.status_code == 200
    user = response.json()
    return user

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    resp = requests.post(config.url + "user/profile/uploadphoto/v1", json={
        "token": token,
        "img_url": img_url,
        "x_start": x_start,
        "y_start": y_start,
        "x_end": x_end,
        "y_end": y_end
    })
    return resp

@pytest.fixture
def setup():
    clear()
    user1 = create_user("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    img_url = 'http://novascotiatoday.com/wp-content/uploads/2021/10/eren-yeager-.-1024x768.jpg'
    image_raw = get(img_url)
    image = Image.open(BytesIO(image_raw.content))
    width, height = image.size
    return [user1, img_url, width, height]


''' 
----------------------------------------------------
    Test HTTP Server for Upload Photo 
----------------------------------------------------
'''
# def test_valid_crop(setup):
#     token = setup[0]['token']
#     img_url = setup[1]
#     x_start = 0
#     y_start = 0
#     x_end = setup[2] - 5
#     y_end = setup[3] - 5

#     resp = user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
#     assert resp.status_code == 200
    
def test_invalid_start(setup):
    token = setup[0]['token']
    img_url = setup[1]
    x_start = -5
    y_start = -5
    x_end = setup[2] - 5
    y_end = setup[3] - 5
    resp = user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
    assert resp.status_code == 400

def test_invalid_end(setup):
    token = setup[0]['token']
    img_url = setup[1]
    x_start = 0
    y_start = 0
    x_end = setup[2] + 10
    y_end = setup[3] + 10
    resp = user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
    assert resp.status_code == 400

def test_invalid_url(setup):
    token = setup[0]['token']
    img_url = 'http://static.wikia.nocookie.net/villains/images/4/4c/Eren_meets_Yeagerists.png/revision/latest?cb=20210302172340'
    image_raw = get(img_url)
    image = Image.open(BytesIO(image_raw.content))
    width, height = image.size
    x_start = 0
    y_start = 0
    x_end = width - 10
    y_end = height - 10
    resp = user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
    assert resp.status_code == 400

def test_invalid_status_code(setup):
    token = setup[0]['token']
    img_url = ''
    x_start = 0
    y_start = 0
    x_end = 10
    y_end = 10
    resp = user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end)
    assert resp.status_code == 400

def test_invalid_token(setup):
    invalid_token = -1
    img_url = setup[1]
    x_start = 0
    y_start = 0
    x_end = setup[2] - 10
    y_end = setup[3] - 10
    resp = user_profile_uploadphoto(invalid_token, img_url, x_start, y_start, x_end, y_end)
    assert resp.status_code == 403

