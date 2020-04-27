import database_model
from exceptions import UserStateError


class UserState:
    """ Состояние пользователя внутри сценария. """
    def __init__(self, scenario_name, step_name, context: dict = None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}


class VkUser:
    def __init__(self, user_id):
        """
        Пользователь ВК.
        Расширенный вариант. Работает с БД, которая пополняется ботом.
        Все данные, получаемые экземпляром класса, сохраняются в БД.

        :param int user_id: id пользователя
        """
        self._user_id = user_id
        self._user_name = None
        self._name = None
        self._email = None
        self._scenario_state = None
        self._sync_user_info_with_db()

    def _sync_user_info_with_db(self):
        """ Получить данные о пользователе из БД """
        info = database_model.get_user_info(user_id=self.user_id)
        self._user_name = info['user_name']
        self._name = info['name']
        self._email = info['email']
        if info['scenario_state'] is not None:
            self._scenario_state = UserState(**info['scenario_state'])
        else:
            self._scenario_state = None

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        database_model.insert_dialog(user_id=value)
        self._user_id = value

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, value):
        database_model.update_dialog(user_id=self.user_id, **{'user_name': value})
        self._user_name = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        database_model.update_dialog(user_id=self.user_id, **{'name': value})
        self._name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        database_model.update_dialog(user_id=self.user_id, **{'email': value})
        self._email = value

    @property
    def scenario_state(self):
        return self._scenario_state

    @scenario_state.setter
    def scenario_state(self, value):
        if not isinstance(value, UserState) and value is None:
            UserStateError('User state must be a UserState instance or NoneType')
        if isinstance(value, UserState):
            database_model.update_user_state(user_id=self.user_id,
                                             scenario_name=value.scenario_name, step_name=value.step_name,
                                             context=value.context)
        elif value is None:
            database_model.clear_user_state(user_id=self.user_id)
        self._scenario_state = value

    def is_need_to_collect_user_info(self):
        return not all([self.user_name])


if __name__ == '__main__':
    user = VkUser(user_id=8023886)
    print(user.user_name)
