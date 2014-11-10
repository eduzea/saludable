# -*- coding: utf-8 -*-
from datetime import datetime
import json
import cgi
import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext.ndb import metadata

from models.models import * 
from google.appengine.ext.ndb.model import IntegerProperty, KeyProperty
from jinja2._markupsafe import Markup

NUMERO_DE_FACTURA_INICIAL = 2775

classModels = {'Cliente':Cliente, 'Fruta':Fruta, 'Porcion':Porcion, 'Precio':Precio}
keyDefs = {'Cliente':['nombre','negocio'], 'Fruta':['nombre'], 'Porcion':['valor','unidades'], 'Precio':['fruta','porcion','cliente']}
uiConfig = {'Cliente':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
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
                        dicc[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
            dicc['id'] = entity.key.id()
            records.append(dicc)
        response = {'columns':getColumns(entity_class), 'records':records}
        self.response.write(json.dumps(response))        

class Home(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render())

def getKey(entity_class,dicc):
    key = u''
    for keypart in keyDefs[entity_class]:
        if type(dicc[keypart]) == ndb.Key:
            key += dicc[keypart].get().to_dict()['rotulo']
        else:
            key += unicode(dicc[keypart])
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
            return self.response.out.write(ex.message)
        self.response.out.write(json.dumps(response))

def tagForField(entity_class, prop):
    tag = ''
    if type(prop['type']) == ndb.KeyProperty:
        tag = "<select name='" + prop['id'] + entity_class + "' id='" + prop['id'] + entity_class + "' data-dojo-type='dijit/form/Select'>"
        options = classModels[prop['type']._kind].query().fetch()
        for option in options:
            dicc = option.to_dict()
            option_value = unicode(getKey(prop['type']._kind, dicc))
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
                                   Precio.cliente == Cliente.get_by_id(values["cliente"]).key,
                                   Precio.porcion == Porcion.get_by_id(values["porcion"]).key)
        precio = ''
        try:
            precio = precioQuery.fetch()[0].precio
        except IndexError as e:
            self.response.out.write(e.message)
        self.response.out.write(precio)

class CrearFactura(webapp2.RequestHandler):
    def get(self):
        prop_cliente = Factura._properties['cliente']
        prop_fruta = Venta._properties['fruta']
        prop_porcion = Venta._properties['porcion']
        prop_cantidad = Venta._properties['cantidad']
        props = {'Cliente':{'ui': 'Cliente', 'id': 'cliente','required':'true','type':prop_cliente},
                 'Fruta':{'ui': 'Fruta', 'id': 'fruta','required':'true','type':prop_fruta},
                 'Porcion':{'ui': 'Porcion', 'id': 'porcion','required':'true','type':prop_porcion},
                 'Cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true', 'valid':'dijit/form/NumberTextBox','type':prop_cantidad}
                }
        template_values = {'props': props}
        template = JINJA_ENVIRONMENT.get_template('crearFactura.html')
        self.response.write(template.render(template_values))

def getConsecutivo():
    numero = NumeroFactura.query().fetch()
    if numero:
        numero[0].consecutivo = numero[0].consecutivo + 1
        numero[0].put()
        return numero[0].consecutivo
    else:
        first = NumeroFactura(consecutivo=NUMERO_DE_FACTURA_INICIAL)
        first.put()
        return NUMERO_DE_FACTURA_INICIAL
         


class GuardarFactura(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.body
        values = json.loads(post_data)
        ventas =[]
        for venta in values['ventas']:
            ventas.append(Venta(fruta=Fruta.get_by_id(venta['fruta']).key,
                           porcion=Porcion.get_by_id(venta['porcion']).key,
                           cantidad = venta['cantidad'],
                           precio = venta['precio'],
                           venta = venta['valorTotal']))
        cliente = Cliente.get_by_id(values['cliente'])
        fecha = datetime.strptime(values['fecha'], '%Y-%m-%d')
        numero = getConsecutivo()
        try:
            factura = Factura(numero=numero, cliente = cliente.key, fecha = fecha, ventas=ventas, total=values['total'])
            factura.put()
            self.response.out.write("Success:" + unicode(factura.key.id()))     
        except Exception as e:
            self.response.out.write(e.message)

        
class MostrarFactura(webapp2.RequestHandler):
    def get(self):
        facturaKey = self.request.get('facturaId')
        factura = Factura.get_by_id(long(facturaKey))
        cliente = factura.cliente.get()
        data = {'numero' : factura.numero,
                'cliente': unicode(cliente.rotulo),
                'direccion': unicode(cliente.direccion),
                'ciudad': unicode(cliente.ciudad),
                'nit':cliente.nit, 
                'noFactura':1456,
                'fecha': factura.fecha.strftime('%Y-%m-%d'),
                'telefono':cliente.telefono,
                'empleado': 'Ofelia',
                'numVentas':len(factura.ventas),
                'total': '{:,}'.format(factura.total)
                }
        ventas = []
        for venta in factura.ventas:
            ventas.append({'fruta': unicode(venta.fruta.id(),'utf-8'), 'porcion':venta.porcion.id(), 'cantidad':venta.cantidad, 
                           'precio': '{:,}'.format(venta.precio), 'valorTotal':'{:,}'.format(venta.venta)})
                
        template = JINJA_ENVIRONMENT.get_template('Factura.htm')
        self.response.write(template.render({'data':data, 'ventas':ventas}))
    
# class ImportClientes(webapp2.RequestHandler):
#     def get(self):
#         message = ''
#         for row in CLIENT_DATA:
#             clientevals = {'nombre' : row[0], 'negocio':row[1], 'direccion': row[2],'ciudad':row[3],'telefono':row[4],
#                            'nit':row[5], 'diasPago':int(row[6])}
#             key = getKey("Cliente", clientevals)
#             cliente = Cliente.get_or_insert(key,**clientevals)
#             cliente.put()
#             message += "Registro importado: " + cliente.rotulo + "\n"
#         self.response.out.write(message)
# 
# class ImportFrutas(webapp2.RequestHandler):
#     def get(self):
#         message = ''
#         for fruit in FRUTA_DATA:
#             key = getKey('Fruta', {'nombre':fruit})
#             fruta = Fruta.get_or_insert(key,nombre=unicode(fruit,'utf-8'))
#             fruta.put()
#             message += "Registro importado: " + fruta.rotulo + " --- "
#         self.response.out.write(message)
# 
# class ImportPorciones(webapp2.RequestHandler):
#     def get(self):
#         message = ''
#         for por in PORCION_DATA:
#             key = getKey("Porcion", {'unidades':'g', 'valor':por})
#             porcion = Porcion.get_or_insert(key,unidades='g', valor=por)
#             porcion.put()
#             message += "Registro importado: " + porcion.rotulo + " --- "
#         self.response.out.write(message)

class Test(webapp2.RequestHandler):
    def get(self):        
        template = JINJA_ENVIRONMENT.get_template('test.html')
        self.response.write(template.render())
    
