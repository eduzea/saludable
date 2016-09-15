import webapp2
import logging
from google.appengine.api import mail
from models.models import Factura
from datetime import datetime
from oauth2client.contrib.appengine import AppAssertionCredentials
from httplib2 import Http
from apiclient.discovery import build
from apiclient import errors
from email.mime.text import MIMEText
import base64
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class FacturasVencidas(webapp2.RequestHandler):
    def get(self):
        logging.debug('Running cron job at: ' + str(datetime.today()))
        facturas = Factura.query(Factura.fechaVencimiento < datetime.today(), 
                                 Factura.pagada == False).fetch()
        clienteFacturas = {}
        for factura in facturas:
            if factura.cliente.get() is None:
                logging.debug('Bad Cliente in factura: ' + str(factura.numero))
                continue
            if factura.cliente.get().activo == False: continue
            email = factura.cliente.get().email
            delta = datetime.today() - factura.fechaVencimiento
            vencida = {'numero': factura.numero,
                       'monto':factura.total,
                       'expedicion': factura.fecha,
                       'vencimiento':factura.fechaVencimiento.date(),
                       'vencidos':delta.days,
                       }
            cliente = factura.cliente.get().nombre
            if cliente in clienteFacturas:
                clienteFacturas[cliente]['facturas'].append(vencida)
            else:
                clienteFacturas[cliente]={'email':'eduzea@gmail.com','cliente': cliente, 'fecha':datetime.today().date(), 'facturas':[vencida]}
                
        for cliente in clienteFacturas.keys():
            html = sendEmail(clienteFacturas[cliente])
            logging.debug('Sending email to: ' + cliente)
        
        self.response.write(html)
            
def sendEmail(data):
    message = mail.EmailMessage(
        sender = 'saludable-foods-sas@appspot.gserviceaccount.com',
        subject= "Facturas vencidas con Salud-Able Foods - " + datetime.today().strftime('%m/%d/%Y')
    )
    message.to = data['email']
    message.html = messageHTML(data)
    message.send()
    return message.html

def messageHTML(data):
    total = sum([factura['monto'] for factura in data['facturas']])
    data['total'] = '{:,}'.format(total)
    template = JINJA_ENVIRONMENT.get_template('FacturasVencidas.html')
    return template.render(data)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

def sendGmail(data):
    credentials = AppAssertionCredentials('https://mail.google.com/')
    delegated_credentials = credentials.create_delegated('servicio@salud-able.com')
    http_auth = delegated_credentials.authorize(Http())
    service = build('gmail', 'v1', http=http_auth)
    subject= "Facturas vencidas con Salud-Able Foods - " + datetime.today().strftime('%m/%d/%Y')
    message = create_message('servicio@salud-able.com', data.email, subject, messageHTML(data))
    send_message(service, 'servicio@salud-able.com', message)
    
    return


app = webapp2.WSGIApplication([('/facturasVencidas', FacturasVencidas)])
