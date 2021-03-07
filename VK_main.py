#!~/Project/VK/venv python 3
"""
my VK bot_group
"""
from random import randint

import requests
from pony.orm import db_session

import handlers
import settings
from models import UserState, Registration
from my_token_vk import token
from vk_api import bot_longpoll  # Without this method does not see the class VkBotLongPoll
import vk_api
import logging

group_id = 202361699
users_info = {}  # user_id : random_id
count_users = 0

log = logging.getLogger('bot')  # create main logging object


def configure_logging():
    """
    logging settings
    :return: None
    """
    stream_handler = logging.StreamHandler()  # analogue  print
    stream_handler.setLevel(logging.DEBUG)  # create record lvl-DEBUG
    stream_handler.setFormatter(logging.Formatter('%(levelname)s '   # define the format for output message
                                                  '%(message)s'))

    file_handler = logging.FileHandler('/home/dmitrii/Project/VK/log/log_file')  # writes to file
    file_handler.setLevel(logging.DEBUG)  # create record lvl-DEBUG
    file_handler.setFormatter(logging.Formatter('%(asctime)s '   # define the format for output message
                                                '%(levelname)s ' 
                                                '%(message)s'))
    log.addHandler(stream_handler)
    log.addHandler(file_handler)
    log.setLevel(logging.DEBUG)  # all log set lvl-DEBUG (view all lvl? because DEBUG is low-lvl


'lvl logging'
'NONSET'
'DEBUG'
'INFO - '
'WARNING'  # sms low-level don't send to log (such as INFO, DEBUG)
'ERROR'
'CRITICAL'


