import pytest
from PIL import Image
import urllib.request
from src.auth import auth_register_v2
from src.user import user_profile_uploadphoto_v1
from src.error import AccessError, InputError
from src.other import clear_v1
from requests import get
from io import BytesIO
from PIL import Image

@pytest.fixture
def user():
    clear_v1()
    user1 = auth_register_v2("andacrossthesea@gmail.com", "TATAKAE!1!", "Eren", "Yaeger")
    img_url = 'http://novascotiatoday.com/wp-content/uploads/2021/10/eren-yeager-.-1024x768.jpg'
    image_raw = get(img_url)
    image = Image.open(BytesIO(image_raw.content))
    width, height = image.size
    return [user1, img_url, width, height]

# def test_valid_crop(user):
#     token = user[0]['token']
#     img_url = user[1]
#     x_start = 0
#     y_start = 0
#     x_end = user[2] - 5
#     y_end = user[3] - 5

#     user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)
    
def test_invalid_start(user):
    token = user[0]['token']
    img_url = user[1]
    x_start = -5
    y_start = -5
    x_end = user[2] - 5
    y_end = user[3] - 5
    with pytest.raises(InputError):
        assert user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)

def test_invalid_end(user):
    token = user[0]['token']
    img_url = user[1]
    x_start = 0
    y_start = 0
    x_end = user[2] + 10
    y_end = user[3] + 10
    with pytest.raises(InputError):
        assert user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)

def test_invalid_url(user):
    token = user[0]['token']
    img_url = 'http://static.wikia.nocookie.net/villains/images/4/4c/Eren_meets_Yeagerists.png/revision/latest?cb=20210302172340'
    image_raw = get(img_url)
    image = Image.open(BytesIO(image_raw.content))
    width, height = image.size
    x_start = 0
    y_start = 0
    x_end = width - 10
    y_end = height - 10
    with pytest.raises(InputError):
        assert user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)

def test_empty_url(user):
    token = user[0]['token']
    img_url = ''
    x_start = 0
    y_start = 0
    x_end = 10
    y_end = 10
    with pytest.raises(InputError):
        assert user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)


def test_invalid_token(user):
    invalid_token = -1
    img_url = user[1]
    x_start = 0
    y_start = 0
    x_end = user[2] - 10
    y_end = user[3] - 10
    with pytest.raises(AccessError):
        assert user_profile_uploadphoto_v1(invalid_token, img_url, x_start, y_start, x_end, y_end)


