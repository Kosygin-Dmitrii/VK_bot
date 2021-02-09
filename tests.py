"""Mock — вспомогательная библиотека по созданию mock-объектов.
Mock — это набор объектов, которыми можно подменить настоящий объект.
На любое обращение к методам, к атрибутам он возвращает тоже mock.
MOCK - ЗАГЛУШКА

coverage
coverage run --source=VK_main -m unittset   запускает тестирование с анализом покрытия кода
coverage report -m    показывает результаты тестирования, покрытие кода в процентах
"""

from unittest import TestCase
from unittest.mock import patch, Mock, ANY
from vk_api.bot_longpoll import VkBotMessageEvent
from VK_main import Bot


class Test1(TestCase):
    RAW_EVENT = {'type': 'message_new',
                 'object': {'message': {'date': 1612890850, 'from_id': 66751578, 'id': 106, 'out': 0,
                                        'peer_id': 66751578, 'text': 'Привет бот1', 'conversation_message_id': 70,
                                        'fwd_messages': [], 'important': False, 'random_id': 0, 'attachments': [],
                                        'is_hidden': False},
                            'client_info': {'button_actions': ['text', 'vkpay', 'open_app', 'location', 'open_link',
                                                               'intent_subscribe', 'intent_unsubscribe'],
                                            'keyboard': True, 'inline_keyboard': True, 'carousel': False,
                                            'lang_id': 0}},
                 'group_id': 202361699, 'event_id': 'a5142f5d290238ce7c91e241dc22abb3283a9841'}
    def test_run(self):
        count = 5
        events = [{}]*count  # [{}, {}, ...]
        long_poller_mock = Mock(return_value=events)  # создаем аналог функции listen, возвращающий пустой список, а не события
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('VK_main.vk_api.VkApi'):  # принимает на вход адрес объекта который нужно пропатчить, замокать(заглушка)
            with patch('VK_main.vk_api.bot_longpoll.VkBotLongPoll',  # ставит заглушки на методы, которые создают ненужные для тестов объекты.
                       return_value=long_poller_listen_mock):   # Переопределяем return long_poller.listen
                bot = Bot('', '')  # создаем класс бота с пустыми токеном и ID
                bot.on_event = Mock()  # заменяем функцию на заглушку
                bot.run()  # т.к использует функцию listen ее необходимо подменить, чтоб возвращала фейковые ивенты и передовала их в функцию on_event

                # т.к это Mock есть свойство запоминающее, как сколько раз и с какими аргументами функция вызывалась
                bot.on_event.assert_called()  # Вызывали ли метод вообще
                bot.on_event.assert_any_call({})  # вызывалась функция только с таким аргументом
                assert bot.on_event.call_count == count

    def test_on_event(self):
        """
        test on_event function - создает класс БОТ, с пустыми id and token, мокает методы, взаимодействующуе с
        внешнимим системами, мокает метод api, позволяющий работать с методами VK, при вызове метода VK send
        натыкается на заглушку. проверяет, вызывался ли метод send с указанными параметрами. Параметры взяты из
        сырой строки (raw) класса VkBotMessageEvent из функции инициализации с помощью дебагинга и брейкпоинта.

        :return:
        """

        event = VkBotMessageEvent(raw=self.RAW_EVENT)

        send_mock = Mock()
        with patch('VK_main.vk_api.VkApi'):
            with patch('VK_main.vk_api.bot_longpoll.VkBotLongPoll'):
                bot = Bot('', '')
                bot.api = Mock()
                bot.api.messages.send = send_mock

                bot.on_event(event)
        send_mock.assert_called_once_with(message='auto answer',
                                          user_id=self.RAW_EVENT['object']['message']['from_id'],
                                          random_id=ANY,  # принимает любое значение
                                          peer_id=self.RAW_EVENT['object']['message']['peer_id'])
