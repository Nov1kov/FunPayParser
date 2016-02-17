# -*- coding utf-8 -*-
from peewee import *

database = SqliteDatabase('Parsing.db', **{})
#conn = database.get_conn()

class BaseModel(Model):
    class Meta:
        database = database

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

def create_tables():
    database.connect()
    database.create_tables([Parsings, PriceFor, Games, Sides, Servers, Users, Data], True)