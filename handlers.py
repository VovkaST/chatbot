import re
from datetime import datetime
from database_model import get_closest_event, get_user_info, event_registration
from database_model import DuplicateKeyError
from settings import RE_NAME, RE_EMAIL, DEFAULT_DATE_FORMAT, NO_EVENTS_ANSWER
from ticket_maker import TicketMaker


def handle_hello(**kwargs):
    """ Обработка приветствия и формирование ответа с обращением по имени, если такое есть в базе """
    info = get_user_info(user_id=kwargs['user_id'])
    message_text = 'Привет!'
    if info['name']:
        message_text = 'Привет, {}!'.format(info['name'])
    return message_text


def handle_polite_hello(**kwargs):
    """ Обработка вежливого приветствия и формирование ответа с обращением по имени, если такое есть в базе """
    hr = datetime.now().hour
    info = get_user_info(user_id=kwargs['user_id'])
    if 0 <= hr < 6:
        greeting = 'Доброй ночи'
    elif 6 <= hr < 12:
        greeting = 'Доброе утро'
    elif 12 <= hr < 18:
        greeting = 'Добрый день'
    else:
        greeting = 'Добрый вечер'
    if info['name']:
        return '{}, {}!'.format(greeting, info['name'])
    return f'{greeting}!'


def handle_name(**kwargs):
    """ Проверка введенного имени по шаблону """
    if re.match(pattern=RE_NAME, string=kwargs['text']):
        kwargs['context']['name'] = kwargs['text']
        return True
    else:
        return False


def handle_email(**kwargs):
    """ Проверка введенного e-mail по шаблону """
    if re.match(pattern=RE_EMAIL, string=kwargs['text']):
        kwargs['context']['email'] = kwargs['text']
        return True
    else:
        return False


def handle_closest_event_date(**kwargs):
    """ Получение названия и даты ближайшего мероприятия """
    event = get_closest_event()
    if event is not None:
        return f'{event.title} состоится {event.date.strftime(DEFAULT_DATE_FORMAT)}'
    else:
        return NO_EVENTS_ANSWER


def handle_closest_event_location(**kwargs):
    """ Получение места проведения ближайшего мероприятия """
    event = get_closest_event()
    if event is not None:
        return f'{event.title} состоится в {event.location}.\r\n{event.map_point}'
    else:
        return NO_EVENTS_ANSWER


def handle_save_data_to_db(**kwargs):
    """ Сохранение регистрации на мероприятие в БД """
    event = get_closest_event()
    if event is not None:
        try:
            event_registration(user_id=kwargs['user_id'], event_id=event.event_id)
        except DuplicateKeyError:
            return 'Вы уже зарегистрированы на это мероприятие!'


def generate_ticket(**kwargs):
    """
    Генерация билета на мероприятие
    
    :return IOBytes: файл билета
    """
    event = get_closest_event()
    ticket = TicketMaker()
    ticket.write_title(title=event.title)
    ticket.write_name(name=kwargs['context']['name'])
    ticket.write_location(location=f'{event.date.strftime(DEFAULT_DATE_FORMAT)}, {event.location}')
    ticket.write_note(note=event.note)
    ticket.draw_avatar(kwargs['context']['email'])
    return ticket.image_io


if __name__ == '__main__':
    content = {}
    handle_name(text='Жириновский В.В.', content=content)
    handle_email(text='vovka.steel911@mail.ru', content=content)
    print(content)
