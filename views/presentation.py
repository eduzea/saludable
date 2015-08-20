'''
Created on Aug 11, 2015

@author: eduze_000
'''
from utils import fieldsInfo, getKey
from google.appengine.ext import ndb
from google.appengine.api import users
import jinja2
from jinja2._markupsafe import Markup
from config import *
from datastorelogic import *

basisTagString = {'StringProperty':'<input data-dojo-type="dijit/form/ValidationTextBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'IntegerProperty': '<input data-dojo-type="dijit/form/NumberTextBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'FloatProperty':'<input data-dojo-type="dijit/form/NumberTextBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'KeyProperty' : '<select data-dojo-type="dijit/form/Select" ATTR_REPLACE > INNER_REPLACE </select> POST_REPLACE',
                  'DateProperty':'<input value = now data-dojo-type="dijit/form/DateTextBox" constraints="{datePattern:\'yyyy-MM-dd\', strict:true}" ATTR_REPLACE ></input>',
                  'TextProperty':'<textarea data-dojo-type="dijit/form/SimpleTextarea" ATTR_REPLACE > INNER_REPLACE </textarea>',
                  'BooleanProperty':'<input type="text" data-dojo-type="dijit/form/CheckBox" ATTR_REPLACE > INNER_REPLACE </input>',
                  'ComputedProperty':'<input readonly ATTR_REPLACE>INNER_REPLACE</input>',
                  'StructuredProperty':'<div class = "addEntityForm" data-dojo-type="dijit/form/Form" style="border:1px solid #b5bcc7;" ATTR_REPLACE><table><tr>INNER_REPLACE</tr></table></div></br>POST_REPLACE'
                  }

def getIdString(field,entity_class):
    idname = field + '_' + entity_class
    return 'id="' + idname + '" name="' + idname + '" '

def getOptions(prop):
    options = classModels[prop._kind].query().fetch()
    html = ''
    for option in options:
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

def getTagHTML(prop,entity_class):
    propType = prop.pop('type')
    if 'default' in prop:
        prop['value'] = str(prop.pop('default'))
    if 'auto' in prop:
        prop['value'] = str(autoNum(entity_class))
        propType = ndb.IntegerProperty() 
    html = basisTagString[str(propType).partition('(')[0]]
    attrReplace = ''
    innerReplace = ''
    postReplace = ''
    for key,value in prop.iteritems():
        if key == 'id':
            attrReplace += getIdString(value, entity_class)
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

#This function creates HTLM markup based on Model props and config
def tagForField(entity_class, prop=None, auto=None):
    if not prop:
        prop = fieldsInfo(entity_class)
    tag = getTagHTML(prop, entity_class)
    return Markup(tag)

# def tagForField(entity_class, prop=None, auto=None):
#     tag = ''
#     if not prop:
#         prop = fieldsInfo(entity_class)
#     if auto and prop['id'] in auto:
#         readonly = '' if 'editable' in prop else 'readonly' 
#         tag = '<input type="text" id="' + prop['id'] +  '_' + entity_class +'" name="'+ prop['id'] + '_' +entity_class 
#         tag +='" required="' + prop['required'] 
#         tag += '" data-dojo-type="' + prop['valid'] +'" style="width: ' + prop['width'] + ';"' + ' value="' + str(auto[prop['id']]) + '"' + readonly
#         tag += '/>'
#     elif type(prop['type']) == ndb.KeyProperty:
#         tag = "<select name='" + prop['id'] + '_' + entity_class + "' id='" + prop['id'] + '_' + entity_class + "' data-dojo-type='dijit/form/Select'>"
#         options = classModels[prop['type']._kind].query().fetch()
#         for option in options:
#             dicc = option.to_dict()
#             option_value = getKey(prop['type']._kind, dicc)
#             tag += "<option value='" + option_value + "'>" + option.rotulo + '</option>'
#         tag += "</select>"
#         if prop['type']._repeated == True:
#             tag += '<button class = "listprop" id="listpropBtnAgregar' + '_' + entity_class + '_' + prop['id'] + '" data-dojo-type="dijit/form/Button">Agregar</button>'
#             tag += '<button class = "listprop" id="listpropBtnQuitar' + '_' + entity_class + '_' + prop['id'] + '" data-dojo-type="dijit/form/Button">Quitar</button>'
#             tag += '<br/><textarea readOnly="True" class = "listpropTextarea" id="text' + prop['id'] + '_' + entity_class + '" data-dojo-type="dijit/form/SimpleTextarea" rows="3" cols="30" style="width:auto;"></textarea>'
#     elif type(prop['type']) == ndb.DateProperty:
#         tag = '<input type="text" name="' + prop['id'] + '_' + entity_class + '" id="' + prop['id'] + '_' + entity_class + '" value="now" data-dojo-type="dijit/form/DateTextBox" constraints="{datePattern:\'yyyy-MM-dd\', strict:true}" required="true"/>'
#     elif type(prop['type']) == ndb.TextProperty:
#         tag = '<textarea id="' + prop['id'] +  '_' + entity_class +'" name="'+ prop['id'] + '_' + entity_class 
#         tag +='" required="' + prop['required'] 
#         tag += '" data-dojo-type="' + prop['valid'] +'" rows="3" cols="30" style="width:auto;"/></textarea>'
#     elif type(prop['type']) == ndb.BooleanProperty:
#         tag = '<input id="' + prop['id'] +  '_' + entity_class +'" name="'+ prop['id'] + '_' + entity_class +'" data-dojo-type="dijit.form.CheckBox" value="si"'
#         tag += 'onChange="this.checked ? document.getElementById(\''+ prop['id'] +  '_' + entity_class +'hidden\').disabled = true : document.getElementById(\''+ prop['id'] +  '_' + entity_class +'hidden\').disabled = false "/>'
#         tag += '<input id="' + prop['id'] +  '_' + entity_class +'hidden" name="'+ prop['id'] + '_' + entity_class +'hidden" type="hidden" value="no" data-dojo-type="dijit.form.TextBox"/>'
#     else:
#         value = str(prop['default']) if 'default' in prop else ''
#         tag = '<input type="text" id="' + prop['id'] +  '_' + entity_class +'" name="'+ prop['id'] + '_' + entity_class 
#         tag +='" required="' + prop['required'] 
#         dojoprops = ' data-dojo-props="' + prop['dojoprops'] + '"' if 'dojoprops' in prop else ''
#         tag += '" data-dojo-type="' + prop['valid'] + '" style="width: ' + prop['width'] + ';"' + ' value="' + value + '"' + dojoprops
#         tag += 'disabled' if 'disabled' in prop else ''
#         tag += '/>'
#     return Markup(tag)


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

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

JINJA_ENVIRONMENT.globals['tagForField']=tagForField
JINJA_ENVIRONMENT.globals['adjustText']=adjustText
JINJA_ENVIRONMENT.globals['isAdminUser']=isAdminUser
JINJA_ENVIRONMENT.globals['autoNum']=autoNum        