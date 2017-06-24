# -*- coding: utf-8 -*-

import poplib
import email, email.header, email.utils

poplib._MAXLINE=20480

class EmailUtility(object):

    def __init__(self, host, user, passwd, isSSL=False):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.isSSL = isSSL
        self.conn = None

    def __connect(self):
        if self.conn:
            return
        if self.isSSL:
            self.conn = poplib.POP3_SSL(self.host)
        else:
            self.conn = poplib.POP3(self.host)
        self.conn.set_debuglevel(1)
        self.conn.user(self.user)
        self.conn.pass_(self.passwd)

    def __disconnect(self):
        if self.conn:
            self.conn.quit()
            self.conn = None

    def get_total_emails_count(self):
        self.__connect()
        n = self.conn.stat()[0]
        self.__disconnect()
        return n

    def get_latest_mails(self, nMails=1, topLineOnly=True):
        ret = []
        self.__connect()
        nTotalMail, nTotalSize = self.conn.stat()
        for i in range(nTotalMail, nTotalMail - nMails, -1):
            try:
                if topLineOnly == True:
                    rsp, msglines, size = self.conn.top(i, 0)
                else:
                    rsp, msglines, size = self.conn.retr(i)
                ret.append((
                    rsp,
                    '\n'.encode('utf-8').join(msglines),
                    size,
                    i)
                )
            except:
                print('retrieve top mail # %d failed' % i)
        self.__disconnect()
        return ret

    def get_mails(self, snList):
        ret = []
        self.__connect()
        for i in snList:
            print('receive mail %d' % i)
            rsp, msglines, size = self.conn.retr(i)
            ret.append((
                rsp,
                '\n'.encode('utf-8').join(msglines),
                size,
                i)
            )
        self.__disconnect()
        return ret

    def get_mail(self, sn):
        self.__connect()
        rsp, msglines, size = self.conn.retr(sn)
        self.__disconnect()
        return rsp, msglines, size

class EmailInfo(object):

    def __init__(self, mail):
        self.mail = email.message_from_bytes(mail)
        self.subject = None
        self.sender = None
        self.date = None
        self.content = ""

    def get_subject(self):
        if self.subject is None:
            decodedHeader = email.header.decode_header(self.mail['subject'])
            decodedPart, charset = decodedHeader[0]
            self.subject = self.__decode_header_str(decodedPart, charset)
        return self.subject

    def __decode_header_str(self, decodedPart, charset):
        if charset:
            return decodedPart.decode(charset)
        else:
            return decodedPart

    def get_sender(self):
        if self.sender is None:
            decodedHeader = email.header.decode_header(self.mail['From'])
            self.sender = ''
            for decodedBytes, charset in decodedHeader:
                self.sender += self.__decode_header_str(decodedBytes, charset) + ' '
        return self.sender

    def get_date(self):
        if self.date is None:
            decodedHeader = email.header.decode_header(self.mail['Date'])
            decodedBytes, charset = decodedHeader[0]
            self.date = self.__decode_header_str(decodedBytes, charset)
        return self.date

    def get_content(self, message=None):
        if self.content != "":
            return self.content

        if message is None:
            message = self.mail
        if message.is_multipart() :
            for msg in message.get_payload():
                self.get_content(msg)
        else:
            msgtype = message.get_content_type()
            msgcharset = message.get_content_charset()
            if msgtype == 'text/plain' or msgtype == 'text/html':
                try:
                    if msgcharset == 'utf_8':
                        self.content += unicode(message.get_payload(decode=True),msgcharset)
                    elif msgcharset == None:
                        self.content += message.get_payload(decode=True)
                    else:
                        self.content += message.get_payload(decode=msgcharset).decode(msgcharset)
                except:
                    self.content += 'BLANK' + '\n'
            elif msgtype == 'text/base64':
                try:
                    self.content += unicode(base64.decodestring(message.get_payload(), msgcharset))
                except:
                    self.content += 'BLANK' + '\n'
            else:
                self.content += 'UNKOWN TYPE' + '\n'

        return self.content

if __name__ == '__main__':
    util = EmailUtility('pop3.163.com', 'zybzyf@163.com', '')
    util.get_mail(2637)