import peewee


class DuplicateKeyError(peewee.IntegrityError):
    pass


class NotNullValueError(peewee.IntegrityError):
    pass


class UserStateError(Exception):
    pass
