"""
Содержит слова (tokens) по которым определяет ответ пользователю, либо запускает сценарий.
Сценарий содержит шаги, которые необходимо пройти поэтапно.

"""


# Намерения
from my_token_vk import passw

INTENTS = [
    {
        'name': 'Дата проведения',
        'tokens': ("когда", "сколько", "дата", "дату"),
        'scenario': None,
        'answer': '03.07.2021',

    },
{
        'name': 'Место проведения',
        'tokens': ("где", "место", "локация", "адрес"),
        'scenario': None,
        'answer': 'Площадка 111',

    },
{
        'name': 'Регистрация',
        'tokens': ('регистр', "добав"),
        'scenario': "registration",
        'answer': None,

    }
]

scenarios = {
    'registration': {
        "first_step": 'step1',
        "steps": {
            "step1": {
                "text": "Что бы зарегистрироваться, введите ваше имя.",
                'failure_text': 'Имя должно состоять от 3 букв и до 30. Пробуй еще раз.',
                "handler": "handle_name",
                "next_step": 'step2'
            },
            "step2":{
                "text": "Введите Email для отправки данных",
                'failure_text': 'Даже Email свой не смог ввести!',
                "handler": "handle_email",
                "next_step": 'step3'
            },
            'step3': {
                "text": "Спасибо за регистрацию, {name}! Мы уже взламываем ваш {email}, удачи!",
                'failure_text': None,
                "handler": None,
                "next_step": None
            }
        }
    }
}

default_answer = 'Ну что за непотребства ты тут пишешь!' \
                'Могу сказать где и когда пройдет событие! Спроси лучше об этом.' \
                 'Также могу зарегистрировать'




#create user db_dmitrii with password *****;
#GRANT ALL PRIVILEGES ON DATABASE "vk_chat_bot" to db_dmitrii;
DB_CONFIG = dict(provider='postgres', user='db_dmitrii', password=passw,host='localhost',database='vk_chat_bot')