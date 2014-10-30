import datetime
import json
import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext.ndb import metadata

from models.models import * 
from google.appengine.ext.ndb.model import IntegerProperty, KeyProperty
from jinja2._markupsafe import Markup

classModels = {'Client':Client, 'Fruta':Fruta, 'Porcion':Porcion, 'Precio':Precio}
keyDefs = {'Client':['nombre','negocio'], 'Fruta':['nombre'], 'Porcion':['valor','unidades'], 'Precio':['fruta','porcion','cliente']}
uiConfig = {'Client':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'negocio','ui':'Negocio', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'ciudad','ui':'Ciudad', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'direccion','ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'telefono','ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'nit','ui':'NIT', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'diasPago','ui':'Dias para pago', 'required':'true', 'valid':'dijit/form/NumberTextBox'}
                       ],
            'Fruta':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox'}],
            'Porcion':[{'id':'valor','ui':'Porcion', 'required':'true', 'valid':'dijit/form/NumberTextBox'},
                       {'id':'unidades','ui':'Unidades', 'required':'true', 'valid':'dijit/form/ValidationTextBox'}],
            'Precio':[{'id':'fruta','ui':'Fruta'},
                      {'id':'porcion','ui':'Porcion'},
                      {'id':'cliente','ui':'Cliente'},
                      {'id':'precio','ui':'Precio','required':'true','valid':'dijit/form/NumberTextBox'}
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
        columns.append({ 'field' : column['id'], 'name' : column['ui'], 'style': "text-align: center"})
    return columns

class EntityData(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        entity_query = classModels[entity_class].query()
        entities = entity_query.fetch()
        records=[]
        for entity in entities:
            dicc = entity.to_dict()
            for prop_key, prop_value in dicc.iteritems():
                if type(prop_value) == ndb.Key:
                    try:
                        dicc[prop_key]= dicc[prop_key].get().to_dict()['rotulo']
                    except Exception as e:
                        dicc[prop_key] = "Ya no hay: " + str(prop_value) + ' Considera borrar este registro o recrear ' + str(prop_value)
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
        if type(dicc[keypart]) == ndb.Key:
            key += dicc[keypart].get().to_dict()['rotulo']
        else:
            key += str(dicc[keypart])
    return ''.join(key.split())
        
def check_types(entity_class, values):
    props = classModels[entity_class]._properties
    for key, value in props.iteritems():
        if type(value) is IntegerProperty:
            values[key] = int(values[key])
        if type(value) is KeyProperty:
            key_obj = ndb.Key(value._kind,values[key])
            values[key]=key_obj
    return values
            

def create_entity(entity_class, values):
    values = check_types(entity_class,values) #All we get from post are strings, so we need to cast/create as appropriate
    key = getKey(entity_class, values)
    entity = classModels[entity_class].get_by_id(key)
    if entity:
        entity.populate(**values)
        entity.put()
        return {'message':"Updated",'key':key}
    else:
        classModels[entity_class].get_or_insert(key,**values)
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
        tag = "<select name='" + prop['id'] + entity_class +"' data-dojo-type='dijit/form/Select'>"
        options = classModels[prop['type']._kind].query().fetch()
        for option in options:
            dicc = option.to_dict()
            option_value = str(getKey(prop['type']._kind, dicc))
            tag += "<option value='" + option_value + "'>" + option.rotulo + '</option>'
        tag += "</select>" 
    else:
        tag = '<input type="text" id="' + prop['id'] +  entity_class +'" name="'+ prop['id'] + entity_class 
        tag +='" required="' + prop['required'] 
        tag += '" data-dojo-type="' + prop['valid'] +'"/>'
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
            entity = classModels[entity_class].get_by_id(key)
            entity.key.delete()
        except Exception as ex:
            self.response.out.write(ex.message)
            return
        self.response.out.write("Se elimino exitosamente: " + entity_class + " " + key)        

class GetPrice(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        precioQuery = Precio.query(Precio.fruta == Fruta.get_by_id(values['fruta']).key,
                                   Precio.cliente == Client.get_by_id(values["client"]).key,
                                   Precio.porcion == Porcion.get_by_id(values["porcion"]).key)
        precio = ''
        try:
            precio = precioQuery.fetch()[0].precio
        except IndexError as e:
            self.response.out.write(e.message)
        self.response.out.write(precio)


class CrearFactura(webapp2.RequestHandler):
    def get(self):
        prop_client = Factura._properties['cliente']
        prop_fruta = Venta._properties['fruta']
        prop_porcion = Venta._properties['porcion']
        prop_cantidad = Venta._properties['cantidad']
        props = {'Client':{'ui': 'Cliente', 'id': 'client','required':'true','type':prop_client},
                 'Fruta':{'ui': 'Fruta', 'id': 'fruta','required':'true','type':prop_fruta},
                 'Porcion':{'ui': 'Porcion', 'id': 'porcion','required':'true','type':prop_porcion},
                 'Cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true', 'valid':'dijit/form/NumberTextBox','type':prop_cantidad}
                }
        template_values = {'props': props}
        template = JINJA_ENVIRONMENT.get_template('crearFactura.html')
        self.response.write(template.render(template_values))


class Test(webapp2.RequestHandler):
    def get(self):
        ventas = []
        for i in range(10):
            venta = Venta(fruta=Fruta.get_by_id('Mango').key,
                           porcion=Porcion.get_by_id('150g').key,
                           cantidad = i*5)
            ventas.append(venta)
        cliente = Client.get_by_id('HarrySAHarrySasson')
        factura = Factura(cliente = cliente.key, fecha = datetime.date.today(),ventas=ventas)
        factura.put()
        
        newFactura = Factura.query().fetch()[0]
         
        newFactura.key.delete()     
        
        template = JINJA_ENVIRONMENT.get_template('test.html')
        self.response.write(template.render())
    