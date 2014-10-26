import urllib
import json
import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext.ndb import metadata

from models.models import * 
from google.appengine.ext.ndb.model import IntegerProperty

classModels = {'Client':Client, 'Fruta':Fruta}
keyDefs = {'Client':['nombre','negocio'], 'Fruta':['nombre']}

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

def getKey(entity_class,entity):
    key = ''
    for keypart in keyDefs[entity_class]:
        key = key + entity[keypart]
    return ''.join(key.split())
        
def check_types(entity_class, values):
    props = classModels[entity_class]._properties
    for key, value in props.iteritems():
        if type(value) is IntegerProperty:
            values[key] = int(values[key])
    return values
            

def create_entity(entity_class, values):
    values = check_types(entity_class,values) #All we get from post are strings, so we need to cast as appropriate
    key = getKey(entity_class, values)
    entity = classModels[entity_class].get_by_id(key, clientbook_key(DEFAULT_CLIENTBOOK_NAME))
    
    if entity:
        entity.populate(**values)
        entity.put()
        return "Updated"
    else:
        classModels[entity_class].get_or_insert(key, parent=clientbook_key(DEFAULT_CLIENTBOOK_NAME), **values)
        return "Created"

class SaveEntity(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        entity_class = values.pop("entity_class")
        response = ''
        try:
            response = create_entity(entity_class,values)
        except Exception as ex:
            self.response.out.write(ex.message)
            return
        self.response.out.write(response)

class AddEntity(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        props = list(globals()[entity_class]._properties)
        template_values = {'entity_class': entity_class, 'props':props}
        template = JINJA_ENVIRONMENT.get_template('addEntity.html')
        self.response.write(template.render(template_values))
        
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
        
        
