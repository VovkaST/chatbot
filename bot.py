from random import randint
import difflib
import re

import requests
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import logging
import logging.config
import log_config
import settings
import handlers
from database import DialogsDatabase
from exceptions import DuplicateKeyError
import database_model
from vk_user import UserState, VkUser


class ChatBot:
    """
    Чат-бот для вКонтакте
    Python 3.7.6
    """
    __vk_api_version = '5.103'

    def __init__(self, token, group_id):
        """
        :param str token: Секретный токен доступа приложения ВК
        :param str group_id: id сообщества ВК
        """
        self.token = token
        self.group_id = group_id
        self.vk = None
        self.api = None
        self.bot_longpoll = None
        logging.config.dictConfig(log_config.CONFIG)
        self.log = logging.getLogger('bot')
        DialogsDatabase()
        self.dialogs = dict()

    @staticmethod
    def words_matcher(standard, patterns, min_ratio):
        """
        Функция попытки определения контекста фразы по ключевым словам

        :param list standard: список эталонных слов, для которых устанавливается схожесть
        :param list patterns: список слов, схожесть которых устанавливается с эталонными
        :param float min_ratio: минимальный порог схожести от 0 до 1
        :return:
        """
        ratio = lambda w1, w2: difflib.SequenceMatcher(None, w1, w2).ratio() >= min_ratio
        for standard in standard:
            if any(ratio(standard.lower(), pattern.lower()) for pattern in patterns):
                return True
        return False

    def connect(self):
        """ Соединение с ВК """
        self.vk = VkApi(token=self.token)
        self.api = self.vk.get_api()
        self.bot_longpoll = VkBotLongPoll(vk=self.vk, group_id=self.group_id)
        self.log.info('Connected to VK and started to listen to')

    def run(self):
        """ Запуск бота """
        try:
            self.connect()
            for event in self.bot_longpoll.listen():
                if event.type.value.startswith('message_'):
                    self.message_handling(event)
        except Exception:
            self.log.exception(Exception)
            print(Exception)

    def message_handling(self, event):
        """
        Обработка событий message_*

        :param VkBotEventType event: Событие VkBotEventType
        """
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.message.from_id
            text = re.sub(pattern=settings.RE_MULTIPLE_SPACES, repl=' ', string=event.message.text.strip())
            self.log.info(f'message from user {user_id}: {text}')
            self.dialogs[user_id] = VkUser(user_id=user_id)
            if self.dialogs[user_id].scenario_state:
                message_text = self.continue_scenario(text=text, user_id=user_id)
            else:
                message_text = self.find_intent(text=text, user_id=user_id)
            self.send_message(message_text=message_text, user_id=user_id)
            self.dialog_to_db(user_id=user_id)
            if self.dialogs[user_id].is_need_to_collect_user_info():
                self.collect_user_info(user_id=user_id)
        elif event.type == VkBotEventType.MESSAGE_TYPING_STATE:
            self.log.info(f'User {event.obj.from_id} is typing...')

    def collect_user_info(self, user_id):
        """
        Собрать дополнительную информацию о собеседнике

        :param user_id: id пользователя
        """
        info = self.api.users.get(user_ids=user_id, fields='photo_50,city', v=self.__vk_api_version)
        user_name = '{} {}'.format(info[0]['last_name'], info[0]['first_name']).strip()
        if user_name:
            self.dialogs[user_id].user_name = user_name

    def find_intent(self, text, user_id):
        """
        Поиск сценария работы

        :param str text: Полученное от пользователя сообщение
        :param user_id: id пользователя
        :return str: Строка сообщения собеседнику для отправки
        """
        for intent in settings.INTENTS:
            needed = False
            if intent['tokens'] is not None:
                needed = self.words_matcher(standard=intent['tokens'],
                                            patterns=re.findall(pattern=r'(\w+)', string=text),
                                            min_ratio=intent['min_ratio'])
            elif intent['re_token'] is not None:
                needed = bool(re.findall(pattern=intent['re_token'], string=text))
            if not needed:
                continue
            if intent['scenario'] is not None:
                return self.start_scenario(scenario_name=intent['scenario'], user_id=user_id)
            elif intent['handler'] is not None:
                handler = getattr(handlers, intent['handler'])
                return handler(user_id=user_id, text=text, content=None)
            else:
                return intent['answer']
        else:
            return settings.DEFAULT_ANSWER

    def start_scenario(self, scenario_name, user_id):
        """
        Начинает новый сценарий.

        :param str scenario_name: Имя сценария
        :param int user_id: id пользователя
        :return str: Строка сообщения собеседнику для отправки
        """
        scenario = settings.SCENARIOS[scenario_name]
        step_name = scenario['first_step']
        self.dialogs[user_id].scenario_state = UserState(scenario_name=scenario_name, step_name=step_name)
        return scenario['steps'][step_name]['context']

    def continue_scenario(self, text, user_id):
        """
        Продолжить сценарий (перейти на следующий шаг или завершить)

        :param str text: Текст сообщения пользователя для проверки
        :param int user_id: id пользователя
        :return str: Строка сообщения собеседнику для отправки
        """
        state = self.dialogs[user_id].scenario_state
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        if 'send_image' in step:
            self.send_image_handle(user_id=user_id, step=step, context=state.context)
        handler = getattr(handlers, step['handler'])
        if handler(user_id=user_id, text=text, context=state.context):
            next_step = steps[step['next_step']]
            message_text = next_step['context'].format(**state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
                self.dialogs[user_id].scenario_state = state
            else:
                if next_step['handler']:
                    handler = getattr(handlers, next_step['handler'])
                    handler(user_id=user_id, text=text, context=state.context)
                if 'send_image' in next_step:
                    self.send_image_handle(user_id=user_id, step=next_step, context=state.context)
                self.dialogs[user_id].scenario_state = None
        else:
            message_text = step['error_response'].format(**state.context)
        return message_text

    def send_image_handle(self, user_id, step, context):
        """
        Обработка шага, у которого есть атрибут отправки сообщения

        :param int user_id: id пользователя-получателя
        :param dict step: Словарь, содержащий текущий шаг сценария
        :param dict context: Контекст выполнения шага
        """
        handler = getattr(handlers, step['send_image'])
        image = handler(context=context)
        self.send_image(image=image, user_id=user_id)

    def send_message(self, user_id, message_text=None, attachment=None):
        """
        Функция отправки сообщения пользователю ВК

        :param int user_id: id пользователя-получателя
        :param str message_text: текст сообщения
        :param str attachment: вложение в сообщение (картинка)
        """
        message_id = randint(1, 2 ** 64)
        try:
            self.api.messages.send(user_id=user_id, random_id=message_id, group_id=self.group_id,
                                   message=message_text, attachment=attachment, v=self.__vk_api_version)
            if message_text:
                self.log.info(f'response to user {user_id}: {message_text}')
            elif attachment:
                self.log.info(f'response to user {user_id}: {attachment}')
        except Exception:
            self.log.exception(Exception)

    def send_image(self, image, user_id):
        """
        Отправить картинку пользователю.

        :param IOBytes image: Картинка для отправки
        :param int user_id: id пользователя-получателя
        """
        upload_url = self.api.photos.getMessagesUploadServer()['upload_url']
        upload_data = requests.post(url=upload_url, files={'photo': ('image.png', image, 'image/png')}).json()
        image_data = self.api.photos.saveMessagesPhoto(**upload_data)
        owner_id = image_data[0]['owner_id']
        media_id = image_data[0]['id']
        attachment = f'photo{owner_id}_{media_id}'
        self.send_message(user_id=user_id, attachment=attachment)

    @staticmethod
    def dialog_to_db(user_id):
        """
        Обновление данных о диалоге с пользователем в БД

        :param int user_id: id пользователя
        """
        try:
            database_model.insert_dialog(user_id=user_id)
        except DuplicateKeyError:
            database_model.update_last_dialog(user_id=user_id)


if __name__ == '__main__':
    from local_settings import VK_ACCESS_TOKEN, VK_GROUP_ID

    bot = ChatBot(token=VK_ACCESS_TOKEN, group_id=VK_GROUP_ID)
    print('Бот запущен...')
    bot.run()
    print('Работа завершена!')
