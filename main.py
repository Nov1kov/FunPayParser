# coding utf-8

import logging
import sys
from MainSpider import FunPaySpider
from ModelDB import init_tables, Parsings
from datetime import datetime, timedelta
from time import sleep


def GetScanSchedule():
    interval_scan = timedelta(hours=2)
    lastParseTime = Parsings.select().order_by(Parsings.id.desc()).get().time
    timeStart = lastParseTime + interval_scan
    nextTimeParse = timeStart - datetime.now()
    return (timeStart, nextTimeParse)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%H:%M:%S')
    init_tables()
    if len(sys.argv) > 1 and sys.argv[1] == 'forced':
        logging.warning('spider run once and forced')
        bot = FunPaySpider()  # thread_number=2
        bot.run()
        sys.exit(0)

    failedScan = False
    timeStart, nextTimeParse = GetScanSchedule()
    logging.info('scan was started through ' + str(round(nextTimeParse.seconds / 60)) + ' minutes in ' +
                 timeStart.strftime('%H:%M:%S'))
    while True:
        timeStart, nextTimeParse = GetScanSchedule()
        if datetime.now() > timeStart or failedScan:
            failedScan = False
            bot = FunPaySpider()  # thread_number=2
            bot.run()
            timeStart, nextTimeParse = GetScanSchedule()
            if bot.gameCount == 0:
                logging.info('scan failed repeat after 2 min')
                sleep(120)
                failedScan = True
            else:
                logging.info(
                    'Parse ' + str(bot.gameCount) + ' games finish,\nadded ' + str(bot.dataCount) + ' data rows\n' +
                    'New users ' + str(bot.userCount) + ' was added\n' +
                    'Next scan through ' + str(round(nextTimeParse.seconds / 60)) + ' minutes in ' +
                    timeStart.strftime('%H:%M:%S'))
        else:
            sleep(0.5)
