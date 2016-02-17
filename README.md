#FunPayParser
Parser for funpay.ru
Script parsing website every 2 hour and collecting in data base (sqlite)

Ищу желающих проанализировать полученные данные

##dependencies
* __python 3+__ 
* [grab](http://docs.grablib.org/en/latest/usage/installation.html) - spider and parser
* [peewee](http://docs.peewee-orm.com/en/latest/) - ORM
* [dateparser](https://dateparser.readthedocs.org/en/latest/) - for easy parse date and times

##structure
* __main.py__ - start file
* __MainSpider.py__ - parser
* __ModelDB.py__ - model for DB