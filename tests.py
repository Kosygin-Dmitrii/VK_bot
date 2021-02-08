"""Mock — вспомогательная библиотека по созданию mock-объектов.
Mock — это набор объектов, которыми можно подменить настоящий объект.
На любое обращение к методам, к атрибутам он возвращает тоже mock.
MOCK - ЗАГЛУШКА
"""

from unittest import TestCase
from unittest.mock import patch, Mock
from VK_main import Bot


class Test1(TestCase):
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
