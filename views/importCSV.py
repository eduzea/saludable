import csv
import locale
from datetime import datetime
import dateutil
from models.models import PagoRecibido, Cliente
from datastorelogic import DataStoreInterface
from google.appengine._internal.django.utils import datastructures

############### Init the instance ##############
dataStoreInterface = DataStoreInterface()

def importCSV(path,entity):
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            pago = csv2PagoRecibido(row)
            print pago
            
def csv2PagoRecibido(record):
    numero = record[0]
    fecha = processDateString(record[1])# 'Marzo 18 de 2016'
    medio = processMedioString(record[2])# Deposito en cheque local
    oficina = record[3]       
    monto =  processMontoString(record[4])#$922.896,00
    documento = record[5].strip()#51624971
    cliente = None
    descripcion = ''
    if medio == 'TRANSFERENCIA':
        nit = processClienteString(record[6])#000000900376423  PROVEEDOR 000000900376423
        cliente = Cliente.query(Cliente.nit == processNIT(nit)).fetch()
        if not cliente:
            print 'WARNING: NO SE PUDO INDENTIFICAR EL CLIENTE: ', record[6]
            return
        cliente = cliente[0].key
        descripcion = processDescripcionString(record[6])#000000900376423  PROVEEDOR 000000900376423
    values =  {'numero':numero,'fecha':fecha, 'medio':medio, 'oficina':oficina,'monto':monto, 'documento':documento, 'cliente':cliente,
           'descripcion':descripcion}
    pago = dataStoreInterface.create_entity('PagoRecibido',values)
    return pago
    
def processNIT(nitString):
    nit = nitString.replace('.','').replace('-','')[:9]
    return nit
    
def processDateString(string):
    #date_object = dateutil.parser.parse(string) # fails, not locale aware
    #locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') # cant in GAE!
    translateMonth = {'Enero':'Jan', 'Febrero':'Feb','Marzo':'Mar','Abril':'Apr','Mayo':'May','Junio':'Jun','Julio':'Jul','Agosto':'Aug',
                      'Septiembre':'Sep','Octubre':'Oct','Noviembre':'Nov','Diciembre':'Dec'}
    mes = string.split()[0]
    month = translateMonth[mes]
    date_object = datetime.strptime(string.replace(' de','').replace(mes,month), '%b %d %Y')
    return date_object

def processMedioString(string):
    if 'Transferencia' in string: 
        return 'TRANSFERENCIA'
    if 'cheque' in string: 
        return 'CHEQUE'
    return 'EFECTIVO'
    
def processMontoString(string):
    return string.strip().replace(',00','').replace('$','').replace('.','')

def processClienteString(string):
    if string.strip() == '': return ''
    nit = string.split()[0].lstrip('0')
    return nit

def processDescripcionString(string):
    return string.strip()