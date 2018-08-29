import webapp2
import logging
from google.appengine.api import mail
from myapp.model.models import Factura, PagoRecibido
from datetime import datetime
from google.appengine.ext import deferred
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
from apiclient import errors
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import base64
import jinja2
from google.appengine.api.mail import EmailMessage
from myapp.controller.controller import getExistencias2
from myapp.initSaludable import dataStoreInterface

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#############################################################################
### Envio automatico de correo con la cartera pendiente a los clientes ###### 
#############################################################################
class FacturasVencidas(webapp2.RequestHandler):
    def get(self):
        return
        logging.debug('Running cron job at: ' + str(datetime.today()))
        facturas = Factura.query(Factura.fechaVencimiento < datetime.today(), 
                                 Factura.pagada == False).fetch()
        logging.debug(len(facturas))
        clienteFacturas = {}
        for factura in facturas:
            cliente = factura.cliente.get()
            if cliente is None:
                logging.debug('Bad Cliente in factura: ' + str(factura.numero))
                continue
            if cliente.activo == False and cliente.diasPago == 0: continue
            email = factura.cliente.get().email
            delta = datetime.today() - factura.fechaVencimiento
            vencida = {'numero': factura.numero,
                       'monto':factura.total,
                       'expedicion': factura.fecha,
                       'vencimiento':factura.fechaVencimiento.date(),
                       'vencidos':delta.days,
                       }
            cliente = factura.cliente.get().nombre
            contacto = factura.cliente.get().contacto
            telefono = factura.cliente.get().telefono
            if cliente in clienteFacturas:
                clienteFacturas[cliente]['facturas'].append(vencida)
            else:
                clienteFacturas[cliente]={'email':email,'contacto': contacto, 'telefono':telefono,'cliente': cliente, 'fecha':datetime.today().date(), 'facturas':[vencida]}
                 
        html=''
        subject= "Facturas vencidas con Salud-Able Foods - " + datetime.today().strftime('%m/%d/%Y')
        for cliente in clienteFacturas.keys():
            body = messageHTML(clienteFacturas[cliente])
#             deferred.defer(sendGmail, clienteFacturas[cliente]['email'], subject, body)
            lastMsgBody = sendGmail(clienteFacturas[cliente]['email'], subject, body)
            logging.debug('Sending email to: ' + cliente)

        self.response.write(lastMsgBody)

def sendGmail(recipient,subject, body):
    scopes=['https://www.googleapis.com/auth/gmail.compose']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('saludable-foods-sas-7c9c1120a32e.json', scopes)
    delegated_credentials = credentials.create_delegated('servicio@salud-able.com')
    http_auth = delegated_credentials.authorize(Http())
    service = build('gmail', 'v1', http=http_auth)
    message = create_message('servicio@salud-able.com', recipient + ',nataljure@salud-able.com,eduzea@gmail.com', subject, body)
    send_message(service, 'servicio@salud-able.com', message)
    return body

def messageHTML(data):
    total = sum([factura['monto'] for factura in data['facturas']])
    data['total'] = '{:,}'.format(total)
    template = JINJA_ENVIRONMENT.get_template('FacturasVencidas.html')
    return template.render(data)

def create_message(sender, to, subject, message_text):
    # Load the image you want to send as bytes
    # path = os.path.join(os.path.split(__file__)[0], 'static/images/SaludAble_logo_small.png')
    img_data = open('SaludAble_logo_small.png', 'rb').read()
    multiPartMsg = MIMEMultipart(_subtype='related')
    
    # Attach the html text
    body = MIMEText(message_text,'html')
    multiPartMsg.attach(body)
    
    # Attach de img
    img = MIMEImage(img_data, 'png')
    img.add_header('Content-Id', '<logo>')  # angle brackets are important
    img.add_header("Content-Disposition", "inline", filename="logo") # David Hess recommended this edit
    multiPartMsg.attach(img)
    
    multiPartMsg['to'] = to
    multiPartMsg['from'] = sender
    multiPartMsg['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(multiPartMsg.as_string())}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error
        
######################################################################################        
##############Snapsot del Inevntario para cada dia ##################################
######################################################################################
class InventarioDiario(webapp2.RequestHandler):
    def get(self):
        records = getExistencias2()
        dataStoreInterface.create_entity('Existencias', {'fecha':datetime.today().date()
                                                         ,'registros':records},True)

######################################################################################
app = webapp2.WSGIApplication([('/facturasVencidas', FacturasVencidas),
                               ('/inventarioDiario', InventarioDiario)])

#This uses appengine Mail api. Just 10 emails x day!
def sendEmail(data):
    message = mail.EmailMessage(
        sender = 'saludable-foods-sas@appspot.gserviceaccount.com',
        subject= "Facturas vencidas con Salud-Able Foods - " + datetime.today().strftime('%m/%d/%Y')
    )
    message.to = data['email']
    message.html = messageHTML(data)
    message.send()
    return message.html