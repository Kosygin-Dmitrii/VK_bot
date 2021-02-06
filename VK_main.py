#!~/Project/VK/venv python 3

from my_token_vk import token
from vk_api import bot_longpoll  # Without this method does not see the class VkBotLongPoll
import vk_api

group_id = 202361699
users_info = {}  # user_id : random_id
count_users = 0


class Bot:
    def __init__(self, group_id, token):  # create attributes
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)  # Main class of library
        self.api = self.vk.get_api()  # This method allows you to refer to VK methods
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)  # Create BotLongPoller

    def run(self):
        for event in self.long_poller.listen():
            print('Получено событие')
            try:
                self.on_event(event)
            except Exception as err:
                print(err)

    def on_event(self, event):
        global users_info  # user_id : random_id
        global count_users

        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:  # actions on message receiving event
            print(event.object.message.get('text'))
            user_id = event.object.message.get('from_id')  # user ID who sent the message
            if user_id not in users_info.keys():
                count_users += 1
                users_info.setdefault(user_id, count_users)
            self.api.messages.send(message='auto answer',
                                   user_id=user_id,
                                   random_id=event.object.message.get('id'),  # needed for safety
                                   peer_id=user_id, )
        else:
            print(f'Получено новое событие типа{event.type}')


if __name__ == '__main__':
    bot = Bot(group_id, token)
    bot.run()
