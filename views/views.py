# -*- coding: utf-8 -*-
from datetime import datetime, date, time
import json
import webapp2
import jinja2
from google.appengine.api import users
from models.models import *
from google.appengine.ext.ndb.model import IntegerProperty, KeyProperty, ComputedProperty, FloatProperty
from jinja2._markupsafe import Markup
from config import *


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def isAdminUser():
    user = users.get_current_user()
    if user:
        if 'salud-able.com' in user.email():
            return True
        else:
            return False 
    else:
        return False

class LogIn(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url('/home'))

class LogOut(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/home'))

class GetWidget(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        temp_name = self.request.get('template')
        template_values = {'entity_class': entityClass}
        template_name = ''
        if temp_name in templateNames:
            template_name = templateNames[temp_name]
        else:
            template_name = 'widget.html'
        template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.write(template.render(template_values))

class ShowEntities(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        template_values = {'entity_class': entity_class}
        template = JINJA_ENVIRONMENT.get_template('showEntities.html')
        self.response.write(template.render(template_values))


def getColumns(entity_class):
    columns=[]
    props = classModels[entity_class]._properties
    for column in uiConfig[entity_class]:
        colProps = { 'field' : column['id'], 'name' : column['ui'], 'style': "text-align: center", 'width':column['width']}
        if column['id'] in props and type(props[column['id']]) == ndb.IntegerProperty:
            colProps['type']='Integer'
        columns.append(colProps);
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
                if type(prop_value) == list:
                    value = ''
                    for item in prop_value:
                        value += item.get().to_dict()['rotulo'] + ';'
                    dicc[prop_key] = value
            dicc['id'] = entity.key.id()
            records.append(dicc)
        response = {'columns':getColumns(entity_class), 'records':records}
        self.response.write(json.dumps(response))        

class Home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {'user': user}
        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.write(template.render(template_values))

def getKey(entity_class,dicc):
    key = u''
    for keypart in keyDefs[entity_class]:
        if type(dicc[keypart]) == ndb.Key:
            entity = dicc[keypart].get()
            if entity:
                key += ' ' + entity.to_dict()['rotulo']
            else:
                print "Entity not found by key:" + keypart 
        else:
            key += ' ' + unicode(dicc[keypart])
    return '.'.join(key.split())
        
def check_types(entity_class, values):
    props = classModels[entity_class]._properties
    for key, value in props.iteritems():
        if type(value) is ComputedProperty:
            values.pop(key, None)
        if type(value) is IntegerProperty:
            values[key] = int(values[key])
        if type(value) is FloatProperty:
            values[key] = float(values[key])
        if type(value) is KeyProperty:
            if value._repeated == True:
                items = []
                if 'proplistdata' in values:
                    proplistdata = json.loads(values['proplistdata'])
                    parts =  proplistdata[key].strip().strip(';').split(';')
                    for item in parts:
                        key_obj = ndb.Key(value._kind,item.strip().replace(' ','.'))
                        items.append(key_obj)
                    values[key]= items
                else:
                    for item in values[key]:
                        key_obj = ndb.Key(value._kind,item.strip().replace(' ','.'))
                        items.append(key_obj)
                    values[key] = items
            else:   
                key_obj = ndb.Key(value._kind,values[key].strip().replace(' ','.'))
                values[key]=key_obj
        if type(value) == ndb.DateProperty:
            values[key] = datetime.strptime(values[key], '%Y-%m-%d').date()
        if type(value) == ndb.StructuredProperty:
            values[key]=[]
    if 'proplistdata' in values:
        values.pop("proplistdata")
    keys = values.keys()
    for item in keys:
        if item not in props:
            values.pop(item)
    return values
            
def create_entity(entity_class, values):
    values = check_types(entity_class,values) #All we get from post are strings, so we need to cast/create as appropriate
    key = getKey(entity_class, values)
    entity = classModels[entity_class].get_by_id(key)
    if entity:
        entity.populate(**values)
        entity.put()
        return {'message':"Updated",'key':key, 'entity':entity}
    else:
        values['id']=key
        entity = classModels[entity_class](**values)
        entity.put()
        return {'message':"Created",'key':key, 'entity':entity}

class SaveEntity(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        entity_class = values.pop("entity_class")
        for key,value in values.iteritems():
            values[key.replace(entity_class,'')] = values.pop(key)
        response = {};
        response = create_entity(entity_class,values)
        self.response.out.write(JSONEncoder().encode(response))

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
        if prop['type']._repeated == True:
            tag += '<button class = "listprop" id="listpropBtnAgregar' + entity_class + '_' + prop['id'] + '" data-dojo-type="dijit/form/Button">Agregar</button>'
            tag += '<button class = "listprop" id="listpropBtnQuitar' + entity_class + '_' + prop['id'] + '" data-dojo-type="dijit/form/Button">Quitar</button>'
            tag += '<br/><textarea readOnly="True" class = "listpropTextarea" id="text' + prop['id'] + entity_class + '" data-dojo-type="dijit/form/SimpleTextarea" rows="3" cols="30" style="width:auto;"></textarea>'
    else:
        tag = '<input type="text" id="' + prop['id'] +  entity_class +'" name="'+ prop['id'] + entity_class 
        tag +='" required="' + prop['required'] 
        tag += '" data-dojo-type="' + prop['valid'] +'" style="width: ' + prop['width'] + ';"/>'
    return Markup(tag)

def adjustText(text):
    html=''
    if len(text)>24:
        pieces = text.split()
        while len(html) + len(pieces[0]) < 24:
            html += ' ' + pieces.pop(0)
        html = html.strip()
        html += '<br>' + " ".join(pieces)
        return Markup(html)
    else:
        return text

def createTemplateString(entity):
    if entity in createTemplateStings:
        return createTemplateStings[entity]
    else:
        return '/addEntity?entityClass=' + entity        

JINJA_ENVIRONMENT.globals['tagForField']=tagForField
JINJA_ENVIRONMENT.globals['adjustText']=adjustText
JINJA_ENVIRONMENT.globals['isAdminUser']=isAdminUser
JINJA_ENVIRONMENT.globals['createTemplateString']=createTemplateString

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
        clientes = [{'value':cliente.key.id(), 'name': cliente.rotulo } for cliente in clientes]
        self.response.out.write(json.dumps(clientes))
        
class GetEmpleados(webapp2.RequestHandler):
    def post(self):
        empleados = Empleado.query().fetch()
        empleados = [{'value':empleado.key.id(), 'name': empleado.rotulo } for empleado in empleados]
        self.response.out.write(json.dumps(empleados))

class GetProducto(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.POST.mixed()
        cliente = Cliente.get_by_id(post_data['cliente'])
        grupo = cliente.grupoDePrecios
        precios = Precio.query(Precio.grupo == grupo,  projection = [Precio.producto], distinct=True).fetch()
        productos = [precio.producto.id() for precio in precios]
        if not productos:
            productos.append('No hay precios definidos')
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
        tipo = self.request.get('tipo')
        if tipo == 'Factura':
            query = Factura.query(Factura.numero == int(facturaKey))
            entity = query.fetch()[0]
        else:
            query = Remision.query(Remision.numero == int(facturaKey))
            entity = query.fetch()[0]
        records=[]
        for venta in entity.ventas:
            dicc = venta.to_dict()
            for prop_key, prop_value in dicc.iteritems():
                if type(prop_value) == ndb.Key:
                    try:
                        dicc[prop_key] = dicc[prop_key].id()#dicc[prop_key].get().to_dict()['rotulo']
                    except Exception as e:
                        dicc[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
                if type(prop_value) == date:
                    dicc[prop_key] = prop_value.strftime('%Y-%m-%d')
            dicc['id'] = dicc['producto'] + dicc['porcion'];
            records.append(dicc)
        self.response.out.write(json.dumps(records))
        
class GetProductSales(webapp2.RequestHandler):
    def get(self):
        records = []
        facturas = Factura.query().fetch()
        for factura in facturas:
            if factura.anulada: continue
            for venta in factura.ventas:
                venta = venta.to_dict()
                if venta['porcion'].get():
                    venta['peso']=venta['porcion'].get().valor * venta['cantidad']
                else: 
                    print venta
                    continue
                venta['factura']=factura.numero
                venta['cliente']=factura.cliente.id()
                venta['fecha']=factura.fecha
                records.append(venta)
        response = {'records':records}
        self.response.out.write(JSONEncoder().encode(response))

class GetCompras(webapp2.RequestHandler):
    def get(self):
        egresoKey = self.request.get('egresoKey')
        query = Egreso.query(Egreso.numero == int(egresoKey))
        egreso = query.fetch()[0]
        records = []
        for compra in egreso.compras:
            compra = compra.to_dict()
            records.append(compra)
        self.response.out.write(JSONEncoder().encode(records))
           

class CrearEgreso(webapp2.RequestHandler):
    def get(self):
        prop_tipo = Egreso._properties['tipo']
        prop_proveedor = Egreso._properties['proveedor']
        prop_empleado = Egreso._properties['empleado']
        prop_bienoservicio = Compra._properties['bienoservicio']
        prop_detalle = Compra._properties['detalle']
        prop_comentario = Egreso._properties['comentario']
        prop_cantidad = Compra._properties['cantidad']
        prop_precio = Compra._properties['precio']
        prop_sucursal = Egreso._properties['sucursal']
        props = {'proveedor':{'ui': 'Proveedor', 'id': 'proveedor','required':'true','type':prop_proveedor},
                 'empleado':{'ui': 'Empleado', 'id': 'empleado','required':'true','type':prop_empleado},
                 'bienoservicio':{'ui': 'Bien o Servicio', 'id': 'bienoservicio','required':'true','type':prop_bienoservicio},
                 'detalle':{'ui': 'Detalle', 'id': 'detalle','required':'true', 'valid':'dijit/form/ValidationTextBox',
                            'width':'10em','type':prop_detalle},
                 'comentario':{'ui': 'Comentario', 'id': 'comentario','required':'false', 'valid':'dijit/form/ValidationTextBox',
                            'width':'50em','type':prop_comentario},
                 'cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true', 'valid':'dijit/form/NumberTextBox',
                             'width':'5em', 'type':prop_cantidad},
                 'precio':{'ui':'Precio Unitario','id':'precio','required':'true', 'valid':'dijit/form/NumberTextBox',
                           'width':'5em', 'type':prop_precio},
                 'tipo':{'ui':'Tipo', 'id':'tipo','required':'true','type':prop_tipo},
                 'sucursal':{'ui':'Ciudad', 'id':'sucursal','required':'true','type':prop_sucursal}
                }
        template_values = {'props': props}
        template = JINJA_ENVIRONMENT.get_template('crearEgreso.html')
        self.response.write(template.render(template_values))

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
                 'Cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true', 'valid':'dijit/form/NumberTextBox',
                             'width':'5em', 'type':prop_cantidad}
                }
        template_values = {'props': props}
        template = JINJA_ENVIRONMENT.get_template('crearFactura.html')
        self.response.write(template.render(template_values))

class SetNumber(webapp2.RequestHandler):
    def get(self):
        tipo = self.request.get('tipo')
        newNumero = self.request.get('numero')
        msg ='Se definio el numero de ' + tipo +' actual como: ' + newNumero
        if tipo =='Factura':
            numero = NumeroFactura.query().get()
            if numero:
                numero.consecutivo = int(newNumero)
                numero.put()
            else:
                NumeroFactura(consecutivo=int(newNumero)).put()
        elif tipo == 'Remision':
            numero = NumeroRemision.query().get()
            if numero:
                numero.consecutivo = int(newNumero)
                numero.put()
            else:
                NumeroRemision(consecutivo=int(newNumero)).put()
        else:
            msg = 'Parametro "tipo" debe ser "Factura" o "Remision"'
        self.response.write(msg)

def getConsecutivo(esRemision):
    if esRemision:
        numero = NumeroRemision.query().fetch()
    else:
        numero = NumeroFactura.query().fetch()
    if numero:
        numero[0].consecutivo = numero[0].consecutivo + 1
        numero[0].put()
        return numero[0].consecutivo
         
class GuardarFactura(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.body
        values = json.loads(post_data)
        ventas =[]
        for venta in values['ventas']:
            producto = venta['producto'].replace(' ','.')
            ventas.append(Venta(producto=Producto.get_by_id(producto).key,
                           porcion=Porcion.get_by_id(venta['porcion']).key,
                           cantidad = venta['cantidad'],
                           precio = venta['precio'],
                           venta = venta['venta']))
        cliente = Cliente.get_by_id(values['cliente'])
        empleado = Empleado.get_by_id(values['empleado'])
        fecha = datetime.strptime(values['fecha'], '%Y-%m-%d')
        numero = ''
        if values['numero']:
            numero = values['numero']
        else:
            numero = getConsecutivo(values['remision'])
        
        if values['remision']:
            remision = Remision(id=str(numero), numero=int(numero), cliente = cliente.key, empleado = empleado.key, fecha = fecha, ventas=ventas, total=values['total'])
            remision.put()
            entity = remision
        else:
            factura = Factura(id=str(numero), numero=int(numero), cliente = cliente.key, empleado = empleado.key, fecha = fecha, ventas=ventas, total=values['total'])
            factura.put()
            entity = factura
        self.response.out.write(json.dumps({'result':'Success','facturaId': entity.key.id()}))     
        

        
class MostrarFactura(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('facturaId')
        tipo = self.request.get('tipo')
        facturaPorPagina = self.request.get('pagina')
        if tipo == 'Factura':
            entity = Factura.get_by_id(key)
        else:
            entity = Remision.get_by_id(key)
        
        cliente = entity.cliente.get()
        empleado = entity.empleado.get()
        data = {'numero' : entity.numero,
                'cliente': unicode(cliente.rotulo),
                'direccion': unicode(cliente.direccion),
                'ciudad': unicode(cliente.ciudad),
                'nit':cliente.nit, 
                'fecha': entity.fecha.strftime('%Y-%m-%d'),
                'telefono':cliente.telefono,
                'empleado': empleado.rotulo,
                'numVentas':len(entity.ventas),
                'total': '{:,}'.format(entity.total),
                'remision': True if tipo == 'Remision' else False
                }
        ventas = []
        for venta in entity.ventas:
            ventas.append({'producto': venta.producto.get().rotulo, 'porcion':venta.porcion.id(), 'cantidad':venta.cantidad, 
                           'precio': '{:,}'.format(venta.precio), 'valorTotal':'{:,}'.format(venta.venta)})
                
        if facturaPorPagina == 'true':
            template = JINJA_ENVIRONMENT.get_template('Factura1p.htm')
        else:
            template = JINJA_ENVIRONMENT.get_template('Factura.htm')
        self.response.write(template.render({'data':data, 'ventas':ventas}))

class AnularFactura(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('id')
        tipo = self.request.get('tipo')
        if tipo == 'Factura':
            entity = Factura.get_by_id(key)
        else:
            entity = Remision.get_by_id(key)
        entity.anulada = True
        entity.put()
        self.response.write('Se anulo ' + tipo + ' :' + key)

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
            print record
            create_entity(entity_class, record)
        self.response.write('Registros Importados!')


class ExportScript(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        data = classModels[entity_class].query().fetch()
        self.response.write(JSONEncoder().encode(data))
        
def createVenta(row):
    values = {'producto':row[1], 'porcion':row[2], 'cantidad':row[3], 'precio':row[4], 'venta':row[5]}
    values = check_types('Venta', values)
    venta = Venta(producto = values['producto'],
                  porcion = values['porcion'],
                  cantidad = values['cantidad'],
                  precio = values['precio'],
                  venta = values['venta']
                  )
    return venta

class ImportFacturas(webapp2.RequestHandler):
    def get(self):
        tipo = self.request.get('tipo')
        if tipo == 'Factura':
            json_data=open('data/Factura.json')
        else:
            json_data=open('data/Remision.json')
        data = json.load(json_data)
        json_data.close()
            
        for record in data:
            entity = classModels[tipo].get_by_id(unicode(record['numero']))
            if not entity:
                entity = create_entity(tipo, record)['entity']
            ventas=[]
            ventasObj = record['ventas']
            for venta in ventasObj:
                venta = check_types('Venta',venta)             
                ventas.append(Venta(**venta))
            entity.ventas = ventas
            entity.put()
            print record['numero']
        self.response.write('Ventas importadas con exito!')

class ImportVentasCSV(webapp2.RequestHandler):
    def get(self):
        import unicodecsv as csv
        with open('data/Ventas.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            facturaId = ''
            ventas = []
            for row in reader:
                if facturaId and facturaId != row[0]:
                    factura = Factura.get_by_id(facturaId)
                    if factura:
                        factura.ventas = ventas
                        factura.put()
                    else:
                        print 'No existe factura ' + facturaId
                    ventas = []
                facturaId = row[0]
                
                ventas.append(createVenta(row))
        self.response.write('Ventas importadas con exito!')


class ImportCSV(webapp2.RequestHandler):
    def get(self):
        import csv
        entity_class = self.request.get('entityClass')
        with open('data/' + entity_class + '.csv', 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            props = [prop['id'] for prop in uiConfig[entity_class]]
            for row in reader:
                values = {props[i] : row[i] for i in range(len(props))}
                create_entity(entity_class,values)
        self.response.write('CSV importada con exito!')
        
class Pivot(webapp2.RequestHandler):
    def get(self): 
        template_values = {'entity_class': self.request.get('entityClass')}
        template = JINJA_ENVIRONMENT.get_template('pivot.html')
        self.response.write(template.render(template_values))
        
class TablaDinamica(webapp2.RequestHandler):
    def get(self): 
        template_values = {'entity_class': self.request.get('entityClass')}
        template = JINJA_ENVIRONMENT.get_template('tablaDinamica.html')
        self.response.write(template.render(template_values))
        
class GetBienesoServicios(webapp2.RequestHandler):
    def get(self):
        tipo = TipoEgreso.get_by_id(self.request.get('tipo'))
        bienesoservicios = Bienoservicio.query(Bienoservicio.tipo == tipo.key).fetch()
        response = [{'value':bienoservicio.key.id(), 'name': bienoservicio.rotulo } for bienoservicio in bienesoservicios]
        self.response.out.write(json.dumps(response))

        
class GetProveedores(webapp2.RequestHandler):
    def get(self):
        bienoservicio = Bienoservicio.get_by_id(self.request.get('bienoservicio'))
        todos = Proveedor.query()
        proveedores = todos.filter(Proveedor.bienesoservicios.IN([bienoservicio.key])).fetch()
        response = [{'value':proveedor.key.id(), 'name': proveedor.rotulo } for proveedor in proveedores]
        self.response.out.write(json.dumps(response))

class Addbienoservicio(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        property = self.request.get('property')
        id= self.request.get('id')
        classModels[entity_class]


def getConsecutivoEgreso():
    numero = NumeroEgreso.query().fetch()
    if numero:
        numero[0].consecutivo = numero[0].consecutivo + 1
        numero[0].put()
        return numero[0].consecutivo
    else:
        NumeroEgreso(consecutivo=1).put()
        return 1
        
        
class GuardarEgreso(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.body
        values = json.loads(post_data)
        compras =[]
        for compra in values['compras']:
            bienoservicio = compra['bienoservicio'].replace(' ','.')
            compras.append(Compra(bienoservicio=Bienoservicio.get_by_id(bienoservicio).key,
                           detalle = compra['detalle'],
                           cantidad = compra['cantidad'],
                           precio = compra['precio'],
                           compra = compra['compra']))
        proveedor = Proveedor.get_by_id(values['proveedor'])
        empleado = Empleado.get_by_id(values['empleado'])
        fecha = datetime.strptime(values['fecha'], '%Y-%m-%d')
        tipo = TipoEgreso.get_by_id(values['tipo'])
        sucursal = Sucursal.get_by_id(values['sucursal'])
        numero = ''
        if values['numero']:
            numero = values['numero']
        else:
            numero = getConsecutivoEgreso()

        resumen = compras[0].bienoservicio.id() if len(compras)==1 else compras[0].bienoservicio.id() + ', etc.' 
        egreso = Egreso(id=str(numero), numero=int(numero), resumen = resumen, tipo = tipo.key, proveedor = proveedor.key, 
                        empleado = empleado.key, fecha = fecha, compras=compras, total=values['total'], sucursal = sucursal.key,
                        comentario = values['comentario'])
        egreso.put()
        entity = egreso
        self.response.out.write(json.dumps({'result':'Success','egresoId': entity.key.id()}))     
        