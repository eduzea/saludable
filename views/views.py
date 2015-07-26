# -*- coding: utf-8 -*-
from __future__ import division
import sys
import random
from _struct import Struct
sys.path.insert(0, 'libs/python-dateutil-1.5')
sys.path.insert(0, 'libs/easydict-1.6')
from datetime import datetime, date, time
from easydict import EasyDict as edict
import json
import webapp2
import jinja2
from dateutil import parser
from google.appengine.api import users
from google.appengine.datastore.datastore_query import Cursor
from models.models import *
from followup import *
from google.appengine.ext.ndb.model import IntegerProperty, KeyProperty, ComputedProperty, FloatProperty
from jinja2._markupsafe import Markup
from config import *


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

#String replace from the right, specifying # of replacements to make.
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


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
        self.redirect(users.create_login_url('/validateUser'))

class ValidateUser(webapp2.RequestHandler):
    def get(self):
        empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
        if empleado:
            self.redirect(users.create_login_url('/home'))
        else:
            tag = '<h1>No hay un usuario registrado con ese login en Salud-Able!</h1><br>'
            tag += '<h2>Pide al administrador eduzea@gmail.com que cree tu usuario.</h2><br>'
            tag += '<a href="/logout">Log out</a>'
            self.response.write(tag)
            


class LogOut(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_logout_url('/login'))

