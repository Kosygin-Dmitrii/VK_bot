"""
handler - функция, которая принимает на вход text и context(dict), а возвращает bool:
True если шаг пройден, False - если введены неправильные данные
"""

import re

pattern_re_name = r'^[\w\s \-]{3,40}$' # ^ - начало строки, $ - конец строки , w - буквы, s - пробел
pattern_re_email = r"(\b^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b)" # ctrl+V google  \b...\b позволяет отделить конструкцию в контексте

def handle_name(text, context):
    """
    processes the received text from the user
    :param text: полученный от пользователя текст
    :param context:
    :return: T or F
    """
    match = re.match(pattern_re_name,  text)  # сравниваем введенный текст с шаблоном имени
    if match:
        context['name'] = text  # create (context == {'name': 'Dima'} )
        return True
    else:
        return False

def handle_email(text, context):
    matches = re.findall(pattern_re_email, text)
    if len(matches) > 0:
        context['email'] = matches[0]
        return True
    else:
        return False


