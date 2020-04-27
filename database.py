from datetime import datetime
from playhouse.sqlite_ext import JSONField, Model
from local_settings import PG_USER, PG_PASSWORD, PG_DB_NAME, PG_HOST, PG_PORT
import peewee


db_handler = peewee.PostgresqlDatabase(database=PG_DB_NAME, user=PG_USER, password=PG_PASSWORD,
                                       host=PG_HOST, port=PG_PORT, autocommit=True)


class BaseModel(Model):
    """ Базовый класс модели таблиц """
    class Meta:
        database = db_handler


class DialogsDatabase:
    """
    Класс работы с БД PostgreSQL 10.5.
    """

    def __init__(self):
        self.db = db_handler


database = DialogsDatabase()


class DialogsTable(BaseModel):
    """
    История диалогов
    """
    class Meta:
        db_table = 'dialogs'
        db = database

    user_id = peewee.BigIntegerField(primary_key=True, help_text='id пользователя')
    user_name = peewee.TextField(null=True, help_text='Имя пользователя (со страницы)')
    name = peewee.TextField(null=True, help_text='Имя пользователя (как представился лично)')
    email = peewee.TextField(null=True, help_text='Электронная почта')
    scenario_state = JSONField(null=True, help_text='Состояние работы по сценарию')
    first_dialog = peewee.DateTimeField(default=datetime.now, help_text='Дата и время первого диалога')
    last_dialog = peewee.DateTimeField(default=datetime.now, help_text='Дата и время последнего диалога')


class EventsTable(BaseModel):
    """
    События, о которых сообщает бот
    """
    class Meta:
        db_table = 'events'
        db = database

    event_id = peewee.AutoField(primary_key=True)
    title = peewee.TextField(help_text='Название мероприятия')
    date = peewee.DateField(help_text='Дата проведения мероприятия')
    location = peewee.TextField(help_text='Место проведения мероприятия')
    map_point = peewee.TextField(help_text='Позиция на карте (ссылка на Яндекс.Карты)')
    note = peewee.TextField(help_text='Примечание')


class EventVisitorsTable(BaseModel):
    """
    Регистрация на события
    """
    class Meta:
        db_table = 'event_visitors'
        db = database
        primary_key = peewee.CompositeKey('event_id', 'user_id')

    event_id = peewee.ForeignKeyField(EventsTable, to_field='event_id', backref='event',
                                      on_delete='Cascade', on_update='Cascade')
    user_id = peewee.ForeignKeyField(DialogsTable, to_field='user_id', backref='user',
                                     on_delete='Cascade', on_update='Cascade')


DialogsTable.create_table()
EventsTable.create_table()
EventVisitorsTable.create_table()


if __name__ == '__main__':
    db = DialogsDatabase()
    EventsTable.insert_many([
        {'title': 'Конференция Moscow Python Meetup №73',
         'date': datetime.strptime('2020-04-01', '%Y-%m-%d').date(),
         'location': 'БЦ "Олимпия Парк", Ленинградское ш. 39Ас2',
         'map_point': 'https://yandex.ru/maps/213/moscow/?ll=37.483073%2C55.837125&mode=search&oid=1807776059&ol=biz&z=17',
         'note': 'Регистрация с 10:00 до 11:00'},
        {'title': 'Конференция Moscow Python Meetup №74',
         'date': datetime.strptime('2020-06-25', '%Y-%m-%d').date(),
         'location': 'БЦ "Олимпия Парк", Ленинградское ш. 39Ас2',
         'map_point': 'https://yandex.ru/maps/213/moscow/?ll=37.483073%2C55.837125&mode=search&oid=1807776059&ol=biz&z=17',
         'note': 'Количество мест ограничено. Необходима предварительная регистрация.'},
    ]).execute()
