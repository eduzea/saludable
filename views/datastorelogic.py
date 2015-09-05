'''
Created on Aug 8, 2015

@author: eduze_000
'''
import json
from datetime import datetime, date
from google.appengine.api import users
from config import *
from google.appengine.ext.ndb.model import IntegerProperty, KeyProperty, ComputedProperty, FloatProperty
from google.appengine.datastore.datastore_query import Cursor
from utils import parseDateString, getKey

def check_types(entity_class, values, forQuery=False):
    props = classModels[entity_class]._properties
    if 'fechaCreacion' in props and not forQuery:
        values['fechaCreacion'] = datetime.today().date()
        values['empleadoCreador'] = users.get_current_user().email()
    proplistdata = None
    if 'proplistdata' in values:
        proplistdata = json.loads(values['proplistdata'])
    for key, value in props.iteritems():
        if not key in values: continue
        if values[key] == 'true': values[key] = True
        if values[key] == 'false': values[key] = False
        if not forQuery:# If the cehck is for create or update, should not include computed props
            if type(value) is ComputedProperty:
                values.pop(key, None)
        if type(value) is IntegerProperty:
            if type(values[key]) is list:
                for entry in values[key]:
                    entry = int(entry)
            else: 
                values[key] = int(values[key])
        if type(value) is FloatProperty:
            values[key] = float(values[key])
        if type(value) is ndb.BooleanProperty:#checkbox value should be 'si'o 'no'
            values[key] = True if (values[key] == 'si' or values[key])  else False
        if type(value) is KeyProperty:
            if value._repeated == True:
                items = []
                if proplistdata:
                    for item in proplistdata[key]:
                        key_obj = ndb.Key(value._kind,item.strip().replace(' ','.'))#in case it comes in label form
                        items.append(key_obj)
                    values[key]= items
                else:
                    for item in values[key]:
                        if type(item) is ndb.Key:
                            items.append(item)
                            continue
                        elif type(item) is dict: #it's an unpacked object! Create it, put it, and assign key
                            obj = create_entity(value._kind, item)['entity']
                            items.append(obj.key)
                        else:#its a key.id string
                            key_obj = ndb.Key(value._kind,item.strip().replace(' ','.'))
                            items.append(key_obj)
                    values[key] = items
            else:
                if type(values[key]) is list:#If this is a query with OR condition
                    for index,val in enumerate(values[key]):
                        if type(val) is ndb.Key: continue
                        values[key][index] = ndb.Key(value._kind,val.strip().replace(' ','.'))
                else:
                    if type(values[key]) is ndb.Key: continue
                    if values[key]:   
                        values[key] = ndb.Key(value._kind,values[key].strip().replace(' ','.'))
                    else:
                        values[key]=None
        if type(value) == ndb.DateProperty:
            if key == 'fechaCreacion':
                values[key]=date.today()
            else:
                if not isinstance(values[key],datetime):
                    if isinstance(values[key],basestring):
                        try:
                            values[key] = datetime.strptime(values[key], '%Y-%m-%d').date()
                        except:
                            values[key]=parseDateString(values[key]).date()
        if type(value) == ndb.StructuredProperty:
            listVals = values[key]
            if isinstance(values[key],basestring):
                listVals = json.loads(values[key])
            objList = []
            for listItem in listVals:
                if isinstance(listItem, ndb.Model):
                    objList.append(listItem)
                else:
                    obj = check_types(value._modelclass._class_name(),listItem)             
                    objList.append(value._modelclass(**obj))
            values[key]=objList
        if key == 'empleadoCreador':
            values[key] = users.get_current_user().email()

    if 'proplistdata' in values:
        values.pop("proplistdata")
    if not forQuery:
        keys = values.keys()
        for item in keys:
            if item not in props:
                values.pop(item)
    return values

def buildQuery(entity_class,params):
    params = check_types(entity_class, params,True) # Make sure data is of the proper type for filters
    entityClass = classModels[entity_class]
    conditions = []
    for key,value in params.iteritems():
        if key == "entityClass": continue
        if key == "sortBy": continue
        if key == "count": continue
        if key == 'cursor': continue
        condition = ''
        if 'fecha' in key:
            if 'Desde' in key:
                condition = entityClass._properties['fecha'] >= datetime.strptime(value, '%Y-%m-%d').date()
            elif 'Hasta' in key:
                condition = entityClass._properties['fecha'] <= datetime.strptime(value, '%Y-%m-%d').date()
            else:
                condition = entityClass._properties['fecha'] == value
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
    
def getEntitiesByPage(entity_class, entity_query, count, self):
    curs = Cursor(urlsafe=self.request.get('cursor'))
    entities, next_curs, more = entity_query.fetch_page(count, start_cursor=curs)
    return {'records':entities, 'cursor': next_curs.urlsafe() if next_curs else '', 'more':more}

def getEntities(entity_class, self, entity_query):
    entities = entity_query.fetch()
    return {'records':entities, 'count':len(entities)}

    
def autoIncrease(entity_class):
    if 'Numero' + entity_class in singletons:
        num = singletons['Numero' + entity_class].query().get()
        num.consecutivo = num.consecutivo + 1
        num.put()

def autoNum(entity_class):
    if 'Numero' + entity_class in singletons:
        num = singletons['Numero' + entity_class].query().get()
        if num:
            return num.consecutivo + 1
        else:
            singletons['Numero' + entity_class](consecutivo=1).put()
            return  1
    else:
        return None    

def removeComputedProps(klass,oldDicc):
    dicc = {}
    for key,propertType in klass._properties.iteritems():
        if type(propertType) is ndb.StructuredProperty:
            purged = []
            for item in oldDicc[key]:
                purged.append(removeComputedProps(propertType._modelclass,item))
            dicc[key]=purged
        else:
            if type(propertType) is not ndb.ComputedProperty:
                dicc[key] = oldDicc[key]
    return dicc

def cloneEntity(entity):
    oldDicc = entity.to_dict() 
    klass = entity.__class__
    dicc = removeComputedProps(klass,oldDicc)
    return klass(**dicc)
     

def create_entity(entity_class, values):
    values = check_types(entity_class,values) #All we get from post are strings, so we need to cast/create as appropriate
    key = getKey(entity_class, values)
    entity = classModels[entity_class].get_by_id(key)
    if entity:
        oldentity = cloneEntity(entity)
        entity.populate(**values)
        entity.put()
        return {'message':"Updated",'key':key, 'entity':entity, 'old':oldentity}
    else:
        values['id']=key
        entity = classModels[entity_class](**values)
        entity.put()
        autoIncrease(entity_class)
        return {'message':"Created",'key':key, 'entity':entity}
    
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