class Bot:
    """

    Use Python3.9
    """
    def __init__(self, group_id, token):  # create attributes
        """

        :param group_id:  group id VK
        :param token:  secret token
        """
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)  # Main class of library
        self.api = self.vk.get_api()  # This method allows you to refer to VK methods
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)  # Create BotLongPoller

        # Находясь на этапе сценария спрашиваем не хочет ли он начать другой, и храним его в этом сценарии

    def run(self):
        """

        start program
        """
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Ошибка в обратботке события')  # method of log, can view exception (as print err)

    @db_session  # decorator save changes in db automaticly ( вместо commit()- сохр. изменения вручную)
    def on_event(self, event: vk_api.bot_longpoll.VkBotEventType):
        """
        replies to text message

        :param event: VkBotMessageEvent object
        :return: None
        """
        global users_info  # user_id : random_id
        global count_users

        if event.type != vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:  # actions on message receiving event
            log.info(f'Получено новое событие типа {event.type}')
            return  # Выбрасывает из функции евент, иначе идет дальше по тексту и вызывает ошибки
        user_id = event.object.message.get('from_id')  # user ID who sent the message
        user_text = event.object.message.get('text')
        if user_id not in users_info.keys():
            count_users += 1
            users_info.setdefault(user_id, count_users)
        # log.debug('Отправляем сообщение назад')

        # state узнать из UserState по user_id через pony ORM
        state = UserState.get(user_id=str(user_id))  # pony method  Getting one object by unique combination of attributes

        if state is not None:  # checking if the user is in the scenario
            self.continue_scenario(text=user_text, state=state, user_id=user_id)  # use func continue_scenario and return txt  # add state to atr
        else:
            # search intent
            for intent in settings.INTENTS:  # looking for a match user_txt in every intention
                log.debug(f'User gets {intent}')
                if any(token in user_text.lower() for token in intent['tokens']):  # looking for a token match in user_txt
                    # run intent and output the answer
                    if intent['answer']:  # if there is an answer, display the answer
                        self.send_text(intent["answer"], user_id)
                    else:  # if there is no answer, start the scenario
                        self.start_scenario(user_id, intent['scenario'], text=user_text)  # user_id and name of scenario
                    break  # exit loop
            else:  # unexpected user_txt
                self.send_text(settings.default_answer,user_id)

    def send_text(self, text_to_send, user_id):  # send answer by ID
        self.api.messages.send(message=text_to_send,
                               user_id=user_id,
                               random_id=randint(0, 2**20),  # needed for safety
                               peer_id=user_id, )

    def send_image(self, image, user_id):
        # Нужно найти сервер, куда загрузить фото (upload_url)
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']  # return obj (upload_url, album_id, group_id)
        # send to upload_url file
        # После успешной загрузки сервер возвращает в ответе JSON-объект с полями server, photo, hash:
        response = requests.post(url=upload_url, files={'photo': ('image.jpg', image, 'image/jpg')})  # >>JSON (serv, photo, hash)
        upload_data = response.json() # берем json значения о загруженном изображении
        # files = {name: file} name work as descriptor, в файл необходимо указать полное название файла, прикрепить сам
        # файл, указать расширение файла, через спец символ "/", так как вк сам не разбирает что за файл, Нужно вручную
        # указывать эти данные, что бы он распарсил данные

        # Сохраняет фотографию после успешной загрузки на сервер
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)  #unpack all kwargs into vk_method
        # answer is obj - возвращённый объект имеет поля id, pid, aid, owner_id, src, src_big, src_small, created.
        owner_id = image_data[0]['owner_id']  # нужно взять первый элемент и из него вытащить нужные данные
        media_id = image_data[0]['id']

        attachment = f'photo{owner_id}_{media_id}'  # <type><owner_id>_<media_id>

        self.api.messages.send(attachment=attachment,  # method send img to user (documentation)
                               user_id=user_id,
                               random_id=randint(0, 2 ** 20),  # needed for safety
                               peer_id=user_id, )


    def send_step(self, step, user_id, text, context):  # send text and image if they exist
        if 'text' in step:
            self.send_text(step['text'].format(**context), user_id)  # current step text
        if 'image' in step:
            handler = getattr(handlers, step['image'])  # in current step get "handle_generate_picture"
            image = handler(text, context) # call generate_picture, return temp_file
            self.send_image(image, user_id)  # call func send_image


    def start_scenario(self, user_id, scenario_name, text):
        """
        start scenario
        :param user_id: user id
        :param scenario_name: scenario name
        :return: text to send (bot_answer)
        """
        scenario = settings.scenarios[scenario_name]  # enter scenario.name (example: scenario.registration)
        first_step = scenario['first_step']  # init first step
        step = scenario['steps'][first_step]  # init current step
        self.send_step(step, user_id, text, context={})  # context={} because it init next row
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={}) #!! create table

    def continue_scenario(self, text, state, user_id):  # add state to atr
        """
        moves in steps
        :param user_id: user id
        :param text: user_text
        :return: text to send (bot_answer)
        """
        steps = settings.scenarios[state.scenario_name]["steps"]  # dict of all steps
        step = settings.scenarios[state.scenario_name]["steps"][state.step_name]  # current step (in settings)

        handler = getattr(handlers, step['handler'])  # Returns handler for the current step getattr(obj,name_attr)
        if handler(text=text, context=state.context):  # if the data is entered correctly
            # next step
            next_step = steps[step['next_step']]  # in the current step choose next_step
            self.send_step(next_step, user_id, text, state.context)  # text to send (bot_answer) context is defined in handlers.py
            if next_step["next_step"]:  # if there is a next step
                # switch to next step
                state.step_name = step['next_step']  # redefine the current step to the next
            else:  # if there is not a next step
                # finish scenario
                log.info('Зарегистрирован: {name} {email}'.format(**state.context))
                state.delete() # remove the user from the scenario  # delete from sql
                Registration(name=state.context['name'], email=state.context['email'])  # init table Registration
        else:  # if the data is entered incorrectly
            # retry current step
            self.send_text(step['failure_text'].format(**state.context), user_id)



if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id, token)
    bot.run()
