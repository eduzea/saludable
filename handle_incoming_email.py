import logging

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2
from models.models import CuentaBancaria, SaldoCuentaBancaria
from google.appengine.ext.ndb import Key
from datetime import datetime
import time
import email.utils


class SaldoSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender)
        subject = mail_message.subject
        if subject.find('Notificacion Saldo Diario') != -1:
            body = mail_message.body.decode()
            lines = body.split('\n')
            saldo = 0
            for line in lines:
                print line
                if '***' in line:
                    cuentaNum = line.split('*')[-1].strip(':')
                    cuentas = CuentaBancaria.query().fetch()
                    cuenta = [cuenta.key for cuenta in cuentas if cuentaNum in cuenta.numero]
                    if len(cuenta) > 0:
                        cuenta = cuenta[0]
                if 'saldo' in line:
                    saldo = int(line.split()[-1].split('.')[0].replace(',', ''))
                    saldoEntity = SaldoCuentaBancaria(cuenta = cuenta,
                                        fecha =  datetime.fromtimestamp(time.mktime(email.utils.parsedate(mail_message.date))),
                                        saldo = saldo)
                    saldoEntity.put()
            
        logging.debug('Done!')
              
app = webapp2.WSGIApplication([SaldoSenderHandler.mapping()], debug=True)

