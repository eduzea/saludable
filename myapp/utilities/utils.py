'''
Created on Aug 8, 2015

@author: eduze_000
'''
from datetime import time, datetime, timedelta, date
from dateutil import parser
from myapp.config import *

import logging
import json

#returns a copy of given dict with the specified key removed
def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


#String replace from the right, specifying # of replacements to make.
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

# Parse date string given by javascript
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
    for column in uiConfigShow[entityClass]:
        colProps = { 'id':column['id'], 'field' : column['id'], 'name' : column['ui'], 'style': "text-align: center", 'width':column['style'].split(':')[1]}
        if 'type' in column:
            colProps['type']=column['type']
        #probably should not assume that computed properties are of type Integer! Will declare the type explicitly in config...
        if column['id'] in props and ( type(props[column['id']]) == ndb.IntegerProperty or type(props[column['id']]) == ndb.ComputedProperty)  :
            if not props[column['id']]._repeated and 'type' not in column:
                colProps['type']='Integer'
        columns.append(colProps);
    return {'columns':columns,'key':keyDefs[entityClass]}

def prepareRecords(entityClass, entities):
    records=[]
    props = classModels[entityClass]._properties
    fields = [field['id'] for field in uiConfigShow[entityClass]]
    for entity in entities:
        try:
            dicc = entity.to_dict()
    #         dicc = {key: dicc[key] for key in dicc if key in props and type(props[key]) != ndb.StructuredProperty }
            keysToRemove =[]
            for prop_key, prop_value in dicc.iteritems():
                if type(prop_value) == ndb.Key:
                    try:
                        dicc[prop_key]= dicc[prop_key].get().to_dict()['rotulo']
                    except Exception:
                        dicc[prop_key] = "Ya no hay: " + unicode(prop_value) + ' Considera borrar este registro o recrear ' + unicode(prop_value)
                if type(prop_value) == date or type(prop_value) == datetime :
                    dicc[prop_key] = prop_value.strftime('%Y-%m-%d')
                ############# For dealing with old objects that no longer match the model definition
                if prop_key not in props:
                    del entity._properties[prop_key]
                    entity.put()
                    continue
                ##########
                if type(prop_value) == messages.Enum:
                    dicc[prop_key] = prop_value
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
        except Exception as e:
            logging.debug('Failed in {0} : {1}'.format(entityClass, entity.numero))
            logging.debug('Error: {0}'.format(e.message))
            continue
    return records            

def createTemplateString(entity):
    if entity in templateStrings:
        return templateStrings[entity]
    else:
        return '/addEntity?entityClass=' + entity        

def fieldInfo(entityClass, fieldName):
    props = classModels[entityClass]._properties
    fields = uiConfigShow[entityClass]    
    fieldProp = {}
    for field in fields:
        if field['id'] == fieldName:
            fieldProp = field 
            fieldProp['type']= props[fieldName]
            return fieldProp

def fieldsInfo(entityClass):
    props = classModels[entityClass]._properties
    fields = uiConfigAdd[entityClass]
    for field in fields:
        field['type']=props[field['id']]
    return fields

    
def estaVencida(factura):
    diasPago = factura.cliente.get().diasPago
    fechaVencimiento = factura.fecha + timedelta(days=diasPago)
    return date.today() > fechaVencimiento
     
getTemplateData={}

# This is bad, abstraction leak. The details of the model should be accessed thought the interface only!
def getEgresoFrutaTemplateData(request):
    props = {'detalle':{'type':Compra._properties['detalle'],'style': 'width:10em', 'ui': 'Fruta', 'id': 'detalle'},
             'cantidad':{'type':Compra._properties['cantidad'],'style': 'width:5em;text-align: right', 'ui': 'Cantidad(kg)', 'id': 'cantidad'},
             'precio':{'type':Compra._properties['precio'],'style': 'width:5em;text-align: right', 'ui': 'Precio', 'id': 'precio'},
             'comentario':{'ui': 'Comentario', 'id': 'comentario','required':'false','style':'width:50em','type':Egreso._properties['comentario']}
                                           }    
    return {'props':props}    

getTemplateData['Fruta'] = getEgresoFrutaTemplateData


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
        elif isinstance(o, messages.Enum):
            return str(o)
        else:
            print "Hold on! Unexpected type!"
