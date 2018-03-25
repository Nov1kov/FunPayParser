# coding utf-8
import logging
import re
from datetime import datetime

from grab.spider import Spider, Task
import dateparser

from utils import parseFloat, parseInt
from ModelDB import Parsings, PriceFor, Games, Servers, Users, Sides, Data, GetMigrateStatus, SetMigrateStatus


class FunPaySpider(Spider):
    initial_urls = ['http://funpay.ru/']

    def prepare(self):
        self.reUserId = re.compile(r'id=(\d+)-')
        self.reGameId = re.compile(r'\/(\d+)\/')
        self.reUserReview = re.compile(r'\ (\d+) ₽')
        self.dataCount = 0
        self.gameCount = 0
        self.userCount = 0
        self.currentParse = Parsings.create(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def task_initial(self, grab, task):
        # CHECK NEW USERS
        self.stopParseUsers = False
        try:
            lastUserId = Users.select().order_by(Users.id.desc()).get().id
        except Users.DoesNotExist:
            self.stopParseUsers = True
            lastUserId = 1
        userId = lastUserId
        maxUserId = lastUserId + 20
        logging.debug('Last user id: ' + str(userId))
        while not self.stopParseUsers:
            # query = Users.select().where(Users.id == userId)
            # if not query.exists():
            yield Task('user', url='http://funpay.ru/users/%d/' % userId, userId=userId)
            userId += 1
            if userId > maxUserId:
                break

        games = dict()

        for elem in grab.doc.select('//div[@class="promo-games-game"]/p[contains(@class, "promo-games-title")]/a'):
            url = elem.node().attrib['href']
            matcher = self.reGameId.search(url)
            game_id = int(matcher.group(1))
            games.setdefault(game_id, ['', ''])[0] = elem.node().text

        for id, params in games.items():
            if GetMigrateStatus():
                game = Games(id=id, name=params[0], moneyName=params[1])
                if Games.select().where(Games.id == id):
                    game.save()
                    logging.info('game updated: ' + str(id) + ' = ' + params[0] + ', ' + params[1])
                else:
                    game.save(True)
                    logging.info('game new save: ' + str(id) + ' = ' + params[0] + ', ' + params[1])
            else:
                game, created = Games.create_or_get(id=id, name=params[0], moneyName=params[1])
                if created:
                    logging.info('game save: ' + str(id) + ' = ' + params[0] + ', ' + params[1])
            url = 'http://funpay.ru/chips/%d/' % id
            yield Task('game', url=url, game=game)

        SetMigrateStatus(False)
        self.gameCount = len(games)

    def task_user(self, grab, task):
        if grab.response.code == 404:
            self.stopParseUsers = True
            logging.debug('user %d not found' % task.userId)
            return

        nickname = ''
        regdata = ''
        for elem in grab.doc.select("//h1[@class='page-header'] | //h1[@class='page-header']/following-sibling::div"):
            if elem.node().tag == 'h1':
                nickname = elem.text()
            elif elem.node().tag == 'div' and len(elem.node().attrib) == 0:
                parse_text = elem.node().text.replace('Зарегистрирован', '')
                regdata = dateparser.parse(parse_text)

        money_user = 0
        for div_elem in grab.doc.select("//body//div[@class='head']"):
            match = self.reUserReview.search(div_elem.text())
            if match:
                money_user += int(match.group(1))

        user, created = Users.create_or_get(id=task.userId,
                                            name=nickname,
                                            money=money_user,
                                            regdata=regdata.strftime('%Y-%m-%d %H:%M:%S'))
        if created:
            self.userCount += 1
            logging.debug('user save: ' + str(task.userId) + ' = ' + nickname + ' money: '
                          + str(money_user) + ' data: ' + regdata.strftime('%Y-%m-%d %H:%M:%S'))

    def task_game(self, grab, task):

        # SERVER NAMES
        servers = []
        for elem in grab.doc.select('//select[@name="server"]/option'):
            server_id = elem.attr('value', '0')
            if server_id != '':
                server_name = elem.text()
                server, created = Servers.create_or_get(id=server_id, name=server_name, game=task.game.id)
                if created:
                    logging.info('server save: ' + str(server_id) + ' = ' + server_name)
                servers.append(int(server_id))

        # SIDES NAME
        data_sides = []
        for elem in grab.doc.select('//select[@name="side"]/option'):
            side_id = elem.attr('value', '0')
            if side_id != '':
                side_name = elem.text()
                side, created = Sides.get_or_create(id=side_id, name=side_name, game=task.game)
                if created:
                    logging.info('side save: ' + str(side_id) + ' = ' + side_name)
                data_sides.append(int(side_id))

        # TABLE NAMES PRICE FOR
        priceFor = None
        elems = grab.doc.select('//table[contains(@class,"table-condensed")]/thead/tr/th[last()]')
        if len(elems) > 0:
            elem = elems[0]
            if elem != None:
                table_name = elem.text()
                priceFor, created = PriceFor.get_or_create(price=table_name)
                if created:
                    logging.info('"price for" save: ' + str(priceFor.id) + ' = ' + table_name)

                    # TABLE DATA
        for elem in grab.doc.select('//table[contains(@class,"table-condensed")]/tbody/tr'):
            if elem.node().tag == 'tr':
                data_href = elem.attr('data-href', '')
                matcher = self.reUserId.search(data_href)
                user_id = int(matcher.group(1))
                serverAttr = elem.attr('data-server', 0)
                if serverAttr == '*':
                    server_ids = servers
                else:
                    server_ids = [int(serverAttr)]

                data_side_attr = elem.attr('data-side', 0)
                if data_side_attr == '*':
                    data_side_ids = data_sides
                else:
                    data_side_ids = [int(data_side_attr)]

                money_summ = 0
                coast = 0
                nick_name = ''
                user_online = False
                columns = []
                for td_elem in elem.node().findall('td'):

                    for div_elem in td_elem.findall('div'):

                        span_elem = div_elem.find('span')
                        if span_elem != None:
                            user_online = True if span_elem.text == 'online' else False
                            nick_name = div_elem.text
                            break

                        _getCoast = parseFloat(div_elem.text)
                        if _getCoast != 0:
                            coast = _getCoast
                            break

                    else:
                        _getNumber = parseInt(td_elem.text)
                        if _getNumber == '':
                            _column = td_elem.text
                            columns.append(_column)
                        else:
                            money_summ = _getNumber

                for server_id in server_ids:
                    for data_side in data_side_ids:
                        data = Data.create(server=server_id,
                                           user=user_id,
                                           side=data_side,
                                           time=self.currentParse.id,
                                           pricefor=priceFor.id,
                                           amount=money_summ,
                                           price=coast)
                        self.dataCount += 1
                        logging.debug(
                            'userid: ' + str(user_id) + ' ' + str(user_online) + ' money: ' + str(money_summ) +
                            " coast: " + str(coast) + " columns: " + str(columns))


if __name__ == '__main__':
    from ModelDB import init_tables

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(message)s',
                        datefmt='%H:%M:%S')
    init_tables()
    bot = FunPaySpider()
    bot.run()
    logging.info('Parse ' + str(bot.gameCount) +
                 ' games finish,\nadded ' + str(bot.dataCount) +
                 ' data rows\n' +
                 'New users ' + str(bot.userCount) + ' was added')
