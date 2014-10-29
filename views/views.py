import urllib
import json
import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext.ndb import metadata

from models.models import * 
from google.appengine.ext.ndb.model import IntegerProperty
from jinja2._markupsafe import Markup

classModels = {'Client':Client, 'Fruta':Fruta, 'Porcion':Porcion, 'Precio':Precio}
keyDefs = {'Client':['nombre','negocio'], 'Fruta':['nombre'], 'Porcion':['valor','unidades'], 'Precio':['fruta','porcion','cliente']}
uiConfig = {'Client':[{'id':'nombre','ui':'Nombre'},
                       {'id':'negocio','ui':'Negocio'},
                       {'id':'ciudad','ui':'Ciudad'},
                       {'id':'direccion','ui':'Direccion'},
                       {'id':'telefono','ui':'Telefono'},
                       {'id':'nit','ui':'NIT'},
                       {'id':'diasPago','ui':'Dias para pago'}
                       ],
            'Fruta':[{'id':'nombre','ui':'Nombre'}],
            'Porcion':[{'id':'valor','ui':'Porcion'},
                       {'id':'unidades','ui':'Unidades'}],
            'Precio':[{'id':'fruta','ui':'Fruta'},
                      {'id':'porcion','ui':'Porcion'},
                      {'id':'cliente','ui':'Cliente'},
                      {'id':'precio','ui':'Precio'}
                      ]
            }

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('.\\templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class ShowEntities(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        template_values = {'entity_class': entity_class}
        template = JINJA_ENVIRONMENT.get_template('showEntities.html')
        self.response.write(template.render(template_values))

def getColumns(entity_class):
    columns=[]
    for column in uiConfig[entity_class]:
        columns.append({ 'field' : column['id'], 'name' : column['ui']})
    return columns


class EntityData(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        entity_query = classModels[entity_class].query()#ancestor=ndb.Key(entity_class, entity_class))
        entities = entity_query.fetch()
        records=[]
        for entity in entities:
            dicc = entity.to_dict()
            dicc['id'] = entity.key.id()
            records.append(dicc)
        response = {'columns':getColumns(entity_class), 'records':records}
        self.response.write(json.dumps(response))        

class Home(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render())

def getKey(entity_class,dicc):
    key = ''
    for keypart in keyDefs[entity_class]:
        key = key + str(dicc[keypart])
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
    entity = classModels[entity_class].get_by_id(key, ndb.Key(entity_class, entity_class))
    if entity:
        entity.populate(**values)
        entity.put()
        return {'message':"Updated",'key':key}
    else:
        classModels[entity_class].get_or_insert(key, parent=ndb.Key(entity_class, entity_class), **values)
        return {'message':"Created",'key':key}

class SaveEntity(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        entity_class = values.pop("entity_class")
        for key,value in values.iteritems():
            values[key.replace(entity_class,'')] = values.pop(key)
        response = {};
        try:
            response = create_entity(entity_class,values)
        except Exception as ex:
            self.response.out.write(ex.message)
            return 
        self.response.out.write(json.dumps(response))

def tagForField(entity_class, prop):
    tag = ''
    if type(prop['type']) == ndb.KeyProperty:
        tag = "<select id='" + prop['id'] + entity_class +"' data-dojo-type='dijit/form/Select'>"
        options = classModels[prop['type']._kind].query().fetch()
        for option in options:
            dicc = option.to_dict()
            option_value = str(getKey(prop['type']._kind, dicc))
            tag += "<option value='" + option_value + "'>" + option.rotulo + '</option>'
        tag += "</select>" 
    else:
        tag = '<input type="text" id="' + prop['id'] +  entity_class +'" name="'+ prop['id'] +  entity_class +'" required="true" data-dojo-type="dijit/form/ValidationTextBox"/>'
    return Markup(tag)

JINJA_ENVIRONMENT.globals['tagForField']=tagForField

def fieldsInfo(entity_class):
    props = classModels[entity_class]._properties
    fields = uiConfig[entity_class]
    for field in fields:
        field['type']=props[field['id']]
    return fields

class AddEntity(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        template_values = {'entity_class': entity_class, 'fields': fieldsInfo(entity_class)}
        template = JINJA_ENVIRONMENT.get_template('addEntity.html')
        self.response.write(template.render(template_values))

class DeleteEntity(webapp2.RequestHandler):        
    def post(self):
        key = self.request.POST.get('key')
        entity_class = self.request.POST.get('entity_class')
        try:
            entity = classModels[entity_class].get_by_id(key,ndb.Key(entity_class, entity_class))
            entity.key.delete()
        except Exception as ex:
            self.response.out.write(ex.message)
            return
        self.response.out.write("Se elimino exitosamente: " + entity_class + " " + key)        
