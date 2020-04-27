from chatbot.bot import ChatBot
import unittest
from unittest.mock import Mock, patch


class TestBot(unittest.TestCase):
    def setUp(self):
        self.ROW_EVENT = {'type': 'message_new',
                          'object':
                              {'message':
                                   {'date': 1578149090,
                                    'from_id': 8023886,
                                    'id': 1,
                                    'out': 0,
                                    'eer_id': 8023886,
                                    'text': 'Привет!',
                                    'conversation_message_id': 1,
                                    'fwd_messages': [],
                                    'important': False,
                                    'random_id': 0,
                                    'attachments': [],
                                    'is_hidden': False
                                    },
                               },
                          'group_id': 170928524,
                          'event_id': 'e0fef5a6e2955111070321c911bca98a45335944',
                          }

    def test_smoke(self):
        ChatBot('', '')

    def test_connect(self):
        with patch('chatbot.bot.VkApi'), \
             patch('chatbot.bot.VkBotLongPoll'), \
             patch('chatbot.bot.logging'):
            bot = ChatBot('', '')
            bot.connect()
            self.assertIsNotNone(bot.vk)
            self.assertIsNotNone(bot.api)
            self.assertIsNotNone(bot.bot_longpoll)

    def listen(self):
        event = Mock(return_value=self.ROW_EVENT)
        event.type = Mock()
        event.type.value = self.ROW_EVENT['type']
        return [event, ]

    def test_run(self):
        long_poll_listen_mock = Mock()
        long_poll_listen_mock.listen = self.listen
        message_handling_mock = Mock()
        with patch('chatbot.bot.VkApi'), \
                patch('chatbot.bot.VkBotLongPoll', return_value=long_poll_listen_mock), \
                patch('chatbot.bot.logging'):
            bot = ChatBot('', '')
            bot.message_handling = message_handling_mock
            bot.run()
            message_handling_mock.assert_called_once()

    def test_message_handling(self):
        event = Mock()
        event.type = self.ROW_EVENT['type']
        event.message = Mock()
        event.message.from_id = self.ROW_EVENT['object']['message']['from_id']
        event.message.text = self.ROW_EVENT['object']['message']['text']
        get_message_response_mock = Mock()
        with patch('chatbot.bot.VkBotEventType') as VkBotEventType, \
                patch('chatbot.bot.ChatBotDataBase'), \
                patch('chatbot.bot.logging'):
            VkBotEventType.MESSAGE_NEW = 'message_new'
            bot = ChatBot('', '')
            bot.get_message_response = get_message_response_mock
            bot.message_handling(event)
            get_message_response_mock.assert_called_once_with(event=event)

    def test_message_response(self):
        event = Mock()
        event.type = self.ROW_EVENT['type']
        event.message = Mock()
        event.message.from_id = self.ROW_EVENT['object']['message']['from_id']
        event.message.text = self.ROW_EVENT['object']['message']['text']
        send_message_mock = Mock()
        with patch('chatbot.bot.VkBotEventType'), patch('chatbot.bot.logging'):
            bot = ChatBot('', '')
            bot.send_message = send_message_mock
            bot.get_message_response(event=event)
            send_message_mock.assert_called_once_with(
                message_text='Привет!',
                user_id=8023886
            )

    def test_send_message(self):
        pass
