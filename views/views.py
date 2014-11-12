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

#########################################
CLIENT_DATA = [
['RESTAURANTE EL ARABE','','CLL 69 A # 6-41','BOGOTA','2484899','900419473-5','0','ARABE'],
['JARDIN ABACO','','CLL 110 # 8-47','BOGOTA','6197512','830123705-3','0','ABACO'],
['AVESCO S.A.','MERCADO 93','CLL 93 A# 12-73','BOGOTA','2362500','860025461-0','30','AVESCO'],
['C&P CORREA','ZOE','CLL 108 # 8 A-22','BOGOTA','','9006800563-6','8','CYP'],
['CARMEL CLUB CAMPESTRE','','AUTO NORTE 153-81','BOGOTA','6497272 EXT. 123','','30','CARMEL'],
['CAROLINA ZULUAGA ','','','BOGOTA','','','0','PARTICULARES'],
['CASA FUEGO','','CLL 118 # 5-41','BOGOTA','6376954','','0','CASAFUEGO'],
['CHATOS','','AV CLL 82 # 9-11','BOGOTA','3220732','900016780-1','0','CHATOS'],
['CORPORACION CLUB EL NOGAL','','','BOGOTA','3267700 ext 3221','','30','NOGAL'],
['HARRYSA S.A.S','HARRY SASSON','CRA 9 #75-70','BOGOTA','3 45 03 04','830144557-1','30','HARRY'],
['HARRYSA S.A.S','HARRYS BAR','CLL 70 #5-57 - Zona G','BOGOTA','3 45 03 04','830144557-1','30','HARRY'],
['INVERSIONES GARDEL','EL DIA QUE ME QUIERAS','CLL 69 # 4-26','BOGOTA','5404585','900268742-2','30','GARDEL'],
['INVERSIIONES LEHAL S.A.','CLUB COLOMBIA','AV CL 82 # 9-11','BOGOTA','3220732','900016780-1','30','LEHAL'],
['JARDIN HANS ANDERSEN','','CRA 13 A # 127-10','BOGOTA','627 0928','8000628134-3','0','HANS'],
['JUAN EL PANADERO SAS','','CLL 81 # 7-93','BOGOTA','6748954','900450289-6','8','JUANELPANADERO'],
['JUAN SOTO','','','BOGOTA','','','0','PARTICULARES'],
['LEIDY MARTINEZ','','','BOGOTA','','','0','PARTICULARES'],
['LUIS CABALLERO','','CRA 28 A # 68-74','BOGOTA','','','0','PARTICULARES'],
['MARIA EZPERANZA BAZURTO ','','','','','','0','PARTICULARES'],
['AVESCO S.A.','MERCADO USAQUEN','CLL 93 A# 12-73','BOGOTA','2362500','860025461-0','30','AVESCO'],
['PAESA S.A  ','SALTO DEL ANGEL','Cra 13 # 93A - 45','BOGOTA','6545454','800241012-4','45','PAESA'],
['PAESA S.A  ','COTIDIANO ROSALES','CRA 5 #71 -45 - ROSALES','BOGOTA','6545454','800241012-4','45','PAESA'],
['PAESA S.A  ','COTIDIANO ANDINO','CC ANDINO LOCAL 402','BOGOTA','6545454','800241012-4','45','PAESA'],
['PAN TOLIMA','','CLL 57 # 16 A-27','BOGOTA','','','0','PANTOLIMA'],
['PATRICIA BERMUDEZ','','','BOGOTA','','','0','PARTICULARES'],
['POLKA DOT/NATALIA BOHORQUEZ','','CLL 86 A  # 13 A 23','BOGOTA','6165479','52718104-1','0','POLKA'],
['SARODY','','AV CL 82 # 9-11','BOGOTA','3220732','900016780-1','0','SARODY'],
['TREINTA Y DOS SEPTIMA SAS /CENTRICO','','CR 7 # 32-16 PISO 41','BOGOTA','3509100','900485850-1','0','CENTRICO']
]

PRODUCTO_DATA = ['ARAZA','CURUBA','DURAZNO','DURAZNO FRUTA','FEIJOA','FRESA','FRUTOS ROJOS','GUANABANA','GUANABANA FRUTA',
                 'GUAYABA','LULO','LULO TAJADO','MANGO','MANGO BICHE','MARACUYA','MARACUYA PEPA','MELON','MORA','NISPERO',
                 'PATILLA','PIÑA','SMOTHIE GMB','SMOTHIE LMF','TAMARINDO','TOMATE DE ARBOL','UCHUVA','UVA']



PORCION_DATA = [50, 70, 100, 110, 120, 125, 130, 140, 150, 160, 170, 180, 200, 700, 750, 1000]
#########################################


NUMERO_DE_FACTURA_INICIAL = 2775

