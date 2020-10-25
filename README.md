# FunPayParser
Parser for [funpay.ru](http://funpay.ru)
Script parsing website every 2 hour and collecting in data base (sqlite)

---

## dependencies
* __python 3+__ 
* [grab](http://docs.grablib.org/en/latest/usage/installation.html) - spider and parser
* [peewee](http://docs.peewee-orm.com/en/latest/) - ORM
* [dateparser](https://dateparser.readthedocs.org/en/latest/) - for easy parse date and times

## structure
* __main.py__ - start file
* __MainSpider.py__ - parser
* __ModelDB.py__ - model for DB

## history
version | date | description
--- | --- | ---
__1.0__ | 4.02.2016 | 
__1.1__ | 28.02.2016 | update together funpay
__1.2__ | 28.04.2016 | update together funpay
__1.3__ | 11.05.2016 | update together funpay
__1.4__ | 18.12.2016 | + all servers option
