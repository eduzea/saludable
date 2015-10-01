'''
Created on Aug 8, 2015

@author: eduze_000
'''
import json
from datetime import datetime, date
from google.appengine.api import users
from config import *
from google.appengine.ext.ndb.model import IntegerProperty, KeyProperty, ComputedProperty, FloatProperty,\
    BooleanProperty
from google.appengine.datastore.datastore_query import Cursor
from utils import parseDateString, getKey

#=============================================================#
# Functions to validate values for entity construction
#=============================================================#

def checkStringProperty(key, value):
    if isinstance(value,basestring):
        return value.strip()
    else:
        raise Exception("Attempted to assign non-string value to StringProperty" + key + ": " + value)    

def checkIntegerProperty(key, value):
    if isinstance(value, int): 
        return value
    else:#try to cast
        try:
            return int(value)
        except Exception:
            raise Exception("Attempted to assign non-int value to IntegerProperty " + key + ": " + value)

def checkFloatProperty(key, value):
    if isinstance(value, float): 
        return value
    else:#try to cast
        try:
            return float(value)
        except Exception:
            raise Exception("Attempted to assign non-float value to FloatProperty " + key + ": " + value)

def checkKeyProperty(key, propertyType, value):
    if isinstance(value, ndb.Key):
        return value
    elif isinstance(value, dict): #it's an unpacked object! Create it, put it, and assign key
        obj = create_entity(propertyType._kind, value)['entity']
        return obj.key
    elif isinstance(value,basestring):#its a key.id string
        key_obj = ndb.Key(propertyType._kind,value.strip().replace(' ','.'))
        return key_obj
    else:
        raise Exception("Attempted to assign non-key value to KeyProperty " + key + ": " + value)

def checkBooleanProperty(key, value):
    if isinstance(value,bool): return value
    if value == 'true': return True
    if value == 'false': return False
    raise Exception('Attempted to assing non-bool value to BooleanProperty ' + key + ': ' + value)

def checkDateProperty(key,value):
    if isinstance(value,datetime): return value
    if isinstance(value,basestring):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except:
            try:
                return parseDateString(value).date()
            except:
                raise Exception("Could not parse string " + value + 'into proper date')

def checkStructuredProperty(key, propertyType, value):
    if isinstance(value,basestring):
        value = json.loads(value)
    if isinstance(value, ndb.Model): return value 
    return checkEntityCreate(propertyType._modelclass._class_name(),value)             

#======================================
# Entity Init functions
#======================================
def dataStoreObjectInit(props, values):
    if 'fechaCreacion' in props:
        values['fechaCreacion'] = datetime.today().date()
    if 'empleadoCreador' in props:
        values['empleadoCreador'] = users.get_current_user().email()
    return values
#=====================================
# Type checking for entity creation and queries
#=====================================

def checkFieldType(key, propertyType, value):
    if type(propertyType) is BooleanProperty:
        value = checkBooleanProperty(key,value)
    if type(propertyType) is IntegerProperty:
        value = checkIntegerProperty(key, value)
    if type(propertyType) is FloatProperty:
        value = checkFloatProperty(key, value)
    if type(propertyType) is KeyProperty:
        value = checkKeyProperty(key, propertyType, value)
    if type(propertyType) == ndb.DateProperty:
        value = checkDateProperty(key, value)
    if type(propertyType) == ndb.StructuredProperty:
        value = checkStructuredProperty(key, propertyType, value)
    if type(propertyType) == ndb.StringProperty:
        value = checkStringProperty(key,value)
    return value

def checkEntityCreate(entityClass, values, forQuery=False):
    """ Check (and adjust if need be) the values given to create a datastore entity
        Arguments:
            *entityClass*: The string with the name of the entity model that will be created
            with the values being checked.
            *values*: A dictionary with the field names and values for the entity to be created. 
        Returns: dictionary of values that are guaranteed to be type correct for entity creation.
    """
    props = classModels[entityClass]._properties
    values = dataStoreObjectInit(props, values)
    for key, value in props.iteritems():
        #property should be skipped in these cases
        if not key in values: continue
        if type(value) is ComputedProperty:
            values.pop(key, None)
            continue
        #Check if repeated property
        if value._repeated == True:
            if isinstance(values[key],basestring):
                values[key] = json.loads(values[key])
            if isinstance(values[key],list):
                ndbKeys = []
                for entry in values[key]:
                    entry = checkFieldType(key, value, entry)
                    ndbKeys.append(entry)
                values[key] = ndbKeys
            else:
                values[key] = checkFieldType(key, value, values[key])
                values[key] = [values[key]]
        else:
            values[key] = checkFieldType(key, value, values[key])
    # Remove fields not in the model        
    keys = values.keys()
    for item in keys:
        if item not in props:
            values.pop(item)

    return values


def checkQueryValues(entityClass, values):
    """ Check (and adjust if need be) the values given to query the datastore
        Arguments:
            *entityClass*: The string with the name of the entity model that will be created
            with the values being checked.
            *values*: A dictionary with the field names and values for the entity to be created. 
        Returns: dictionary of values that are guaranteed to be type correct for entity query.
    """
    props = classModels[entityClass]._properties
    for key, value in props.iteritems():
        if not key in values: continue
        if isinstance(values[key],list):#If this is a query with OR condition
            for index,val in enumerate(values[key]):
                if type(val) is ndb.Key: continue
                values[key][index] = checkFieldType(key, value, values[key][index])
        else:
            values[key] = checkFieldType(key, value, values[key])
    return values

def buildQuery(entity_class,params):
    params = checkQueryValues(entity_class, params) # Make sure data is of the proper type for filters
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
    values = checkEntityCreate(entity_class,values) #All we get from post are strings, so we need to cast/create as appropriate
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
    values = checkEntityCreate('Venta', values)
    venta = Venta(producto = values['producto'],
                  porcion = values['porcion'],
                  cantidad = values['cantidad'],
                  precio = values['precio'],
                  venta = values['venta']
                  )
    return venta    
