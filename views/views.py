# -*- coding: utf-8 -*-
from datetime import datetime, date, time
import json
import webapp2
import jinja2

from models.models import * 
from google.appengine.ext.ndb.model import IntegerProperty, KeyProperty, ComputedProperty
from jinja2._markupsafe import Markup

NUMERO_DE_FACTURA_INICIAL = 2775

classModels = {'Cliente':Cliente, 'Producto':Producto, 'Porcion':Porcion, 'Precio':Precio, 'GrupoDePrecios':GrupoDePrecios, 
               'Factura':Factura, 'Empleado':Empleado}
keyDefs = {'Cliente':['nombre','negocio'], 'Producto':['nombre'], 'Porcion':['valor','unidades'], 'GrupoDePrecios':['nombre'],
           'Precio':['producto','porcion','grupo'], 'Empleado':['nombre','apellido']}
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
                      ],
            'Empleado':[{'id':'nombre', 'ui':'Nombre', 'required':'true', 'valid':'dijit/form/ValidationTextBox'},
                        {'id':'apellido', 'ui':'Apellido', 'required':'true', 'valid':'dijit/form/ValidationTextBox'}],
            'Factura':[{'id':'id', 'ui':'Numero'},
                       {'id':'cliente', 'ui':'Cliente'},
                       {'id':'empleado', 'ui':'Empleado'},
                       {'id':'fecha', 'ui':'Fecha'},
                       {'id':'total', 'ui':'Valor'}
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
        props = classModels[entity_class]._properties
        for entity in entities:
            dicc = entity.to_dict()
            dicc = {key: dicc[key] for key in dicc if type(props[key]) != ndb.StructuredProperty }
            for prop_key, prop_value in dicc.iteritems():
                if type(prop_value) == ndb.Key:
                    try:
                        dicc[prop_key]= dicc[prop_key].get().to_dict()['rotulo']
                    except Exception as e:
                        dicc[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
                if type(prop_value) == date:
                    dicc[prop_key] = prop_value.strftime('%Y-%m-%d')
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
            entity = dicc[keypart].get() 
            key += entity.to_dict()['rotulo']
        else:
            key += unicode(dicc[keypart])
    return ''.join(key.split())
        
def check_types(entity_class, values):
    props = classModels[entity_class]._properties
    for key, value in props.iteritems():
        if type(value) is ComputedProperty:
            values.pop(key, None)
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

class GetClientes(webapp2.RequestHandler):
    def post(self):
        clientes = Cliente.query().fetch()
        clientes = [cliente.key.id() for cliente in clientes]
        self.response.out.write(json.dumps(clientes))


class GetProducto(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.POST.mixed()
        if post_data:
            cliente = Cliente.get_by_id(post_data['cliente'])
        else:
            cliente = Cliente.query().get(); 
        grupo = cliente.grupoDePrecios
        precios = Precio.query(Precio.grupo == grupo,  projection = [Precio.producto], distinct=True).fetch()
        productos = [precio.producto.id() for precio in precios]
        self.response.out.write(json.dumps(productos))
        
class GetPorcion(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.POST.mixed()
        cliente = Cliente.get_by_id(post_data['cliente'])
        producto= Producto.get_by_id(post_data['producto']) 
        grupo = cliente.grupoDePrecios
        precios = Precio.query(Precio.grupo == grupo,
                               Precio.producto == producto.key,
                               projection = [Precio.porcion], distinct=True).fetch()
        porciones = [precio.porcion.id() for precio in precios]
        self.response.out.write(json.dumps(porciones))        


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
        
class GetVentas(webapp2.RequestHandler):
    def get(self):
        facturaKey = self.request.get('facturaKey')
        facturaQuery = Factura.query(Factura.numero == int(facturaKey))
        factura = facturaQuery.fetch()[0]
        records=[]
        for venta in factura.ventas:
            dicc = venta.to_dict()
            for prop_key, prop_value in dicc.iteritems():
                if type(prop_value) == ndb.Key:
                    try:
                        dicc[prop_key] = dicc[prop_key].get().to_dict()['rotulo']
                    except Exception as e:
                        dicc[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
                if type(prop_value) == date:
                    dicc[prop_key] = prop_value.strftime('%Y-%m-%d')
            dicc['id'] = dicc['producto'] + dicc['porcion'];
            records.append(dicc)
        self.response.out.write(json.dumps(records))

class CrearFactura(webapp2.RequestHandler):
    def get(self):
        prop_cliente = Factura._properties['cliente']
        prop_empleado = Factura._properties['empleado']
        prop_producto = Venta._properties['producto']
        prop_porcion = Venta._properties['porcion']
        prop_cantidad = Venta._properties['cantidad']
        props = {'Cliente':{'ui': 'Cliente', 'id': 'cliente','required':'true','type':prop_cliente},
                 'Empleado':{'ui': 'Empleado', 'id': 'empleado','required':'true','type':prop_empleado},
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
                           venta = venta['venta']))
        cliente = Cliente.get_by_id(values['cliente'])
        empleado = Empleado.get_by_id(values['empleado'])
        fecha = datetime.strptime(values['fecha'], '%Y-%m-%d')
        numero = getConsecutivo()
        try:
            factura = Factura(id=str(numero), numero=numero, cliente = cliente.key, empleado = empleado.key, fecha = fecha, ventas=ventas, total=values['total'])
            factura.put()
            self.response.out.write(json.dumps({'action':'Created','facturaId': factura.key.id()}))     
        except Exception as e:
            self.response.out.write(e.message)

        
class MostrarFactura(webapp2.RequestHandler):
    def get(self):
        facturaKey = self.request.get('facturaId')
        factura = Factura.get_by_id(facturaKey)
        cliente = factura.cliente.get()
        empleado = factura.empleado.get()
        data = {'numero' : factura.numero,
                'cliente': unicode(cliente.rotulo),
                'direccion': unicode(cliente.direccion),
                'ciudad': unicode(cliente.ciudad),
                'nit':cliente.nit, 
                'noFactura':1456,
                'fecha': factura.fecha.strftime('%Y-%m-%d'),
                'telefono':cliente.telefono,
                'empleado': empleado.rotulo,
                'numVentas':len(factura.ventas),
                'total': '{:,}'.format(factura.total)
                }
        ventas = []
        for venta in factura.ventas:
            ventas.append({'producto': unicode(venta.producto.id(),'utf-8'), 'porcion':venta.porcion.id(), 'cantidad':venta.cantidad, 
                           'precio': '{:,}'.format(venta.precio), 'valorTotal':'{:,}'.format(venta.venta)})
                
        template = JINJA_ENVIRONMENT.get_template('Factura.htm')
        self.response.write(template.render({'data':data, 'ventas':ventas}))
    
# class ImportClientes(webapp2.RequestHandler):
#     def get(self):
#         message = ''
#         for row in CLIENT_DATA:
#             clientevals = {'nombre' : row[0], 'negocio':row[1], 'direccion': row[2],'ciudad':row[3],'telefono':row[4],
#                            'nit':row[5], 'diasPago':int(row[6])}
#             grupo = GrupoDePrecios.get_or_insert(row[7],nombre=row[7])
#             clientevals['grupoDePrecios']=grupo.key
#             key = getKey("Cliente", clientevals)
#             cliente = Cliente.get_or_insert(key,**clientevals)
#             cliente.put()
#             message += "Registro importado: " + cliente.rotulo + "\n"
#         self.response.out.write(message)
#   
# class ImportProductos(webapp2.RequestHandler):
#     def get(self):
#         message = ''
#         for producto in PRODUCTO_DATA:
#             key = getKey('Producto', {'nombre':producto})
#             producto = Producto.get_or_insert(key,nombre=unicode(producto,'utf-8'))
#             producto.put()
#             message += "Registro importado: " + producto.rotulo + " --- "
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

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ndb.key.Key):
            return o.id()
        if isinstance(o, ndb.Model):
            return o.to_dict()
        elif isinstance(o, (datetime, date, time)):
            return str(o)  # Or whatever other date format you're OK with...
        else:
            print "Hold on!"

class ImportScript(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        json_data=open('data/' + entity_class +'.json')
        data = json.load(json_data)
#         data = json.loads(data)
        json_data.close()
        for record in data:
            create_entity(entity_class, record)
        self.response.write('Registros Importados!')


class ExportScript(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        data = classModels[entity_class].query().fetch()
        self.response.write(JSONEncoder().encode(data))
        
        
        
