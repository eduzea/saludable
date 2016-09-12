import webapp2
import logging
from google.appengine.api import mail
from models.models import Factura
from datetime import datetime

import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class FacturasVencidas(webapp2.RequestHandler):
    def get(self):
        facturas = Factura.query(Factura.fechaVencimiento < datetime.today(), Factura.pagada == False).fetch()
        clienteFacturas = {}
        for factura in facturas:
            if factura.cliente.get() is None:
                logging.debug('Bad Cliente in factura: ' + str(factura.numero))
                continue
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
        
        self.response.write(html)
            
def sendEmail(data):
    total = sum([factura['monto'] for factura in data['facturas']])
    data['total'] = '{:,}'.format(total)
    message = mail.EmailMessage(
    sender = 'saludable-foods-sas@appspot.gserviceaccount.com',
    subject= "Facturas vencidas con Salud-Able Foods - " + datetime.today().strftime('%m/%d/%Y'))

    message.to = data['email']
    template = JINJA_ENVIRONMENT.get_template('FacturasVencidas.html')
    message.html = template.render(data)
#     message.send()
    return message.html
                  


app = webapp2.WSGIApplication([('/facturasVencidas', FacturasVencidas)])