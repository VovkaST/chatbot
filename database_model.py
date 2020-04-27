from datetime import datetime
import peewee
from database import DialogsTable, EventsTable, db_handler, EventVisitorsTable
from exceptions import DuplicateKeyError, NotNullValueError


def insert_dialog(user_id, user_name=None, name=None):
    """
    Создать новую запись диалога в БД

    :param int user_id: id пользователя
    :param str user_name: Имя пользователя (со страницы)
    :param str name: Имя пользователя (как представился лично)
    """
    try:
        DialogsTable.insert({'user_id': user_id, 'user_name': user_name, 'name': name}).execute()
    except peewee.IntegrityError as exc:
        db_handler.rollback()
        if 'duplicate key value violates' in exc.args[0]:
            raise DuplicateKeyError
        elif 'violates not-null constraint' in exc.args[0]:
            raise NotNullValueError


def update_dialog(user_id, **kwargs):
    """
    Обновить данные в таблице диалогов

    :param int user_id: id пользователя
    :param dict kwargs: Словарь {'имя поля': 'значение'}
    """
    DialogsTable \
        .update(kwargs) \
        .where(DialogsTable.user_id == user_id) \
        .execute()


def update_last_dialog(user_id):
    """
    Обновить время последнего диалога с пользователем в таблице

    :param int user_id: id пользователя
    """
    DialogsTable \
        .update(last_dialog=datetime.now()) \
        .where(DialogsTable.user_id == user_id) \
        .execute()


def update_user_state(user_id, scenario_name, step_name, context):
    """
    Установить значения нахождения пользователя в сценарии

    :param int user_id: id пользователя
    :param str scenario_name: Имя сценария
    :param str step_name: Имя шага в сценарии
    :param dict context: Контекст сценария
    """
    DialogsTable \
        .update(scenario_state={'scenario_name': scenario_name, 'step_name': step_name, 'context': context}) \
        .where(DialogsTable.user_id == user_id) \
        .execute()


def clear_user_state(user_id):
    """
    Сбросить пользователя из состояния нахождения в сценарии

    :param int user_id: id пользователя
    """
    DialogsTable \
        .update(scenario_state=None) \
        .where(user_id == user_id) \
        .execute()


def get_user_info(user_id):
    """
    Получить информацию о пользователе из БД для инициализации экземпляра класса VkUser.
    возвращается словарь вида:
      {'user_name': user.user_name,
       'name': user.name,
       'email': user.email,
       'scenario_state': user.scenario_state}

    :param int user_id: id пользователя
    :return dict:
    """
    result = {'user_name': None,
              'name': None,
              'email': None,
              'scenario_state': None}
    user = DialogsTable \
        .select(DialogsTable.user_name, DialogsTable.name, DialogsTable.email, DialogsTable.scenario_state) \
        .where(DialogsTable.user_id == user_id)
    if user.count():
        user = user.first()
        result = {'user_name': user.user_name,
                  'name': user.name,
                  'email': user.email,
                  'scenario_state': user.scenario_state}
    return result


def get_closest_event():
    """
    Получить ближайшее мероприятие из БД

    :return EventsTable: Строка результата поиска
    """
    event = EventsTable\
        .select()\
        .where(EventsTable.date >= datetime.now())\
        .order_by(EventsTable.date)\
        .limit(1)
    return event.first()


def event_registration(user_id, event_id):
    """
    Регистрация (и запись в базу) пользователя на событие

    :param int user_id: id пользователя
    :param int event_id: id события
    """
    try:
        EventVisitorsTable.insert({'user_id': user_id, 'event_id': event_id}).execute()
    except peewee.IntegrityError as exc:
        db_handler.rollback()
        if 'duplicate key value violates' in exc.args[0]:
            raise DuplicateKeyError
        elif 'violates not-null constraint' in exc.args[0]:
            raise NotNullValueError


if __name__ == '__main__':
    # user_id = 8023886
    # update_user_state(user_id=8023886, scenario_name='registration', step_name='step1')

    # update_last_dialog(user_id=8023886)
    # res = DialogsTable \
    #     .select(DialogsTable.scenario_state) \
    #     .where(DialogsTable.user_id == user_id)
    # print(type(res.first().scenario_state))

    # print(is_user_in_scenario_state(user_id))
    from vk_user import VkUser

    u = VkUser(user_id=8023886)
    print(u)
