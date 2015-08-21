'''
Created on Aug 8, 2015

@author: eduze_000
'''
from datetime import time
from dateutil import parser
from config import *
from datastorelogic import *

#String replace from the right, specifying # of replacements to make.
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

def parseDateString(string):
    start = string.find( '(' )
    end = string.find( ')' )
    fecha = string
    if start != -1 and end != -1:
        result = string[start:end+1]
        fecha = string.replace(result,'')
    return parser.parse(fecha)
    
def getColumns(entityClass):
    columns=[]
    props = classModels[entityClass]._properties
    for column in uiConfig[entityClass]:
        colProps = { 'field' : column['id'], 'name' : column['ui'], 'style': "text-align: center", 'width':column['style'].split(':')[1]}
        if column['id'] in props and type(props[column['id']]) == ndb.IntegerProperty:
            if not props[column['id']]._repeated:
                colProps['type']='Integer'
        columns.append(colProps);
    return {'columns':columns,'key':keyDefs[entityClass]}

def getKey(entityClass,dicc):
    key = u''
    for keypart in keyDefs[entityClass]:
        if type(dicc[keypart]) == ndb.Key:
            entity = dicc[keypart].get()
            if entity:
                key += ' ' + entity.key.id()
            else:
                print "Entity not found by key:" + keypart 
        else:
            key += ' ' + unicode(dicc[keypart])
    return '.'.join(key.split())


def prepareRecords(entityClass, entities):
    records=[]
    props = classModels[entityClass]._properties
    fields = [field['id'] for field in uiConfig[entityClass]]
    for entity in entities:
        dicc = entity.to_dict()
#         dicc = {key: dicc[key] for key in dicc if key in props and type(props[key]) != ndb.StructuredProperty }
        keysToRemove =[]
        for prop_key, prop_value in dicc.iteritems():
            if type(prop_value) == ndb.Key:
                try:
                    dicc[prop_key]= dicc[prop_key].get().to_dict()['rotulo']
                except Exception:
                    dicc[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
            if type(prop_value) == date:
                dicc[prop_key] = prop_value.strftime('%Y-%m-%d')
            if type(prop_value) == bool: 
                dicc[prop_key] = 'Si' if prop_value == True else 'No'
            if type(props[prop_key]) == ndb.StructuredProperty:
                if type(prop_value) == list:
                    dicc[prop_key] = ', '.join({item['rotulo'] for item in prop_value})
            elif type(prop_value) == list:
                value = ''
                if prop_value:
                    if type(prop_value[0]) == ndb.Key:
                        if prop_value[0].get():
                            value = prop_value[0].get().to_dict()['rotulo']#if a list, return the first value. To return a separated list, use a computed property...
                        else:
                            print 'Inconsistent record: ', prop_value[0]
                    else:
                        value = ', '.join(str(x) for x in prop_value)
                dicc[prop_key] = value
        dicc = {key: dicc[key] for key in dicc if key not in keysToRemove}
        dicc['id'] = entity.key.id()
        records.append(dicc)
    return records            

def createTemplateString(entity):
    if entity in templateStrings:
        return templateStrings[entity]
    else:
        return '/addEntity?entityClass=' + entity        

def fieldsInfo(entityClass):
    props = classModels[entityClass]._properties
    fields = uiConfig[entityClass]
    for field in fields:
        field['type']=props[field['id']]
    return fields

def getConsecutivo(entityClass):
    tipo = {'Remision' : NumeroRemision, 'Factura' : NumeroFactura }
    numero = tipo[entityClass].query().fetch()
    if numero:
        numero[0].consecutivo = numero[0].consecutivo + 1
        numero[0].put()
        return numero[0].consecutivo
    else:
        tipo[entity_class](consecutivo=int(0)).put()
        return 0;
    
#################### INVENTARIO #########################
getTemplateData={}
def getInventarioTemplateData(request):
    prop_ciudad = InventarioRegistro._properties['sucursal']
    prop_producto = InventarioRegistro._properties['producto']
    prop_porcion = InventarioRegistro._properties['porcion']
    prop_existencias = InventarioRegistro._properties['existencias']
    props = {
             'sucursal':{'ui': 'Sucursal', 'id': 'sucursal','required':'true','type':prop_ciudad},
             'producto':{'ui': 'Producto', 'id': 'producto','required':'true','type':prop_producto},
             'porcion':{'ui': 'Porcion', 'id': 'porcion','required':'true','type':prop_porcion},
             'existencias':{'ui': 'Existencias', 'id': 'existencias','required':'true',
                     'style':'width:3em', 'type':prop_existencias}
        }
    return {'props':props}

    
getTemplateData['Inventario'] = getInventarioTemplateData



def getConsecutivoEgreso():
    numero = NumeroEgreso.query().fetch()
    if numero:
        numero[0].consecutivo = numero[0].consecutivo + 1
        numero[0].put()
        return numero[0].consecutivo
    else:
        NumeroEgreso(consecutivo=1).put()
        return 1 

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ndb.key.Key):
            if hasattr(self, 'unpack'):
                if o.kind() in self.unpack:
                    return o.get().to_dict()
                else:
                    return o.id()
            else:
                return o.id()
        if isinstance(o, ndb.Model):
            return o.to_dict()
        elif isinstance(o, (datetime, date, time)):
            return str(o)  # Or whatever other date format you're OK with...
        else:
            print "Hold on! Unexpected type!"
