import urllib
import json
import webapp2
import jinja2
from google.appengine.api import users

from models.models import * 

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('.\\templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class TestClient(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('ContentPaneTest.html')
        self.response.write(template.render())

class Clients(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('clients.html')
        self.response.write(template.render())

class ClientData(webapp2.RequestHandler):
    def get(self):
        clients_query = Client.query(ancestor=clientbook_key(DEFAULT_CLIENTBOOK_NAME))
        clients = clients_query.fetch()
        response=[]
        for client in clients:
            dicc = client.to_dict()
            dicc['id'] = client.key.id()
            response.append(dicc)
        self.response.write(json.dumps(response))
        

class Home(webapp2.RequestHandler):
    def get(self):
        clients_query = Client.query(
            ancestor=clientbook_key(DEFAULT_CLIENTBOOK_NAME))
        clients = clients_query.fetch(10)

        template_values = {
            'clients': clients
        }
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_values))
        
def create_client(params):
        key = ''.join(params['nombre'].split())
        client = Client.get_by_id(key,clientbook_key(DEFAULT_CLIENTBOOK_NAME))
        if client:
            client.populate(**params)
            client.put()
            return "Updated"
        else:
            Client.get_or_insert(key,parent=clientbook_key(DEFAULT_CLIENTBOOK_NAME), **params)
            return "Created"

class SaveClient(webapp2.RequestHandler):        
    def post(self):
        nombre = self.request.POST.get('nombre')
        ciudad = self.request.POST.get('ciudad')
        direccion = self.request.POST.get('direccion')
        telefono = self.request.POST.get('telefono')
        nit = self.request.POST.get('nit')
        diasPago = int(self.request.POST.get('diasPago'))
        response =''
        try:
            response = create_client({'nombre':nombre, 'ciudad':ciudad, 'direccion':direccion, 'telefono':telefono, 'nit':nit, 'diasPago':diasPago})
        except Exception as ex:
            self.response.out.write(ex.message)
            return
        self.response.out.write(response)
        
class DeleteClient(webapp2.RequestHandler):        
    def post(self):
        key = self.request.POST.get('key')
        try:
            client = Client.get_by_id(key,clientbook_key(DEFAULT_CLIENTBOOK_NAME))
            client.key.delete()
        except Exception as ex:
            self.response.out.write(ex.message)
            return
        self.response.out.write("Se elimino exitosamente el cliente: " + client.nombre)        
        
class AddClient(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('addClient.html')
        self.response.write(template.render())