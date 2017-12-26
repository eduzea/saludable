import logging

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import webapp2
from models import CuentaBancaria, SaldoCuentaBancaria
from google.appengine.ext.ndb import Key
from datetime import datetime
import time
import email.utils
import re
from myapp import dataStoreInterface

class SaldoSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received message from: " + mail_message.sender + "  at " + str(datetime.now()))
        subject = mail_message.subject
        if 'Notificacion Saldo Diario' in subject:
            body = mail_message.body.decode()
            lines = body.split('\n')
            saldo = 0
            for line in lines:
                try:
                    if '***' in line:
                        cuentaNumRegexp = re.search(re.escape('*******')+'(.*)\:', line)
                        cuentaNum = cuentaNumRegexp.group(1).replace('*','') 
                        cuentas = CuentaBancaria.query().fetch()
                        cuenta = [cuenta.key for cuenta in cuentas if cuentaNum in cuenta.numero]
                        if len(cuenta) > 0:
                            cuenta = cuenta[0]
                        else:
                            logging.debug('No entendi el numero de cuenta. CuentaNum: ' + cuentaNum)
                    if '$' in line:
                        saldoRegexp = re.search('\$(.*)\.', line)
                        saldo = saldoRegexp.group(1).split('.', 1)[0].replace(',','').strip()
                        values = {'cuenta':cuenta, 
                                'fecha': datetime.fromtimestamp(time.mktime(email.utils.parsedate(mail_message.date))),
                                'saldo': int(saldo)}
                        saldoEntity = dataStoreInterface.create_entity('SaldoCuentaBancaria', values)['entity']
                        saldoEntity.put()
                        break
                except Exception as e:
                    logging.debug('Choked on: ' + line)
                    logging.debug('Error: ' + e.message)
                    continue
        logging.info('Processed email!')
              
app = webapp2.WSGIApplication([SaldoSenderHandler.mapping()], debug=True)

