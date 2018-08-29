# -*- coding: utf-8 -*- 
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from google.appengine.ext import ndb
from google.appengine.api import users
import jinja2
from jinja2._markupsafe import Markup

from myapp.utilities.utils import fieldsInfo, fieldInfo
from myapp.model.models import classModels, Remision, msgprop
from myapp.initSaludable import dataStoreInterface

################## FUNCTIONS TO BE EXPOSED TO JINJA VIA pythonFunction() #####################
def tagForField(entityClass, field):
    tag = getTagHTML(field, entityClass)
    return Markup(tag)


def selectForField(entityClass, field, tagId):
    entity = classModels[entityClass]
    entities = entity.query(entity._properties['activo'] != False).fetch()
    options = set([getattr(entity, field) for entity in entities])
    optionsObjs = [{'value':option,'rotulo':option} for option in options]
    optionsObjs.sort()
    html = getSelectTagHTML(tagId, optionsObjs)
    return Markup(html)

def selectForEntityClass(entityClass, tagId):
    options = getOptions(entityClass)
    optionObj =  [{'value':option.key.id(),'rotulo':option.rotulo} for option in options]
    html = getSelectTagHTML(tagId, optionObj)
    return Markup(html)

def getClientesConRemision(tagId):
    remisiones = Remision.query(projection = [Remision.cliente], distinct = True).fetch()
    clientes = set([remision.cliente.get().nombre.strip() for remision in remisiones])
    clientes = [{'value':cliente, 'rotulo':cliente} for cliente in clientes]
    clientes.sort(key = lambda cliente: cliente['rotulo'])
    html = getSelectTagHTML(tagId, clientes)
    return Markup(html)

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

def isAdminUser():
    user = users.get_current_user()
    if user:
        if 'salud-able.com' in user.email():
            return True
        else:
            return False 
    else:
        return False

functionMap = {'tagForField':tagForField,
               'getClientesConRemision':getClientesConRemision,
               'adjustText':adjustText,
               'isAdminUser':isAdminUser
               }


basisTagString = {'StringProperty':'<input data-dojo-type="dijit/form/ValidationTextBox" data-dojo-props="trim:true, uppercase:true" ATTR_REPLACE > INNER_REPLACE </input>',
                  'IntegerProperty': '<input data-dojo-type="dijit/form/NumberTextBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'FloatProperty':'<input data-dojo-type="dijit/form/NumberTextBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'KeyProperty' : '<select data-dojo-type="dijit/form/Select" ATTR_REPLACE > INNER_REPLACE </select> POST_REPLACE',
                  'EnumProperty' : '<select data-dojo-type="dijit/form/Select" ATTR_REPLACE > INNER_REPLACE </select> POST_REPLACE',
                  'DateProperty':'<input value = now data-dojo-type="dijit/form/DateTextBox" constraints="{datePattern:\'yyyy-MM-dd\', strict:true}" ATTR_REPLACE ></input>',
                  'TextProperty':'<textarea data-dojo-type="dijit/form/SimpleTextarea" ATTR_REPLACE > INNER_REPLACE </textarea>',
                  'BooleanProperty':'<input type="text" data-dojo-type="dijit/form/CheckBox" onchange="this.value = this.checked;" ATTR_REPLACE > INNER_REPLACE </input>',
                  'ComputedProperty':'<input readonly ATTR_REPLACE>INNER_REPLACE</input>',
                  'StructuredProperty':'<div class = "addEntityForm" data-dojo-type="dijit/form/Form" style="border:1px solid #b5bcc7;" ATTR_REPLACE><table><tr>INNER_REPLACE</tr></table></div></br>POST_REPLACE'
                  }

def getSelectTagHTML(tagId, options):
    html = '<select data-dojo-type="dijit/form/Select" ATTR_REPLACE > INNER_REPLACE </select>'
    innerReplace = ''
    for option in options:
        innerReplace += "<option value='" + option['value'] + "'>" + option['value'] + '</option>'
    return html.replace('ATTR_REPLACE', ' id="' + tagId + '" name= "' + tagId + '"').replace('INNER_REPLACE',innerReplace)

def getIdString(field,entityClass):
    idname = field + '_' + entityClass
    return 'id="' + idname + '" name="' + idname + '" '

def getOptions(entityClass, sortField=None):
    if sortField is None:
        options = classModels[entityClass].query(classModels[entityClass].activo ==True).fetch()
    else:
        options = classModels[entityClass].query(classModels[entityClass].activo ==True).order(classModels[entityClass]._properties[sortField]).fetch()
    return options

