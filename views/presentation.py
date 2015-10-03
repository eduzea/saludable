# -*- coding: utf-8 -*- 
from utils import fieldsInfo, fieldInfo, getKey
from google.appengine.ext import ndb
from google.appengine.api import users
import jinja2
from jinja2._markupsafe import Markup
from config import *
from datastorelogic import *

############### Init the instance ##############
dataStoreInterface = DataStoreInterface()

################## FUNCTIONS TO BE EXPOSED TO JINJA VIA pythonFunction() #####################
def tagForField(entity_class, prop, auto=None, customId=None):
    if isinstance(prop,basestring):
        prop = fieldInfo(entity_class, prop)
    tag = getTagHTML(prop, entity_class, customId)
    return Markup(tag)

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

def pythonFunction(functionName,args):
    return functionMap[functionName](**args)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

JINJA_ENVIRONMENT.globals['pythonFunction']=pythonFunction #generic function dispatcher
JINJA_ENVIRONMENT.globals['tagForField']=tagForField
JINJA_ENVIRONMENT.globals['adjustText']=adjustText
JINJA_ENVIRONMENT.globals['isAdminUser']=isAdminUser
JINJA_ENVIRONMENT.globals['autoNum']= dataStoreInterface.autoNum        

basisTagString = {'StringProperty':'<input data-dojo-type="dijit/form/ValidationTextBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'IntegerProperty': '<input data-dojo-type="dijit/form/NumberTextBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'FloatProperty':'<input data-dojo-type="dijit/form/NumberTextBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'KeyProperty' : '<select data-dojo-type="dijit/form/Select" ATTR_REPLACE > INNER_REPLACE </select> POST_REPLACE',
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
        innerReplace += "<option value='" + option['value'] + "'>" + option['rotulo'] + '</option>'
    return html.replace('ATTR_REPLACE', ' id="' + tagId + '" ').replace('INNER_REPLACE',innerReplace)

def getIdString(field,entity_class):
    idname = field + '_' + entity_class
    return 'id="' + idname + '" name="' + idname + '" '

def getOptions(prop):
    options = classModels[prop._kind].query().fetch()
    html = ''
    for option in options:
        if not option.activo: continue
        dicc = option.to_dict()
        option_value = getKey(prop._kind, dicc)
        html += "<option value='" + option_value + "'>" + option.rotulo + '</option>'
    return html

def repeatedPropHTML(field, entity_class):
    html = "<button class = listBtn id='" + field + '_' + entity_class + "_Btn_list' data-dojo-type='dijit/form/Button'>Agregar</button>"
    html += "<div style='border:1px solid #b5bcc7;' id='" + field + '_' + entity_class + "_list' class='list'></div>"
    return html

def structuredPropHTML(propType, fieldName, entity_class):
    model = propType._modelclass._class_name()
    fields = fieldsInfo(model)
    inner=''
    for field in fields:
        inner += '<td>' + getTagHTML(field,model) + '</td>'
    inner += "<td><button id='" + fieldName + "_" + entity_class + "_Btn' data-dojo-type='dijit/form/Button'>Agregar</button></td>"
    post = '<div class= "struct-grid grid_' + entity_class + '" model ="' + model + '" id="grid_' + fieldName + '_' + entity_class +  '"/>'
    return {'inner':inner, 'post':post}

#This function creates HTLM markup based on Model props and config
def getTagHTML(prop,entity_class, customId=None):
    propType = prop.pop('type')
    if 'default' in prop:
        prop['value'] = str(prop.pop('default'))
    if 'auto' in prop:
        prop['value'] = str(dataStoreInterface.autoNum(entity_class))
        propType = ndb.IntegerProperty() 
    html = basisTagString[str(propType).partition('(')[0]]
    attrReplace = ''
    innerReplace = ''
    postReplace = ''
    for key,value in prop.iteritems():
        if key == 'id':
            if not customId:
                attrReplace += getIdString(value, entity_class)
            else:
                attrReplace += 'id="' + customId + '" name="' + customId + '" '
        else:
            attrReplace += key + '="' + value + '" '
    if type(propType) == ndb.KeyProperty:
        innerReplace += getOptions(propType)
        if propType._repeated == True:
            postReplace += repeatedPropHTML(prop['id'],entity_class)
    elif type(propType) == ndb.StructuredProperty:
        structPropHTML = structuredPropHTML(propType,prop['id'],entity_class)
        innerReplace += structPropHTML['inner']
        postReplace += structPropHTML['post'] 
    html = html.replace('ATTR_REPLACE',attrReplace).replace('INNER_REPLACE',innerReplace).replace('POST_REPLACE',postReplace)
    return html


