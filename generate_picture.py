from PIL import Image, ImageFont, ImageDraw

PICTURE_PATH = 'original_picture.jpg'
FONT_PATH = 'Roboto-Regular.ttf'
FONT_SIZE = 30
BLACK = (0, 0, 0, 255)  # RGBO, O - opacity - прозрачность
NAME_OFFSET = (140, 310)  # Смещение
EMAIL_OFFSET = (140, 360)  # 140, 360 отступ вправо вниз от угла.


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
    base.show()


generate_picture('Dima', 'asd@asd.ru')
