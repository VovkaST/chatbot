import pathlib
import re

DEFAULT_ANSWER = 'Пока я не на столько умен... 😔 Но это временно! 👍🏻 Скажи что-нибудь еще!'
DEFAULT_DATE_FORMAT = '%d.%m.%Y'
NO_EVENTS_ANSWER = 'В настоящее время нет запланированных мероприятий!'
RE_MULTIPLE_SPACES = re.compile(pattern=r'\s{2,}')
RE_NAME = re.compile(r'^[a-zА-Я].{,24}$', flags=re.IGNORECASE)
RE_EMAIL = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", flags=re.IGNORECASE)
WORK_DIR = pathlib.Path().absolute()

INTENTS = [
    {
        'name': 'Приветствие',
        'tokens': ['привет', 'здорова'],
        'min_ratio': 0.7,
        're_token': None,
        'scenario': None,
        'answer': None,
        'handler': 'handle_hello',
    },
    {
        'name': 'Вежливое приветствие',
        'tokens': None,
        'min_ratio': None,
        're_token': re.compile(pattern='добр(ое|ый|ой|ого) (утр(о|а)|д(ень|ня)|вечер|вечера|ночи)',
                               flags=re.IGNORECASE),
        'scenario': None,
        'answer': None,
        'handler': 'handle_polite_hello',
    },
    {
        'name': 'Дата проведения',
        'tokens': ['когда', 'дата', 'дату', ],
        'min_ratio': 0.8,
        're_token': None,
        'scenario': None,
        'answer': None,
        'handler': 'handle_closest_event_date',
    },
    {
        'name': 'Место проведения',
        'tokens': ['где', 'место', 'адрес', ],
        'min_ratio': 0.6,
        're_token': None,
        'scenario': None,
        'answer': None,
        'handler': 'handle_closest_event_location',
    },
    {
        'name': 'Регистрация',
        'tokens': ['регистраци', 'зарегистрир', 'записаться', 'принять участие', 'участвов'],
        'min_ratio': 0.6,
        're_token': None,
        'scenario': 'registration',
        'answer': None,
        'handler': None,
    },
]

SCENARIOS = {
    'registration': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'context': 'Давайте зарегистрируемся для участия в мероприятии! '
                           'Представьтесь, пожалуйста! Ваше имя будет указано на бейдже.',
                'handler': 'handle_name',
                'error_response': 'Неправильный формат имени: должно начинаться с буквы, длина не более 25 символов.',
                'next_step': 'step2'
            },
            'step2': {
                'context': 'Укажите адрес электронной почты.',
                'handler': 'handle_email',
                'error_response': 'Неправильный формат электронной почты.',
                'next_step': 'step3'
            },
            'step3': {
                'context': 'Регистрация успешно пройдена, {name}! Спасибо! Распечатайте, пожалуйста Ваш билет.',
                'send_image': 'generate_ticket',
                'handler': 'handle_save_data_to_db',
                'error_response': None,
                'next_step': None
            },
        }
    }
}
