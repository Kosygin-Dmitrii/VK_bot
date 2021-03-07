from io import BytesIO

import requests
from PIL import Image, ImageFont, ImageDraw

PICTURE_PATH = 'original_picture.jpg'
FONT_PATH = 'Roboto-Regular.ttf'
FONT_SIZE = 30
BLACK = (0, 0, 0, 255)  # RGBO, O - opacity - прозрачность
NAME_OFFSET = (140, 310)  # Смещение
EMAIL_OFFSET = (140, 360)  # 140, 360 отступ вправо вниз от угла.
WIDGHT = 200
HEIGHT = 200

def generate_picture(name, email):  # name - user name
    """
    draw words in picture
    :param name: user name
    :param email: user email
    :return:
    """
    base = Image.open(PICTURE_PATH).convert('RGBA')  # open picture
    font = ImageFont.truetype(FONT_PATH, size=FONT_SIZE)  # download font

    # create object draw ( it is used to insert text)
    draw = ImageDraw.Draw(base)
    draw.text(NAME_OFFSET, name, font=font, fill=BLACK)
    draw.text(EMAIL_OFFSET, email, font=font, fill=BLACK)
    response = requests.get(url=f'https://eu.ui-avatars.com/api/?name={name}+{email}'
                                f'&background=random'
                                f'&size=100'
                                f'&rounded=False')
    avatar_like_file = BytesIO(response.content)  # на вход байты, на выходе объект-файл, In - bytes, Out - like file
    'avatar = Image.open(response.content)  # ожидает путь или файловый дискриптор, а response.contenet возвращает строчку с байтами'
    avatar_pic = Image.open(avatar_like_file)
    base.paste(avatar_pic, (357,290))

    temp_file = BytesIO()  # object like file descriptor
    base.save(temp_file, 'png')  # Сохранив значение во временный файл, минмый курсор остался в конце записи, при чтении
    temp_file.seek(0)  # файла, читаться будет с курсора, поэтому устанавливаем его в начало файла seek - искать


    return temp_file







