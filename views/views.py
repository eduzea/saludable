import urllib
import webapp2
import jinja2
from google.appengine.api import users

from models.models import * 

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('.\\templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def create_client(nombre, ciudad, direccion, telefono,nit,diasPago):
        client = Client(parent = clientbook_key(DEFAULT_CLIENTBOOK_NAME),name=nombre,city=ciudad,address=direccion)
        client.phone = telefono
        client.NIT = nit
        client.days2pay = diasPago
        client.put()

class Clients(webapp2.RequestHandler):
    def get(self):
        clients_query = Client.query(
            ancestor=guestbook_key(DEFAULT_CLIENTBOOK_NAME))
        clients = clients_query.fetch(10)

        template_values = {
            'clients': clients
        }

        template = JINJA_ENVIRONMENT.get_template('clients.html')
        self.response.write(template.render(template_values))

class Home(webapp2.RequestHandler):
    def get(self):
        clients_query = Client.query(
            ancestor=guestbook_key(DEFAULT_CLIENTBOOK_NAME))
        clients = clients_query.fetch(10)

        template_values = {
            'clients': clients
        }
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_values))
        
class AddClient(webapp2.RequestHandler):        
    def post(self):
        nombre = self.request.POST.get('nombre')
        ciudad = self.request.POST.get('ciudad')
        direccion = self.request.POST.get('direccion')
        telefono = self.request.POST.get('telefono')
        nit = self.request.POST.get('nit')
        diasPago = self.request.POST.get('diasPago')
        try:
            create_client(nombre, ciudad, direccion, telefono, nit, diasPago)
        except Exception as ex:
            self.response.out.write(ex.message)
            return
        self.response.out.write("Cliente creado exitosamente")