def getOptionsHTML(entityClass, sortField=None):
    if entityClass not in classModels:
        entityClass = entityClass._kind
    options = getOptions(entityClass, sortField)
    html = ''
    for option in options:
        if not option.activo: continue
        dicc = option.to_dict()
        option_value = dataStoreInterface.getKey(entityClass, dicc)
        html += "<option value='" + option_value + "'>" + option.rotulo + '</option>'
    return html

def getEnumOptionsHTML(propType):
    options = propType._enum_type.to_dict().keys()
    html = ''
    for option in options:    
        html += "<option value='" + option + "'>" + option+ '</option>'
    return html

def repeatedPropHTML(field, entityClass):
    html = "<button class = listBtn id='" + field + '_' + entityClass + "_Btn_list' data-dojo-type='dijit/form/Button'>Agregar</button>"
    html += "<div style='border:1px solid #b5bcc7;' id='" + field + '_' + entityClass + "_list' class='list'></div>"
    return html

def structuredPropHTML(propType, fieldName, entityClass):
    model = propType._modelclass._class_name()
    fields = fieldsInfo(model)
    inner=''
    for field in fields:
        inner += '<td>' + getTagHTML(field,model) + '</td>'
    inner += "<td><button id='struc_" + fieldName + "_" + entityClass + "_Btn' data-dojo-type='dijit/form/Button'>Agregar</button></td>"
    post = '<div class= "struct-grid grid_' + entityClass + '" model ="' + model + '" id="grid_' + fieldName + '_' + entityClass +  '"/>'
    return {'inner':inner, 'post':post}

#This function creates HTLM markup based on Model props and config
def getTagHTML(prop,entityClass, customId=None):
    attrReplace = ''
    innerReplace = ''
    postReplace = ''
    propType = prop['type']
    if 'default' in prop:
        prop['value'] = str(prop.pop('default'))
    if 'auto' in prop:
        prop['value'] = str(dataStoreInterface.autoNum(entityClass))
        propType = ndb.IntegerProperty()
        attrReplace = ' readonly ' 
    if propType._repeated and type(propType) is ndb.IntegerProperty:#for the case of delimiter separated lists of numbers
        propType = ndb.StringProperty()
    html = basisTagString[str(propType).partition('(')[0]]
    for key,value in prop.iteritems():
        if key == 'type' : continue
        if key == 'id':
            if not customId:
                attrReplace += getIdString(value, entityClass)
            else:
                attrReplace += 'id="' + customId + '" name="' + customId + '" '
        else:
            attrReplace += key + '="' + value + '" '
    if 'key' == 'lowerCase':
        attrReplace += 'data-dojo-props="trim:true, lowercase:true"'
    if type(propType) == ndb.KeyProperty:
        sortField = None
        if 'sort' in prop:
            sortField = prop['sort']
        if 'noPreload' in prop:
            innerReplace += "<option value=''></option>"
        else:
            innerReplace += getOptionsHTML(propType, sortField)
        if propType._repeated == True:
            postReplace += repeatedPropHTML(prop['id'],entityClass)
    if type(propType) == msgprop.EnumProperty:
        innerReplace += getEnumOptionsHTML(propType)
    elif type(propType) == ndb.StructuredProperty:
        structPropHTML = structuredPropHTML(propType,prop['id'],entityClass)
        attrReplace = attrReplace.replace('id="', 'id="struct') # This is to avoid the structured prop form being interpreted as a field
        innerReplace += structPropHTML['inner']
        postReplace += structPropHTML['post'] 
    html = html.replace('ATTR_REPLACE',attrReplace).replace('INNER_REPLACE',innerReplace).replace('POST_REPLACE',postReplace)
    return html

##### Set up templating system ######

# Configure JINJA template engine
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('myapp/view/templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Function to expose arbitrary python functions in the templates
def pythonFunction(functionName,args):
    return functionMap[functionName](**args)

JINJA_ENVIRONMENT.globals['pythonFunction']=pythonFunction #generic function dispatcher

# Put here functions to be exposed in the templates
functionMap = {'tagForField' : tagForField,
               'selectForField' : selectForField,
               'selectForEntityClass' : selectForEntityClass,
               'adjustText' : adjustText,
               'isAdminUser' : isAdminUser,
               'autoNum' : dataStoreInterface.autoNum
               }


#### END Set up templating system #####

