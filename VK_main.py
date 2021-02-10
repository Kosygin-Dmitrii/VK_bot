#!~/Project/VK/venv python 3
"""
my VK bot_group
"""
import handlers
import settings
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

class UserState:
    """
    user states inside the scenario
    """
    def __init__(self, scenario_name, step_name, context = None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}



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

        self.user_states = dict()  # user_id --> UserState - step on script
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


        if user_id in self.user_states:
            text_to_send = self.continue_scenario(user_id, text=user_text)
        else:
            # search intent
            for intent in settings.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in event.object.message.get('text') for token in intent['tokens']):
                    # run intent произведем нужные действя и сделаем брейк
                    if intent['answer']:
                        text_to_send = intent["answer"]
                    else:
                        text_to_send = self.start_scenario(user_id, intent['scenario'])
                    break
            else:
                text_to_send = settings.default_answer

        self.api.messages.send(message=text_to_send,
                               user_id=user_id,
                               random_id=event.object.message.get('id'),  # needed for safety
                               peer_id=user_id, )

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.scenarios[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send

    def continue_scenario(self, user_id, text):
        state = self.user_states[user_id]
        steps = settings.scenarios[state.scenario_name]["steps"]
        step = settings.scenarios[state.scenario_name]["steps"][state.step_name]

        handler = getattr(handlers, step['handler'])  # ищет в модуле определенную функцию
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)  # text для отправки
            if next_step["next_step"]:
                # switch to next step
                state.step_name = step['next_step']
            else:
                # finish scenario
                self.user_states.pop(user_id)
                log.info('Зарегистрирован: {name} {email}'.format(**state.context))
        else:
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)

        return text_to_send


if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id, token)
    bot.run()