classModels = {'Cliente':Cliente, 'Producto':Producto, 'Porcion':Porcion, 'Precio':Precio, 'GrupoDePrecios':GrupoDePrecios}
keyDefs = {'Cliente':['nombre','negocio'], 'Producto':['nombre'], 'Porcion':['valor','unidades'], 'GrupoDePrecios':['nombre'],'Precio':['producto','porcion','grupo']}
uiConfig = {'Cliente':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'negocio','ui':'Negocio', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'ciudad','ui':'Ciudad', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'direccion','ui':'Direccion', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'telefono','ui':'Telefono', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'nit','ui':'NIT', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                       {'id':'diasPago','ui':'Dias para pago', 'required':'true', 'valid':'dijit/form/NumberTextBox'},
                       {'id':'grupoDePrecios','ui':'Grupo de Precios', 'required':'true', 'valid':'dijit/form/ValidationTextBox'}
                       ],
            'Producto':[{'id':'nombre','ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox'}],
            'Porcion':[{'id':'valor','ui':'Porcion', 'required':'true', 'valid':'dijit/form/NumberTextBox'},
                       {'id':'unidades','ui':'Unidades', 'required':'true', 'valid':'dijit/form/ValidationTextBox'}],
            'GrupoDePrecios':[{'id':'nombre', 'ui':'Nombre', 'required':'true','valid':'dijit/form/ValidationTextBox'}],
            'Precio':[{'id':'producto','ui':'Producto'},
                      {'id':'porcion','ui':'Porcion'},
                      {'id':'grupo','ui':'Grupo de Precios'},
                      {'id':'precio','ui':'Precio','required':'true','valid':'dijit/form/NumberTextBox'}
                      ]
            }

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
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
            self.response.out.write(json.dumps(response))
        except Exception as ex:
            return self.response.out.write(ex.message)
        

def tagForField(entity_class, prop):
    tag = ''
    if type(prop['type']) == ndb.KeyProperty:
        tag = "<select name='" + prop['id'] + entity_class + "' id='" + prop['id'] + entity_class + "' data-dojo-type='dijit/form/Select'>"
        options = classModels[prop['type']._kind].query().fetch()
        for option in options:
            dicc = option.to_dict()
            option_value = getKey(prop['type']._kind, dicc)
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
        precioQuery = Precio.query(Precio.producto == Producto.get_by_id(values['producto']).key,
                                   Precio.grupo == Cliente.get_by_id(values["cliente"]).grupoDePrecios,
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
        prop_producto = Venta._properties['producto']
        prop_porcion = Venta._properties['porcion']
        prop_cantidad = Venta._properties['cantidad']
        props = {'Cliente':{'ui': 'Cliente', 'id': 'cliente','required':'true','type':prop_cliente},
                 'Producto':{'ui': 'Producto', 'id': 'producto','required':'true','type':prop_producto},
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
            ventas.append(Venta(producto=Producto.get_by_id(venta['producto']).key,
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
            ventas.append({'producto': unicode(venta.producto.id(),'utf-8'), 'porcion':venta.porcion.id(), 'cantidad':venta.cantidad, 
                           'precio': '{:,}'.format(venta.precio), 'valorTotal':'{:,}'.format(venta.venta)})
                
        template = JINJA_ENVIRONMENT.get_template('Factura.htm')
        self.response.write(template.render({'data':data, 'ventas':ventas}))
    
class ImportClientes(webapp2.RequestHandler):
    def get(self):
        message = ''
        for row in CLIENT_DATA:
            clientevals = {'nombre' : row[0], 'negocio':row[1], 'direccion': row[2],'ciudad':row[3],'telefono':row[4],
                           'nit':row[5], 'diasPago':int(row[6])}
            grupo = GrupoDePrecios.get_or_insert(row[7],nombre=row[7])
            clientevals['grupoDePrecios']=grupo.key
            key = getKey("Cliente", clientevals)
            cliente = Cliente.get_or_insert(key,**clientevals)
            cliente.put()
            message += "Registro importado: " + cliente.rotulo + "\n"
        self.response.out.write(message)
  
class ImportProductos(webapp2.RequestHandler):
    def get(self):
        message = ''
        for producto in PRODUCTO_DATA:
            key = getKey('Producto', {'nombre':producto})
            producto = Producto.get_or_insert(key,nombre=unicode(producto,'utf-8'))
            producto.put()
            message += "Registro importado: " + producto.rotulo + " --- "
        self.response.out.write(message)
  
class ImportPorciones(webapp2.RequestHandler):
    def get(self):
        message = ''
        for por in PORCION_DATA:
            key = getKey("Porcion", {'unidades':'g', 'valor':por})
            porcion = Porcion.get_or_insert(key,unidades='g', valor=por)
            porcion.put()
            message += "Registro importado: " + porcion.rotulo + " --- "
        self.response.out.write(message)

class Test(webapp2.RequestHandler):
    def get(self):        
        template = JINJA_ENVIRONMENT.get_template('test.html')
        self.response.write(template.render())
    
