# -*- coding utf-8 -*-
from peewee import *
import logging

database = SqliteDatabase('Parsing.db', **{})


class BaseModel(Model):
    class Meta:
        database = database

    @classmethod
    def create_or_get(cls, **kwargs):
        try:
            with cls._meta.database.atomic():
                return cls.create(**kwargs), True
        except IntegrityError:
            query = []
            for field_name, value in kwargs.items():
                field = getattr(cls, field_name)
                if field.unique or field.primary_key:
                    query.append(field == value)
            return cls.get(*query), False


class Parsings(BaseModel):
    id = PrimaryKeyField(primary_key=True, unique=True)  # IDENTITY
    time = DateTimeField()

    class Meta:
        db_table = 'Parsings'


class PriceFor(BaseModel):
    id = PrimaryKeyField(primary_key=True, unique=True)  # IDENTITY
    price = CharField()

    class Meta:
        db_table = 'PriceFor'


class Games(BaseModel):
    id = PrimaryKeyField(primary_key=True, unique=True)  # IDENTITY
    name = CharField()
    moneyName = CharField()

    class Meta:
        db_table = 'Games'


class Servers(BaseModel):
    id = PrimaryKeyField(primary_key=True, unique=True)  # IDENTITY
    game = ForeignKeyField(Games)
    name = CharField()

    class Meta:
        db_table = 'Servers'


class Sides(BaseModel):
    id = PrimaryKeyField(primary_key=True, unique=True)  # IDENTITY
    game = ForeignKeyField(Games)
    name = CharField()

    class Meta:
        db_table = 'Sides'


class Users(BaseModel):
    id = PrimaryKeyField(primary_key=True, unique=True)  # IDENTITY
    name = CharField()
    regdata = DateTimeField()
    money = IntegerField()

    class Meta:
        db_table = 'Users'


class Data(BaseModel):
    id = PrimaryKeyField(primary_key=True, unique=True)  # IDENTITY
    server = ForeignKeyField(Servers)
    user = ForeignKeyField(Users)
    side = ForeignKeyField(Sides, null=True)
    time = ForeignKeyField(Parsings)
    pricefor = ForeignKeyField(PriceFor)
    amount = IntegerField()
    price = DoubleField()

    class Meta:
        db_table = 'Data'


def check_conformity_games():
    for column in database.get_columns('Games'):
        if column.name == 'moneyName':
            return True
    return False


def migrate_games():
    try:
        database.execute_sql('ALTER TABLE Games ADD COLUMN moneyName VARCHAR(255)')
    except OperationalError as e:
        return False
    return True


MIGRATE_GAMES = False


def GetMigrateStatus():
    return MIGRATE_GAMES


def SetMigrateStatus(status):
    global MIGRATE_GAMES
    MIGRATE_GAMES = status


def init_tables():
    database.connect()
    database.create_tables([Parsings, PriceFor, Games, Sides, Servers, Users, Data], True)
    if not check_conformity_games():
        if migrate_games():
            logging.info('alter table succesfully')
            SetMigrateStatus(True)
