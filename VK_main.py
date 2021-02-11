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
        self.context = context or {}  # context is defined in handlers.py



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

        if user_id in self.user_states:  # checking if the user is in the scenario
            text_to_send = self.continue_scenario(user_id, text=user_text)  # use func continue_scenario and return txt
        else:
            # search intent
            for intent in settings.INTENTS:  # looking for a match user_txt in every intention
                log.debug(f'User gets {intent}')
                if any(token in user_text for token in intent['tokens']):  # looking for a token match in user_txt
                    # run intent and output the answer
                    if intent['answer']:  # if there is an answer, display the answer
                        text_to_send = intent["answer"]
                    else:  # if there is no answer, start the scenario
                        text_to_send = self.start_scenario(user_id, intent['scenario'])  # user_id and name of scenario
                    break  # exit loop
            else:  # unexpected user_txt
                text_to_send = settings.default_answer

        self.api.messages.send(message=text_to_send,
                               user_id=user_id,
                               random_id=event.object.message.get('id'),  # needed for safety
                               peer_id=user_id, )

    def start_scenario(self, user_id, scenario_name):
        """
        start scenario
        :param user_id: user id
        :param scenario_name: scenario name
        :return: text to send (bot_answer)
        """
        scenario = settings.scenarios[scenario_name]  # enter scenario.name (example: scenario.registration)
        first_step = scenario['first_step']  # init first step
        step = scenario['steps'][first_step]  # init current step
        text_to_send = step['text']  # current step text
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)  # create dict (user_id : UserState)
        return text_to_send  # returns the text_to_send of the first step

    def continue_scenario(self, user_id, text):
        """
        moves in steps
        :param user_id: user id
        :param text: user_text
        :return: text to send (bot_answer)
        """
        state = self.user_states[user_id]  # current state of user (cls UserState)
        steps = settings.scenarios[state.scenario_name]["steps"]  # dict of all steps
        step = settings.scenarios[state.scenario_name]["steps"][state.step_name]  # current step (in settings)

        handler = getattr(handlers, step['handler'])  # Returns handler for the current step getattr(obj,name_attr)
        if handler(text=text, context=state.context):  # if the data is entered correctly
            # next step
            next_step = steps[step['next_step']]  # in the current step choose next_step
            text_to_send = next_step['text'].format(**state.context)  # text to send (bot_answer) context is defined in handlers.py
            if next_step["next_step"]:  # if there is a next step
                # switch to next step
                state.step_name = step['next_step']  # redefine the current step to the next
            else:  # if there is not a next step
                # finish scenario
                self.user_states.pop(user_id)  # remove the user from the scenario
                log.info('Зарегистрирован: {name} {email}'.format(**state.context))
        else:  # if the data is entered incorrectly
            # retry current step
            text_to_send = step['failure_text'].format(**state.context)

        return text_to_send


if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id, token)
    bot.run()
