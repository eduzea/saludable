'''
Created on Aug 8, 2015

@author: eduze_000
'''
import json, re
from datetime import datetime, date
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from google.appengine.ext.ndb.model import IntegerProperty, KeyProperty, ComputedProperty, FloatProperty,BooleanProperty
from google.appengine.datastore.datastore_query import Cursor
from myapp.utilities import utils
from myapp.config import classModels, keyDefs, singletons

#=============================================================#
# Functions to validate values for proper type
#=============================================================#

def representsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def checkStringProperty(key, value):
    if isinstance(value,basestring):
        return value.strip()
    else:
        raise Exception("Attempted to assign non-string value to StringProperty: " + key + ": " + str(value))    

def checkIntegerProperty(key, value):
    if isinstance(value, int): 
        return value
    else:#try to cast
        try:
            return int(value)
        except Exception:
            raise Exception("Attempted to assign non-int value to IntegerProperty " + key + ": " + str(value))

def checkFloatProperty(key, value):
    if isinstance(value, float): 
        return value
    else:#try to cast
        try:
            return float(value)
        except Exception:
            raise Exception("Attempted to assign non-float value to FloatProperty " + key + ": " + str(value))


def checkBooleanProperty(key, value):
    if isinstance(value,bool): return value
    if value == 'true': return True
    if value == 'false': return False
    raise Exception('Attempted to assing non-bool value to BooleanProperty ' + key + ': ' + str(value))

def checkDateProperty(key,value):
    if isinstance(value,date): return value
    if isinstance(value,basestring):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except:
            try:
                return utils.parseDateString(value).date()
            except:
                raise Exception("Could not parse string " + value + 'into proper date')