class GetWidget(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        temp_name = self.request.get('template')
        template_name = ''
        template_values = {}
        if temp_name in templateUrls:
            template_name = 'dojoxWidgetLoader.html'
            template_values['template'] = templateUrls[temp_name]
        else:
            template_name = 'widget.html'#carga los views genericos de creacion y listado
        template_values['entity_class']=entityClass
        template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.write(template.render(template_values))


# class GetWidget(webapp2.RequestHandler):
#     def get(self):
#         entityClass = self.request.get('entityClass')
#         temp_name = self.request.get('template')
#         template_values = {'entity_class': entityClass}
#         template_name = ''
#         if temp_name in templateNames:
#             template_name = templateNames[temp_name]
#         else:
#             template_name = 'widget.html'#carga los views genericos de creacion y listado
#         template = JINJA_ENVIRONMENT.get_template(template_name)
#         self.response.write(template.render(template_values))

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

class GetColumns(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        self.response.write(json.dumps(getColumns(entity_class)))
        

def buildQuery(entity_class,params):
    entityClass = classModels[entity_class]
    conditions = []
    for key,value in params.iteritems():
        if key == "entityClass": continue
        if key == "sortBy": continue
        if key == "count": continue
        if key == 'cursor': continue
        if 'fecha' in key:
            if 'Desde' in key:
                condition = entityClass._properties['fecha'] >= datetime.strptime(value, "%Y-%m-%d").date()
            elif 'Hasta' in key:
                condition = entityClass._properties['fecha'] <= datetime.strptime(value, "%Y-%m-%d").date()
        else:
            if not isinstance(value, list):
                condition = entityClass._properties[key]==value
            else:
                orConditions = []
                for orVal in value:
                    orConditions.append(entityClass._properties[key] == orVal)
                condition = ndb.OR(*orConditions)
        conditions.append(condition)
    if 'sortBy' in params.keys():
        descending = True if params['sortBy'][0]=='-' else False
        sortField = keyDefs[entity_class][0]
        if descending:
            return entityClass.query(*conditions).order(-entityClass._properties[sortField])
        else:
            return entityClass.query(*conditions).order(entityClass._properties[sortField])
    else:
        return  entityClass.query(*conditions)

def prepareRecords(entity_class, entities):
    records=[]
    props = classModels[entity_class]._properties
    for entity in entities:
        dicc = entity.to_dict()
        dicc = {key: dicc[key] for key in dicc if type(props[key]) != ndb.StructuredProperty }
        for prop_key, prop_value in dicc.iteritems():
            if type(prop_value) == ndb.Key:
                try:
                    dicc[prop_key]= dicc[prop_key].get().to_dict()['rotulo']
                except Exception:
                    dicc[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
            if type(prop_value) == date:
                dicc[prop_key] = prop_value.strftime('%Y-%m-%d')
            if type(prop_value) == list:
                value = ''
#                 for item in prop_value:
#                     value += item.get().to_dict()['rotulo'] + ';'
                if prop_value:
                    value = prop_value[0].get().to_dict()['rotulo']#if a list, return the first value. To return a separated list, use a computed property...
                dicc[prop_key] = value
        dicc['id'] = entity.key.id()
        records.append(dicc)
    return records


def getEntitiesByPage(entity_class, entity_query, count, self):
    curs = Cursor(urlsafe=self.request.get('cursor'))
    entities, next_curs, more = entity_query.fetch_page(count, start_cursor=curs)
    records = prepareRecords(entity_class, entities)
    return {'records':records, 'cursor': next_curs.urlsafe() if next_curs else '', 'more':more}

def getEntities(entity_class, self, entity_query):
    entities = entity_query.fetch()
    records = prepareRecords(entity_class, entities)
    return {'records':records, 'count':len(records)}

class EntityData(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass');
        entity_query = buildQuery(entity_class, self.request.params)
        count = self.request.get('count');
        if count:
            response = getEntitiesByPage(entity_class, entity_query, int(count), self)
        else:
            response = getEntities(entity_class, self, entity_query)    
        self.response.write(json.dumps(response))        

class Home(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
            if empleado:
                template_values = {'user': user}
                template = JINJA_ENVIRONMENT.get_template('home.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect(users.create_login_url('/login'))
        else:
            self.redirect(users.create_login_url('/login'))
              
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
        if type(value) is ndb.BooleanProperty:#checkbox value should be 'si'o 'no'
            values[key] = True if (values[key] == 'si' or values[key])  else False
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
            if key == 'fechaCreacion':
                values[key]=date.today()
            else:
                try:
                    values[key] = datetime.strptime(values[key], '%Y-%m-%d').date()
                except:
                    start = values[key].find( '(' )
                    end = values[key].find( ')' )
                    if start != -1 and end != -1:
                        result = values[key][start:end+1]
                        fecha = values[key].replace(result,'')
                    values[key] = parser.parse(fecha)
        if type(value) == ndb.StructuredProperty:
            objList = []
            listVals = values[key]
            for listItem in listVals:
                obj = check_types(value._modelclass._class_name(),listItem)             
                objList.append(value._modelclass(**obj))
            values[key]=objList
        if key == 'empleadoCreador':
            values[key] = users.get_current_user().email()

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
        autoIncrease(entity_class)
        return {'message':"Created",'key':key, 'entity':entity}

class SaveEntity(webapp2.RequestHandler):        
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        entity_class = values.pop("entity_class")     
        for key,value in values.iteritems():
            values[rreplace(key, '_' + entity_class,'',1)] = values.pop(key)
        response = create_entity(entity_class,values)
        if entity_class in postSaveAction:
            postSaveAction[entity_class](response['entity'])
        self.response.out.write(JSONEncoder().encode(response))


def tagForField(entity_class, prop=None, auto=None):
    tag = ''
    if not prop:
        prop = fieldsInfo(entity_class)
    if auto and prop['id'] in auto:
        readonly = '' if 'editable' in prop else 'readonly' 
        tag = '<input type="text" id="' + prop['id'] +  '_' + entity_class +'" name="'+ prop['id'] + '_' +entity_class 
        tag +='" required="' + prop['required'] 
        tag += '" data-dojo-type="' + prop['valid'] +'" style="width: ' + prop['width'] + ';"' + ' value="' + str(auto[prop['id']]) + '"' + readonly
        tag += '/>'
    elif type(prop['type']) == ndb.KeyProperty:
        tag = "<select name='" + prop['id'] + '_' + entity_class + "' id='" + prop['id'] + '_' + entity_class + "' data-dojo-type='dijit/form/Select'>"
        options = classModels[prop['type']._kind].query().fetch()
        for option in options:
            dicc = option.to_dict()
            option_value = getKey(prop['type']._kind, dicc)
            tag += "<option value='" + option_value + "'>" + option.rotulo + '</option>'
        tag += "</select>"
        if prop['type']._repeated == True:
            tag += '<button class = "listprop" id="listpropBtnAgregar' + '_' + entity_class + '_' + prop['id'] + '" data-dojo-type="dijit/form/Button">Agregar</button>'
            tag += '<button class = "listprop" id="listpropBtnQuitar' + '_' + entity_class + '_' + prop['id'] + '" data-dojo-type="dijit/form/Button">Quitar</button>'
            tag += '<br/><textarea readOnly="True" class = "listpropTextarea" id="text' + prop['id'] + '_' + entity_class + '" data-dojo-type="dijit/form/SimpleTextarea" rows="3" cols="30" style="width:auto;"></textarea>'
    elif type(prop['type']) == ndb.DateProperty:
        tag = '<input type="text" name="' + prop['id'] + '_' + entity_class + '" id="' + prop['id'] + '_' + entity_class + '" value="now" data-dojo-type="dijit/form/DateTextBox" constraints="{datePattern:\'yyyy-MM-dd\', strict:true}" required="true"/>'
    elif type(prop['type']) == ndb.TextProperty:
        tag = '<textarea id="' + prop['id'] +  '_' + entity_class +'" name="'+ prop['id'] + '_' + entity_class 
        tag +='" required="' + prop['required'] 
        tag += '" data-dojo-type="' + prop['valid'] +'" rows="3" cols="30" style="width:auto;"/></textarea>'
    elif type(prop['type']) == ndb.BooleanProperty:
        tag = '<input id="' + prop['id'] +  '_' + entity_class +'" name="'+ prop['id'] + '_' + entity_class +'" data-dojo-type="dijit.form.CheckBox" value="si"'
        tag += 'onChange="this.checked ? document.getElementById(\''+ prop['id'] +  '_' + entity_class +'hidden\').disabled = true : document.getElementById(\''+ prop['id'] +  '_' + entity_class +'hidden\').disabled = false "/>'
        tag += '<input id="' + prop['id'] +  '_' + entity_class +'hidden" name="'+ prop['id'] + '_' + entity_class +'hidden" type="hidden" value="no" data-dojo-type="dijit.form.TextBox"/>'
    else:
        value = str(prop['default']) if 'default' in prop else ''
        tag = '<input type="text" id="' + prop['id'] +  '_' + entity_class +'" name="'+ prop['id'] + '_' + entity_class 
        tag +='" required="' + prop['required'] 
        dojoprops = ' data-dojo-props="' + prop['dojoprops'] + '"' if 'dojoprops' in prop else ''
        tag += '" data-dojo-type="' + prop['valid'] + '" style="width: ' + prop['width'] + ';"' + ' value="' + value + '"' + dojoprops
        tag += 'disabled' if 'disabled' in prop else ''
        tag += '/>'
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
    if entity in createTemplateStrings:
        return createTemplateStrings[entity]
    else:
        return '/addEntity?entityClass=' + entity        

def fieldsInfo(entity_class):
    props = classModels[entity_class]._properties
    fields = uiConfig[entity_class]
    for field in fields:
        field['type']=props[field['id']]
    return fields

def autoIncrease(entity_class):
    if 'Numero' + entity_class in singletons:
        num = singletons['Numero' + entity_class].query().get()
        num.consecutivo = num.consecutivo + 1
        num.put() 

def autoNum(entity_class):
    if 'Numero' + entity_class in singletons:
        num = singletons['Numero' + entity_class].query().get()
        if num:
            return {'numero': num.consecutivo + 1}
        else:
            singletons['Numero' + entity_class](consecutivo=1).put()
            return  {'numero': 1}
    else:
        return None          

class AddEntity(webapp2.RequestHandler):
    def get(self):
        entity_class = self.request.get('entityClass')
        template_values = {'entity_class': entity_class, 'fields': fieldsInfo(entity_class), 'auto':autoNum(entity_class)}
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
        precios = Precio.query(Precio.grupoDePrecios == grupo,  projection = [Precio.producto], distinct=True).fetch()
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
        precios = Precio.query(Precio.grupoDePrecios == grupo,
                               Precio.producto == producto.key,
                               projection = [Precio.porcion], distinct=True).fetch()
        porciones = [precio.porcion.id() for precio in precios]
        self.response.out.write(json.dumps(porciones))        


class GetPrice(webapp2.RequestHandler):
    def post(self):
        post_data = self.request.POST
        values = post_data.mixed()
        precioQuery = Precio.query(Precio.producto == Producto.get_by_id(values['producto']).key,
                                   Precio.grupoDePrecios == Cliente.get_by_id(values["cliente"]).grupoDePrecios,
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
        entity_query = buildQuery('Factura', self.request.params)
        facturas = entity_query.fetch()
        for factura in facturas:
            if factura.anulada: continue
            for venta in factura.ventas:
                venta = venta.to_dict()
                venta['peso']=venta['porcion'].get().valor * venta['cantidad']
                venta['ciudad']=factura.cliente.get().ciudad.get().rotulo
                venta['factura']=factura.numero
                venta['cliente']=factura.cliente.id()
                venta['fecha']=factura.fecha
                venta['mesnum']=factura.fecha.month
                venta['mes']=factura.fecha.strftime('%B')
                venta['year']=factura.fecha.year
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
           

class GetAllCompras(webapp2.RequestHandler):
    def get(self):
        records = []
        entity_query = buildQuery('Egreso', self.request.params)
        egresos = entity_query.fetch()
        for egreso in egresos:
            for compra in egreso.compras:
                compra = compra.to_dict()
                compra['egreso']=egreso.numero
                compra['proveedor']=egreso.proveedor.get().rotulo
                compra['fecha']=egreso.fecha
                compra['mesnum']=egreso.fecha.month
                compra['mes']=egreso.fecha.strftime('%B')
                compra['year']=egreso.fecha.year
                compra['tipo']=egreso.tipo.get().rotulo
                compra['sucursal']=egreso.sucursal.get().rotulo
                records.append(compra)
        response = {'records':records}
        self.response.out.write(JSONEncoder().encode(response))


class CrearEgreso(webapp2.RequestHandler):
    def get(self):
        prop_tipo = Egreso._properties['tipo']
        prop_proveedor = Egreso._properties['proveedor']
#         prop_empleado = Egreso._properties['empleado']
        prop_bienoservicio = Compra._properties['bienoservicio']
        prop_detalle = Compra._properties['detalle']
        prop_comentario = Egreso._properties['comentario']
        prop_cantidad = Compra._properties['cantidad']
        prop_precio = Compra._properties['precio']
        prop_sucursal = Egreso._properties['sucursal']
        empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
        empleadoName = empleado.rotulo
        empleadoValue = empleado.key.id()
        props = {'proveedor':{'ui': 'Proveedor', 'id': 'proveedor','required':'true','type':prop_proveedor},
#                  'empleado':{'ui': 'Empleado', 'id': 'empleado','required':'true','type':prop_empleado},
                 'empleado': {'value':empleadoValue,'label':empleadoName},
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
        template_values = {'props': props, 'entityClass':'Egreso'}
        template = JINJA_ENVIRONMENT.get_template('crearEgreso.html')
        self.response.write(template.render(template_values))

class CrearFactura(webapp2.RequestHandler):
    def get(self):
        entityClass = self.request.get('entityClass')
        prop_cliente = Factura._properties['cliente']
#         prop_empleado = Factura._properties['empleado']
        prop_producto = Venta._properties['producto']
        prop_porcion = Venta._properties['porcion']
        prop_cantidad = Venta._properties['cantidad']
        empleado = Empleado.query(Empleado.email == users.get_current_user().email()).get()
        empleadoName = empleado.rotulo
        empleadoValue = empleado.key.id()
        props = {'Cliente':{'ui': 'Cliente', 'id': 'cliente','required':'true','type':prop_cliente},
#                  'Empleado':{'ui': 'Empleado', 'id': 'empleado','required':'true','type':prop_empleado},
             'Empleado': {'value':empleadoValue,'label':empleadoName},
             'Producto':{'ui': 'Producto', 'id': 'producto','required':'true','type':prop_producto},
             'Porcion':{'ui': 'Porcion', 'id': 'porcion','required':'true','type':prop_porcion},
             'Cantidad':{'ui': 'Cantidad', 'id': 'cantidad','required':'true', 'valid':'dijit/form/NumberTextBox',
                         'width':'5em', 'type':prop_cantidad}
            }
        template_values = {'props': props, 'entityClass':entityClass}
        template = JINJA_ENVIRONMENT.get_template('crearFactura.html')
        self.response.write(template.render(template_values))
        
class SetNumber(webapp2.RequestHandler):
    def get(self):
        tipo = self.request.get('tipo')
        newNumero = self.request.get('numero')
        msg ='Se definio el numero de ' + tipo +' actual como: ' + newNumero
        if 'Numero' + tipo in singletons:
            model = singletons['Numero' + tipo]
            numero = model.query().get()
            if numero:
                numero.consecutivo = int(newNumero)
                numero.put()
            else:
                model(consecutivo=int(newNumero)).put()
        else:
            msg = 'Parametro "tipo" debe estar en "singletons"'
        self.response.write(msg)

def getConsecutivo(entity_class):
    tipo = {'Remision' : NumeroRemision, 'Factura' : NumeroFactura }
    numero = tipo[entity_class].query().fetch()
    if numero:
        numero[0].consecutivo = numero[0].consecutivo + 1
        numero[0].put()
        return numero[0].consecutivo
    else:
        tipo[entity_class](consecutivo=int(0)).put()
        return 0;
         
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
            numero = getConsecutivo(values['entity_class'])
        
        if values['entity_class'] == 'Remision':
            remision = Remision(id=str(numero), numero=int(numero), cliente = cliente.key, empleado = empleado.key,
                                 fecha = fecha, ventas=ventas, total=int(values['total']),subtotal=values['subtotal'],
                                 montoIva=values['iva'])
            remision.put()
            entity = remision
        else:
            factura = Factura(id=str(numero), numero=int(numero), cliente = cliente.key, 
                              empleado = empleado.key, fecha = fecha, ventas=ventas, total=int(values['total']),
                              subtotal=values['subtotal'], 
                               montoIva=values['iva'])
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
                'ciudad': unicode(cliente.ciudad.get().rotulo),
                'nit':cliente.nit, 
                'fecha': entity.fecha.strftime('%Y-%m-%d'),
                'telefono':cliente.telefono,
                'empleado': empleado.rotulo,
                'numVentas':len(entity.ventas),
                'total': '{:,.0f}'.format(entity.total),
                'iva': '{:,.0f}'.format(entity.montoIva),
                'subtotal': '{:,.0f}'.format(entity.subtotal if entity.montoIva != 0 else 0),
                'exento':'{:,.0f}'.format(entity.subtotal if entity.montoIva==0 else 0),
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

##################### FORMULAS P&G ##################################
# This function assumes the queried entities have a 'total' field
def getTotalFromModel(model, qryParams):
#     qryParams.pop("resumen", None)
    query = buildQuery(model, qryParams)
    entities = query.fetch()
    if entities:
        return sum([entity.total for entity in entities])
    else:
        return 0

def getDepreciaciones(fechaDesde, fechaHasta):
    return 0 # Figure out what this should be

def getServiciosPublicos(fechaDesde, fechaHasta):
    electricidad = getTotalFromModel('Egreso', {'resumen':'Servicios.Publicos-Energia',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    telecom = getTotalFromModel('Egreso', {'resumen':'Servicios.Publicos-Telecomunicaciones',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    gas = getTotalFromModel('Egreso', {'resumen':'Servicios.Publicos-Gas',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    agua = getTotalFromModel('Egreso', {'resumen':'Servicios.Publicos-Agua',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    return edict({'total': electricidad + telecom + gas + agua,
                  'electricidad':electricidad,'telecom':telecom,'gas':gas,'agua':agua})


def getCostosIndirectos(fechaDesde, fechaHasta):
    serviciosPublicos = getServiciosPublicos(fechaDesde, fechaHasta)
    arriendo = getTotalFromModel('Egreso', {'resumen':'Arriendo',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta}
                                 )
    varios = getTotalFromModel('Egreso', {'resumen':['Servicios-Varios',
                                                     'Servicios-Fumigacion',
                                                     'Alimentacion.Empleado',
                                                     'Utensilios',
                                                     'Vigilancia',
                                                     'Combustible',
                                                     'Dotacion',
                                                     'Dotacion.empleados',
                                                     'Pruebas.laboratorio',
                                                     'Cursos.para.el.personal',
                                                     'Medicinas.Botiquin'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta}
                               )
    return edict({'total':serviciosPublicos.total + arriendo + varios,
            'serviciosPublicos':serviciosPublicos,'arriendo':arriendo,'varios':varios})

def getManoDeObra(fechaDesde, fechaHasta):
    manoDeObraDirecta = getTotalFromModel('Egreso', {'resumen':'Nomina.-.Operativa',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    manoDeObraIndirecta = getTotalFromModel('Egreso', {'resumen':'Nomina-Turnos',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    return edict({'total' : manoDeObraDirecta + manoDeObraIndirecta,
            'manoDeObraDirecta': manoDeObraDirecta, 'manoDeObraIndirecta': manoDeObraIndirecta})

def getMateriaPrima(fechaDesde, fechaHasta):
    materiaPrimaFruta = getTotalFromModel('Egreso', {'resumen':'Materia.Prima-Fruta',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    materiaPrimaVarios = getTotalFromModel('Egreso', {'resumen':['Materia.Prima-Bolsas.Plasticas',
                                                                 'Materia.Prima-Varios',
                                                                 'Materia.Prima-Quimicos',
                                                                 'Materia.Prima-Implementos.de.Aseo',
                                                                 'Materia.Prima-Hielo.Seco',
                                                                 ],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    return edict({'total':materiaPrimaFruta + materiaPrimaVarios,
            'materiaPrimaFruta':materiaPrimaFruta, 'materiaPrimaVarios':materiaPrimaVarios}) 

def getCostosDeProduccion(fechaDesde, fechaHasta):
    materiaPrima = getMateriaPrima(fechaDesde, fechaHasta)
    manoDeObra = getManoDeObra(fechaDesde, fechaHasta)
    costosIndirectos = getCostosIndirectos(fechaDesde, fechaHasta)
    depreciaciones = getDepreciaciones(fechaDesde, fechaHasta)
    return edict({'total': materiaPrima.total + manoDeObra.total + costosIndirectos.total + depreciaciones,
            'materiaPrima':materiaPrima , 'manoDeObra':manoDeObra , 'costosIndirectos':costosIndirectos , 'depreciaciones':depreciaciones})
    
def getVentasNetas(fechaDesde, fechaHasta):
    ventasPyG = getTotalFromModel('Factura', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta})
    devoluciones = getTotalFromModel('Devolucion', {'fechaDesde':fechaDesde,'fechaHasta': fechaHasta})
    return edict({'total': ventasPyG - devoluciones, 'ventas': ventasPyG, 'devoluciones': devoluciones})

def getGastosDeVentas(fechaDesde,fechaHasta):
    impuestos = getTotalFromModel('Egreso', {'resumen':['Impuestos.Nacionales',
                                                        'Impuestos.Distritales'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    transportes = getTotalFromModel('Egreso', {'resumen':['Transporte.del.Producto-Local',
                                                        'Transporte.del.Producto-Intermunicipal',
                                                        'Taxis.y.Pasajes.de.Bus'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    mantenimientoVehiculos = getTotalFromModel('Egreso', {'resumen':'Mantenimiento.de.vehiculos',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    parqueadero = getTotalFromModel('Egreso', {'resumen':'Parqueadero',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    publicidad = getTotalFromModel('Egreso', {'resumen':'Publicidad',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    
    return edict({'total': impuestos + transportes + mantenimientoVehiculos + parqueadero + publicidad,
            'impuestos':impuestos,'transportes':transportes,'mantenimientoVehiculos':mantenimientoVehiculos,
            'parqueadero':parqueadero,'publicidad':publicidad})

def getGastosAdministrativos(fechaDesde,fechaHasta):
    gastosDePersonal = getTotalFromModel('Egreso', {'resumen':'Nomina.-.Administrativa',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    honorarios = getTotalFromModel('Egreso', {'resumen':'Honorarios',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    mantenimientoYreparaciones = getTotalFromModel('Egreso', {'resumen':['Mantenimiento.y.arreglos.locativos',
                                                                         'Materiales.de.Construccion'],
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    gastosLegales = getTotalFromModel('Egreso', {'resumen':'Gastos.legales',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    papeleriaYfotocopias =  getTotalFromModel('Egreso', {'resumen':'Papeleria',
                                                     'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    camaraDeComercio = getTotalFromModel('Egreso', {'resumen':'Camara.de.comercio',
                                                    'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    return edict({'total': gastosDePersonal + honorarios + mantenimientoYreparaciones + gastosLegales + papeleriaYfotocopias + camaraDeComercio,
            'gastosDePersonal':gastosDePersonal,'honorarios':honorarios, 'mantenimientoYreparaciones':mantenimientoYreparaciones,
            'gastosLegales' : gastosLegales, 'papeleriaYfotocopias': papeleriaYfotocopias, 'camaraDeComercio': camaraDeComercio})

def getOtrosGastos(fechaDesde, fechaHasta):
    gastosFinancieros = getTotalFromModel('Egreso', {'resumen':'Servicios.Financieros',
                                                    'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    gastosExtraordinarios = getTotalFromModel('Egreso', {'resumen':'Gastos.Extraordinarios',
                                                    'fechaDesde':fechaDesde,
                                                     'fechaHasta': fechaHasta})
    return edict({'total': gastosFinancieros + gastosExtraordinarios,
            'financieros':gastosFinancieros,'extraordinarios':gastosExtraordinarios})

def getIngresosNoOperacionales(fechaDesde, fechaHasta):
    return getTotalFromModel('OtrosIngresos', {'fechaDesde':fechaDesde, 'fechaHasta': fechaHasta})

def getImpuestos(fechaDesde, fechaHasta):
    renta = getTotalFromModel('Egreso', {'resumen':['Impuesto.-.Renta',
                                                    'Impuestos.Nacionales'], 
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta':fechaHasta})
    cree = getTotalFromModel('Egreso', {'resumen':'Impuesto.-.CREE', 
                                         'fechaDesde':fechaDesde,
                                         'fechaHasta':fechaHasta})
    return edict({'total':renta + cree, 'renta':renta, 'cree':cree})

def getPyGData(fechaDesde,fechaHasta):
    ventasNetas = getVentasNetas(fechaDesde, fechaHasta)
    costos = getCostosDeProduccion(fechaDesde, fechaHasta)
    utilidadBruta = ventasNetas.total - costos.total
    margenBruto = utilidadBruta/ventasNetas.total
    gastosDeVentas = getGastosDeVentas(fechaDesde,fechaHasta)
    gastosAdministrativos = getGastosAdministrativos(fechaDesde,fechaHasta)
    utilidadOperacional = ventasNetas.total - costos.total - gastosAdministrativos.total - gastosDeVentas.total
    margenOperacional = utilidadOperacional / ventasNetas.total
    otrosGastos = getOtrosGastos(fechaDesde, fechaHasta)
    ingresosNoOperacionales = getIngresosNoOperacionales(fechaDesde, fechaHasta)
    utilidadAntesDeImpuestos = utilidadOperacional - otrosGastos.total + ingresosNoOperacionales
    margenAntesDeImpuestos = utilidadAntesDeImpuestos / ventasNetas.total
    impuestos = getImpuestos(fechaDesde,fechaHasta)
    utilidadNeta = utilidadAntesDeImpuestos - impuestos.total 
    margenNeto = utilidadNeta/ventasNetas.total
    return {'desde':fechaDesde,
            'hasta':fechaHasta,
            'ventasNetas': '${:,}'.format(ventasNetas.total) , 
            'ventas': '${:,}'.format(ventasNetas.ventas),
            'devoluciones':'${:,}'.format(ventasNetas.devoluciones), 
            'costos': '${:,}'.format(costos.total),
            'materiaPrima':'${:,}'.format(costos.materiaPrima.total),
            'materiaPrimaFruta':'${:,}'.format(costos.materiaPrima.materiaPrimaFruta),
            'materiaPrimaVarios':'${:,}'.format(costos.materiaPrima.materiaPrimaVarios),
            'manoDeObra':'${:,}'.format(costos.manoDeObra.total),
            'manoDeObraDirecta':'${:,}'.format(costos.manoDeObra.manoDeObraDirecta),
            'manoDeObraIndirecta':'${:,}'.format(costos.manoDeObra.manoDeObraIndirecta),
            'costosIndirectos':'${:,}'.format(costos.costosIndirectos.total),
            'serviciosPublicos': '${:,}'.format(costos.costosIndirectos.serviciosPublicos.total),
            'electricidad':'${:,}'.format(costos.costosIndirectos.serviciosPublicos.electricidad),
            'gas':'${:,}'.format(costos.costosIndirectos.serviciosPublicos.gas),
            'telecom':'${:,}'.format(costos.costosIndirectos.serviciosPublicos.telecom),
            'agua':'${:,}'.format(costos.costosIndirectos.serviciosPublicos.agua),
            'arriendo' : '${:,}'.format(costos.costosIndirectos.arriendo),
            'costosIndirectosVarios': '${:,}'.format(costos.costosIndirectos.varios),
            'depreciaciones': '${:,}'.format(getDepreciaciones(fechaDesde, fechaHasta)), 
            'utilidadBruta' : '${:,}'.format(utilidadBruta),
            'margenBruto': '{:.2%}'.format(margenBruto),
            'gastosDeVentas':'${:,}'.format(gastosDeVentas.total),
            'gastosDeVentasImpuestos':'${:,}'.format(gastosDeVentas.impuestos),
            'transportes':'${:,}'.format(gastosDeVentas.transportes),
            'mantenimientoVehiculos':'${:,}'.format(gastosDeVentas.mantenimientoVehiculos),
            'parqueadero':'${:,}'.format(gastosDeVentas.parqueadero),
            'publicidad':'${:,}'.format(gastosDeVentas.publicidad),
            'gastosAdministrativos':'${:,}'.format(gastosAdministrativos.total),
            'gastosDePersonal':'${:,}'.format(gastosAdministrativos.gastosDePersonal),
            'honorarios':'${:,}'.format(gastosAdministrativos.honorarios),
            'mantenimientoYreparaciones':'${:,}'.format(gastosAdministrativos.mantenimientoYreparaciones),
            'gastosLegales':'${:,}'.format(gastosAdministrativos.gastosLegales),
            'papeleriaYfotocopias':'${:,}'.format(gastosAdministrativos.papeleriaYfotocopias),
            'camaraDeComercio':'${:,}'.format(gastosAdministrativos.camaraDeComercio),
            'utilidadOperacional':'${:,}'.format(utilidadOperacional),
            'margenOperacional':'{:.2%}'.format(margenOperacional),
            'ingresosNoOperacionales':'${:,}'.format(ingresosNoOperacionales),
            'otrosGastos':'${:,}'.format(otrosGastos.total),
            'financieros':'${:,}'.format(otrosGastos.financieros),
            'extraordinarios':'${:,}'.format(otrosGastos.extraordinarios),
            'utilidadAntesDeImpuestos':'${:,}'.format(utilidadAntesDeImpuestos),
            'margenAntesDeImpuestos':'{:.2%}'.format(margenAntesDeImpuestos),
            'impuestos':'${:,}'.format(impuestos.total),
            'renta':'${:,}'.format(impuestos.renta),
            'cree':'${:,}'.format(impuestos.cree),
            'utilidadNeta':'${:,}'.format(utilidadNeta),
            'margenNeto': '{:.2%}'.format(margenNeto)
    }


class PyG(webapp2.RequestHandler):
    def get(self):
        fechaDesde = self.request.get('fechaDesde')
        fechaHasta = self.request.get('fechaHasta')
        pYgData = getPyGData(fechaDesde,fechaHasta)
        template = JINJA_ENVIRONMENT.get_template('PyG.htm')
        self.response.write(template.render(pYgData))

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
#             print record
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
        
class DojoxLoader(webapp2.RequestHandler):
    def get(self): 
        template_values = {'entity_class': self.request.get('entityClass')}
        template = self.request.get('template')
        template = JINJA_ENVIRONMENT.get_template(template)
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

        resumen = compras[0].bienoservicio.id() #if len(compras)==1 else compras[0].bienoservicio.id() + ', etc.' #think of a better way to do this! 
        egreso = Egreso(id=str(numero), numero=int(numero), resumen = resumen, tipo = tipo.key, proveedor = proveedor.key, 
                        empleado = empleado.key, fecha = fecha, compras=compras, total=values['total'], sucursal = sucursal.key,
                        comentario = values['comentario'])
        egreso.put()
        entity = egreso
        self.response.out.write(json.dumps({'result':'Success','egresoId': entity.key.id()}))
        

class GetCuentasPorCobrar(webapp2.RequestHandler):
    def get(self):
        response = []
        saldos={}
        facturas = Factura.query(Factura.pagada == False).fetch()
        for factura in facturas:
            if factura.cliente.id() in saldos:
                saldos[factura.cliente.id()] += factura.total-factura.abono
            else:
                saldos[factura.cliente.id()] = factura.total-factura.abono
        for key,value in saldos.iteritems():
            response.append({'id':key,'cliente':key, 'monto':value})
        self.response.out.write(json.dumps(response))

class GetDetalleCuentasPorCobrar(webapp2.RequestHandler):
    def get(self):
        cliente = self.request.get('cliente') 
        facturas = Factura.query(Factura.cliente == ndb.Key('Cliente',cliente))
        response = [{'id':factura.numero, 'factura':factura.numero,'fecha':factura.fecha,'total':factura.total, 'abono':factura.abono} for factura in facturas if not factura.pagada]
        self.response.out.write(JSONEncoder().encode(response))    
        
class FixPrecios(webapp2.RequestHandler):
    def get(self):
        precios = Precio.query().fetch()
        for precio in precios:
            if precio.grupoDePrecios:
                precio.grupo = precio.grupoDePrecios
            if 'grupoDePrecios' in precio._properties:
                del precio._properties['grupoDePrecios']
            precio.put()

JINJA_ENVIRONMENT.globals['tagForField']=tagForField
JINJA_ENVIRONMENT.globals['adjustText']=adjustText
JINJA_ENVIRONMENT.globals['isAdminUser']=isAdminUser
JINJA_ENVIRONMENT.globals['createTemplateString']=createTemplateString
JINJA_ENVIRONMENT.globals['autoNum']=autoNum        