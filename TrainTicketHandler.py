#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import re
from operator import attrgetter, itemgetter
import smtplib
from datetime import datetime

from EmailUtility import EmailUtility
from EmailUtility import EmailInfo
from LogHelper import LogHelper

class TrainTicketHandler(object):

    def __init__(self, server='', user='', passwd='', nTopMails=50):
        self.server = server
        self.user = user
        self.passwd = passwd
        self.nTopMails = nTopMails
        self.log = LogHelper().get_logger('TrainTicketHandler')

    def get_account_info(self):
        if self.server == '':
            self.server = input("server (e.g. pop3.163.com): ")
        if self.user == '':
            self.user = input('account (e.g. youremail@163.com): ')
        if self.passwd == '':
            self.passwd = getpass.getpass('password: ' )
        if self.nTopMails == 0:
            self.nTopMails = int(input('how many mails to retrieve: '))

    def get_tickets(self):
        self.get_account_info()
        mailSrv = EmailUtility(self.server, self.user, self.passwd)
        headerList = mailSrv.get_latest_mails(self.nTopMails, topLineOnly=True)
        ticketMailSNs = []
        tickets = []
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

        for rsp, mail, size, sn in ticketMails:
            mailInfo = EmailInfo(mail)
            content = mailInfo.get_content()
            p = '\\d\\.(.*?)[，,](.*?)开[，,](.*?)[，,](.*?)列车[，,](.*?)[，,](.*?)[，,]票价(.*?)元'
            ms = re.findall(p, content)
            if ms:
                new_tickets = [TicketInfo(m[0], m[1], m[2], m[3], m[4], m[5], m[6], mailInfo.get_date()) for m in ms]
                tickets.extend([t for t in new_tickets if datetime.strptime(t.leave_date, '%Y年%m月%d日%H:%M')  > datetime.now()])
        sortedTickets = sorted(tickets, key=attrgetter('leave_date'))
        for x in sortedTickets:
            self.log.info(str(x))

        return sortedTickets

class TicketInfo(object):

    def __init__(self, owner, leave_date, fromto, trainno, seatno, seattype, price, book_date):
        self.owner = owner
        self.leave_date = leave_date
        self.fromto = fromto
        self.trainno = trainno
        self.seatno = seatno
        self.seattype = seattype
        self.price = price
        self.book_date = book_date

    def to_dict(self):
        return {
            'owner': self.owner,
            'fromto': self.fromto,
            'trainno': self.trainno,
            'seatno': self.seatno,
            'seattype': self.seattype,
            'price': self.price,
            'book_date': self.book_date,
            'leave_date': self.leave_date
        }

    def __repr__(self):
        return repr((self.owner, self.leave_date, self.fromto, self.trainno, self.seatno, self.seattype, self.price, self.book_date))

def send_email(smtp_server, email, passwd, tickets):
    msg = 'From: %s\r\nTo:%s\r\nSubject:TrainTicketsInfo\r\n\r\n' % (email, email) + '\n'.join([
        '%(date)s\t%(weekday)s\t%(trainno)s\t%(seatno)s \n' % {
            'date': t.leave_date,
            'weekday': translate_week_day(t.leave_date),
            'trainno': t.trainno,
            'seatno': t.seatno
        } for t in tickets
    ])
    # print(msg)
    server = smtplib.SMTP()
    server.set_debuglevel(1)
    server.connect(smtp_server)
    server.login(email, passwd)
    server.sendmail(email, email, msg.encode())
    server.quit()

def translate_week_day(strdate):
    weekday = ['一','二','三','四','五','六','日']
    myDate = datetime.strptime(strdate, '%Y年%m月%d日%H:%M')
    return '周' + weekday[myDate.weekday()]


if __name__ == '__main__':
    pop3_server = input("pop server (e.g. pop3.163.com): ")
    if pop3_server == '':
        pop3_server = 'pop3.163.com'
    email = input('email (e.g. youremail@163.com): ')
    if email == '':
        email = 'zybzyf@163.com'
    passwd = getpass.getpass('password: ' )
    smtp_server = input('smtp server (e.g. smtp.163.com)')
    if smtp_server == '':
        smtp_server = 'smtp.163.com'

    ticketHandler = TrainTicketHandler('pop3.163.com', email, passwd)
    tickets = ticketHandler.get_tickets()
    for t in tickets:
        print('%(leave_date)s\t%(trainno)s\t%(seatno)s \n' % t.to_dict())

    send_email(smtp_server, email, passwd, tickets)