class DataStoreInterface():
    
    def __init__(self, classModels, keyDefs, singletons):
        self.classModels = classModels
        self.keyDefs = keyDefs
        self.singletons = singletons
    
    _funcMap = {'pre':{'create':{},'update':{},'delete':{}},
                'post':{'create':{},'update':{},'delete':{}}
                }
    
    #======================================
    # Entity Init functions
    #======================================
    def _dataStoreObjectInit(self, props, values):
        if 'fechaCreacion' in props:
            values['fechaCreacion'] = datetime.today().date()
        if 'empleadoCreador' in props:
            if users.get_current_user():
                values['empleadoCreador'] = users.get_current_user().email()
            else:
                values['empleadoCreador'] = 'auto'
        return values

    def _checkStructuredProperty(self,key, propertyType, value):
        if isinstance(value,basestring):
            value = json.loads(value)
        if isinstance(value, ndb.Model): return value
        values = self._checkEntityCreate(propertyType._modelclass._class_name(),value)
        key = self.getKey(propertyType._modelclass._class_name(), value)
        values['id'] = key 
        return values
    
    
    def _checkComputedProperty(self, key, value):
        if isinstance(value,basestring):
            if value == 'true': return True
            if value == 'false': return False
            if representsInt(value): return int(value)
        else:
            return value

    def _checkKeyProperty(self, key, propertyType, value):
        if isinstance(value, ndb.Key):
            return value
        elif isinstance(value, ndb.Model):
            return value.key
        elif isinstance(value, dict): #it's an unpacked object! Create it, put it, and assign key
            obj = self.create_entity(propertyType._kind, value)['entity']
            return obj.key
        elif isinstance(value,basestring):#its a key.id string
            if len(keyDefs[propertyType._kind]) == 1 and type(classModels[propertyType._kind]._properties[keyDefs[propertyType._kind][0]]) == ndb.IntegerProperty:
                key_obj = ndb.Key(propertyType._kind,int(value.strip().replace(' ','.')))
            else:
                if value != '': 
                    key_obj = ndb.Key(propertyType._kind,value.strip().replace(' ','.'))
                elif propertyType._required:
                    raise Exception( "Attempted to assign empty string to required KeyProperty " + key)
                else:
                    return
            return key_obj
        elif isinstance(value, int):
                key_obj = ndb.Key(propertyType._kind,value)
                return key_obj
        else:
            raise Exception( "Attempted to assign non-key value to KeyProperty " + key + ": " + str(value) )
     
    def _checkEnumProperty(self, key, propertyType, value):
        if isinstance(value,msgprop.EnumProperty):
            return value
        elif isinstance(value,basestring):
            return propertyType._enum_type._EnumClass__by_name[value]
        else:
            raise Exception( "Attempted to assign non-ENUM value to EnumProperty " + key + ": " + str(value) )
    #=====================================
    # Type checking for entity creation and queries
    #=====================================
    
    def _checkFieldType(self,key, propertyType, value):
        if value == None: return value # let datastore handle this case...
        if type(propertyType) is BooleanProperty:
            value = checkBooleanProperty(key,value)
        if type(propertyType) is IntegerProperty:
            value = checkIntegerProperty(key, value)
        if type(propertyType) is FloatProperty:
            value = checkFloatProperty(key, value)
        if type(propertyType) is KeyProperty:
            value = self._checkKeyProperty(key, propertyType, value)
        if type(propertyType) == ndb.DateProperty:
            value = checkDateProperty(key, value)
        if type(propertyType) == ndb.StructuredProperty:
            value = self._checkStructuredProperty(key, propertyType, value)
        if type(propertyType) == ndb.StringProperty:
            value = checkStringProperty(key,value)
        if type(propertyType) == msgprop.EnumProperty:
            value = self._checkEnumProperty(key, propertyType, value)
        if type(propertyType) == ndb.ComputedProperty:
            test = self._checkComputedProperty(key, value)
        return value
    
    def _checkEntityCreate(self,entityClass, values, forQuery=False):
        """ Check (and adjust if need be) the values given to create a datastore entity
            Arguments:
                *entityClass*: The string with the name of the entity model that will be created
                with the values being checked.
                *values*: A dictionary with the field names and values for the entity to be created. 
            Returns: dictionary of values that are guaranteed to be type correct for entity creation.
        """
        props = classModels[entityClass]._properties
        values = self._dataStoreObjectInit(props, values)
        for key, value in props.iteritems():
            #property should be skipped in these cases
            if not key in values: continue
            if type(value) is ComputedProperty:
                values.pop(key, None)
                continue
            #Check if repeated property
            if value._repeated == True:
                if isinstance(values[key],basestring):
                    try:
                        values[key] = json.loads(values[key]) #if json
                    except:
                        values[key] = re.split('\W+', values[key])#values[key].split(',') #if token separated
                if isinstance(values[key],list):
                    ndbKeys = []
                    for entry in values[key]:
                        entry = self._checkFieldType(key, value, entry)
                        ndbKeys.append(entry)
                    values[key] = ndbKeys
                else:
                    values[key] = self._checkFieldType(key, value, values[key])
                    values[key] = [values[key]]
            else:
                values[key] = self._checkFieldType(key, value, values[key])
        # Remove fields not in the model        
        keys = values.keys()
        for item in keys:
            if item not in props:
                values.pop(item)
    
        return values
    
    
    def _checkQueryValues(self,entityClass, values):
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
                    values[key][index] = self._checkFieldType(key, value, values[key][index])
            else:
                values[key] = self._checkFieldType(key, value, values[key])
        return values
    
    def _removeComputedProps(self, klass, oldDicc):
        dicc = {}
        for key,propertType in klass._properties.iteritems():
            if type(propertType) is ndb.StructuredProperty:
                purged = []
                for item in oldDicc[key]:
                    purged.append(self._removeComputedProps(propertType._modelclass,item))
                dicc[key]=purged
            else:
                if type(propertType) is not ndb.ComputedProperty:
                    dicc[key] = oldDicc[key]
        return dicc
    
    def _cloneEntity(self,entity):
        oldDicc = entity.to_dict() 
        klass = entity.__class__
        dicc = self._removeComputedProps(klass,oldDicc)
        return klass(**dicc)

    def _autoIncrease(self,entityClass):
        if 'Numero' + entityClass in singletons:
            num = singletons['Numero' + entityClass].query().get()
            num.consecutivo = num.consecutivo + 1
            num.put()

        ####################### PUBLIC INTERFACE ###################
        
    def registerFollowUpLogic(self, when, action, entityClass, function):
        self._funcMap[when][action][entityClass] = function
        
    def buildQuery(self, entityClass,params):
        params = self._checkQueryValues(entityClass, params) # Make sure data is of the proper type for filters
        entityClassObj = classModels[entityClass]
        conditions = []
        for key,value in params.iteritems():
            if key == "entityClass": continue
            if key == "sortBy": continue
            if key == "count": continue
            if key == 'cursor': continue
            condition = ''
            if 'fecha' in key:
                if 'Desde' in key:
                    if isinstance(value, datetime):
                        condition = entityClassObj._properties['fecha'] >= value.date()
                    else:
                        condition = entityClassObj._properties['fecha'] >= datetime.strptime(value, '%Y-%m-%d').date()
                elif 'Hasta' in key:
                    if isinstance(value, datetime):
                        condition = entityClassObj._properties['fecha'] <= value.date()
                    else:
                        condition = entityClassObj._properties['fecha'] <= datetime.strptime(value, '%Y-%m-%d').date()
                else:
                    condition = entityClassObj._properties['fecha'] == value
            else:
                if not isinstance(value, list):
                    condition = entityClassObj._properties[key]==value
                else:
                    if len(value) == 1:
                        condition = entityClassObj._properties[key]==value[0]
                    else:
                        orConditions = []
                        for orVal in value:
                            orConditions.append(entityClassObj._properties[key] == orVal)
                        condition = ndb.OR(*orConditions)
            conditions.append(condition)
        if 'sortBy' in params.keys():#If no sortField is given it defaults to the entityClass key
            sortField = ''
            descending = False
            if params['sortBy'][0]=='-':
                descending = True
                params['sortBy'] = params['sortBy'][1:]
            if params['sortBy']:
                sortField = params['sortBy']
            else:
                sortField = keyDefs[entityClass][0]  
            
            if descending:
                return entityClassObj.query(*conditions).order(-entityClassObj._properties[sortField])
            else:
                return entityClassObj.query(*conditions).order(entityClassObj._properties[sortField])
        else:
            return  entityClassObj.query(*conditions)
        
    def getEntitiesByPage(self,cursor, entityClass, entity_query, count):
        curs = Cursor(urlsafe=cursor)
        entities, next_curs, more = entity_query.fetch_page(count, start_cursor=curs)
        return {'records':entities, 'cursor': next_curs.urlsafe() if next_curs else '', 'more':more}
    
    def getEntities(self, entityClass, entity_query):
        entities = entity_query.fetch()
        return {'records':entities, 'count':len(entities)}
        
    def autoNum(self,entityClass):
        if 'Numero' + entityClass in singletons:
            num = singletons['Numero' + entityClass].query().get()
            if num:
                return num.consecutivo + 1
            else:
                singletons['Numero' + entityClass](consecutivo=1).put()
                return  1
        else:
            return None
    
    def create_entity(self, entityClass, values, bypass_writepermission_check=False):
        if not bypass_writepermission_check:
            empleado = classModels['Empleado'].query(classModels['Empleado'].email == users.get_current_user().email()).get()
            if not empleado.writePermission:
                    return {'result':'FAIL','message':"No tiene permiso de modificar el sistema"}
        values = self._checkEntityCreate(entityClass,values) #All we get from post are strings, so we need to cast/create as appropriate
        key = self.getKey(entityClass, values)
        entity = classModels[entityClass].get_by_id(key)
        if entity:
            if entityClass in self._funcMap['pre']['update']:
                try:
                    self._funcMap['pre']['update'][entityClass](entity)
                except Exception as e:
                    print 'Pre-Update: ' + e.message
            oldentity = self._cloneEntity(entity)
            entity.populate(**values)
            entity.put()
            if entityClass in self._funcMap['post']['update']:
                try:
                    self._funcMap['post']['update'][entityClass](entity)
                except Exception as e:
                    print 'Post-Update: ', e.message
            return {'result':'SUCCESS','message':"Updated",'key':key, 'entity':entity, 'old':oldentity}
        else:
            values['id']=key
            if entityClass in self._funcMap['pre']['create']:
                try:
                    self._funcMap['pre']['create'][entityClass](entity)
                except Exception as e:
                    print 'Pre-Create', e
            entity = classModels[entityClass](**values)
            entity.put()
            if entityClass in self._funcMap['post']['create']:
                try:
                    self._funcMap['post']['create'][entityClass](entity)
                except Exception as e:
                    print 'Post-Create: ' , e
            self._autoIncrease(entityClass)
            return {'result':'SUCCESS','message':"Created",'key':key, 'entity':entity}
        
    def deleteEntity(self, entityClass, entity):
        if isinstance(entity, ndb.Model):
            pass
        elif isinstance(entity,ndb.Key):
            entity = entity.get()
        elif isinstance(entity,basestring):
            entity = classModels[entityClass].get_by_id(entity)
        
        if not isinstance(entity, ndb.Model):
            raise Exception("Can't interpret " + str(entity) + " as an entity!")
        
        if entityClass in self._funcMap['pre']['delete']:
            try:
                self._funcMap['pre']['delete'][entityClass](entity)
            except Exception as e:
                print 'Pre-Delete: ' + e.message
        entity.key.delete()
        if entityClass in self._funcMap['post']['delete']:
            try:
                self._funcMap['post']['delete'][entityClass](entity)
            except Exception as e:
                print 'Post-Delete: ' + e.message

    def getConsecutivo(self, entityClass):
        """
        Returns the next key number to use for an entityClass. It does not increase the entityClass counter, 
        which should only get increased if the new object is effectively saved to the datastore.
        """
        if 'Numero' + entityClass in singletons:
            numero = singletons['Numero' + entityClass].query().get()
            if numero:
                return numero.consecutivo + 1
            else:
                singletons['Numero' + entityClass](consecutivo=int(0)).put()
                return 0;
        else:
            raise Exception("No hay consecutivo en esta entityClass!")
        
    def getKey(self,entityClass,dicc):
        key = ''
        for keypart in keyDefs[entityClass]:
            if type(dicc[keypart]) == ndb.Key:
                entity = dicc[keypart].get()
                if entity:
                    key += ' ' + unicode(str(entity.key.id()),'utf-8') 
                else:
                    print "Entity not found by key: " , keypart  , '=' , dicc[keypart]  
            else:
                key += ' ' + unicode(dicc[keypart])
        return '.'.join(key.split())

