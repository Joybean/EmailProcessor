#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import re
from operator import attrgetter, itemgetter

from EmailUtility import EmailUtility
from EmailUtility import EmailInfo
from LogHelper import LogHelper

class TrainTicketHandler(object):

    def __init__(self, server='', user='', passwd=''):
        self.server = server
        self.user = user
        self.passwd = passwd
        self.nTopMails = 0
        self.log = LogHelper().get_logger('TrainTicketHandler')

    def get_account_info(self):
        if self.server == '':
            self.server = input("server (e.g. pop3.163.com): ")
        if self.user == '':
            self.user = input('account (e.g. youremail@163.com): ')
        if self.passwd == '':
            self.passwd = getpass.getpass('password: ' )
        self.nTopMails = int(input('how many mails to retrieve: '))

    def get_tickets(self):
        self.get_account_info()
        mailSrv = EmailUtility(self.server, self.user, self.passwd)
        headerList = mailSrv.get_latest_mails(self.nTopMails, topLineOnly=True)
        ticketMailSNs = []
        for rsp, mail, size, sn in headerList:
            mailInfo = EmailInfo(mail)
            try:
                self.log.debug('mail[%d].subject: %s \tdate:%s' % (sn, mailInfo.get_subject(), mailInfo.get_date()))
                if mailInfo.get_subject().find('网上购票系统-用户支付通知') > -1:
                    ticketMailSNs.append(sn)
            except Exception as ex:
                print('get_tickets except: ', rsp, size, sn)
                print(ex)
        self.log.info('%d mail is found!' % len(ticketMailSNs))
        self.log.debug(ticketMailSNs)

        ticketMails = mailSrv.get_mails(ticketMailSNs)
        self.log.debug('%d mail is received.' % len(ticketMails))
        tickets = []
        for rsp, mail, size, sn in ticketMails:
            mailInfo = EmailInfo(mail)
            content = mailInfo.get_content()
            p = '\\d\\.(.*?)[，,](.*?)开[，,](.*?)[，,](.*?)列车[，,](.*?)[，,](.*?)[，,]票价(.*?)元'
            ms = re.findall(p, content)
            if ms:
                tickets.extend([TicketInfo(m[0], m[1], m[2], m[3], m[4], m[5], m[6], mailInfo.get_date()) for m in ms])
        sortedTickets = sorted(tickets, key=attrgetter('date'), reverse=True)
        for x in sortedTickets:
            self.log.info(str(x))

class TicketInfo(object):

    def __init__(self, owner, date, fromto, trainno, seatno, seattype, price, bookdate):
        self.owner = owner
        self.date = date
        self.fromto = fromto
        self.trainno = trainno
        self.seatno = seatno
        self.seattype = seattype
        self.price = price
        self.bookdate = bookdate

    def __repr__(self):
        return repr((self.owner, self.date, self.fromto, self.trainno, self.seatno, self.seattype, self.price, self.bookdate))

if __name__ == '__main__':
    ticketHandler = TrainTicketHandler('pop3.163.com', 'zybzyf@163.com')
    ticketHandler.get_tickets()
