# This module uses the information from the model definition and the view configuration to produce the information needed
# to create de view. It should isolate the view logic from the details of the model and the details of the view configuration.
import modelsx
from myapp import config
from google.appengine.ext import ndb

# Return the UI configuration of a particular field in the entity, after appending the NDB Property object associated
# to the field
def fieldInfo(entityClass, fieldName):
    modelFields = modelsx.classModels[entityClass]._properties
    configFields = config.addConfig[entityClass]    
    fieldProp = {}
    for field in configFields:
        if field['id'] == fieldName:
            fieldProp = field 
            fieldProp['type']= modelFields[fieldName]
            return fieldProp

# Return the UI configuration of the entity class after appending to each field its associated NDB Property object
# This is a way to add type information from the model definition to the UI configuration, so the view logic has all
# the info it needs to render each field in the entity.
def fieldsInfo(entityClass):
    modelFields = modelsx.classModels[entityClass]._properties
    configFields = config.addConfig[entityClass]
    for field in configFields:
        field['type']=modelFields[field['id']]
    return configFields

# Returns columns to display in view based on the information from the model and the view config
def getColumns(entityClass):
    columns=[]
    modelFields = modelsx.classModels[entityClass]._properties
    for column in config.showConfig[entityClass]:
        colProps = { 'id':column['id'], 'field' : column['id'], 'name' : column['ui'], 'style': "text-align: center", 'width':column['style'].split(':')[1]}
        if column['id'] in modelFields and ( type(modelFields[column['id']]) == ndb.IntegerProperty or type(modelFields[column['id']]) == ndb.ComputedProperty)  :
            if not modelFields[column['id']]._repeated and 'type' not in column:
                colProps['type']='Integer'
        columns.append(colProps);
    return {'columns':columns,'key':modelsx.keyDefs[entityClass]}