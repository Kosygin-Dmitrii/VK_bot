#!~/Project/VK/venv python 3

from my_token_vk import token
from vk_api import bot_longpoll  # Without this method does not see the class VkBotLongPoll
import vk_api
import logging

group_id = 202361699
users_info = {}  # user_id : random_id
count_users = 0

log = logging.getLogger('bot')  # create main logging object


def configure_logging():
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
    def __init__(self, group_id, token):  # create attributes
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)  # Main class of library
        self.api = self.vk.get_api()  # This method allows you to refer to VK methods
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)  # Create BotLongPoller

    def run(self):
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('Ошибка в обратботке события')  # method of log, can view exception (as print err)

    def on_event(self, event):
        global users_info  # user_id : random_id
        global count_users

        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:  # actions on message receiving event
            print(event.object.message.get('text'))
            user_id = event.object.message.get('from_id')  # user ID who sent the message
            if user_id not in users_info.keys():
                count_users += 1
                users_info.setdefault(user_id, count_users)
            log.debug('Отправляем сообщение назад')
            self.api.messages.send(message='auto answer',
                                   user_id=user_id,
                                   random_id=event.object.message.get('id'),  # needed for safety
                                   peer_id=user_id, )
        else:
            log.info(f'Получено новое событие типа {event.type}')


if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id, token)
    bot.run()
