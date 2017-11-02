import csv
import locale
from datetime import datetime
import dateutil
from models.models import PagoRecibido, Cliente, Factura
from datastorelogic import DataStoreInterface
from google.appengine._internal.django.utils import datastructures

############### Init the instance ##############
dataStoreInterface = DataStoreInterface()

def importCSV(path):
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            pago = csv2Record(row)
            
def getClienteFromNIT(clienteString):
    nit = processClienteString(clienteString)#000000900376423  PROVEEDOR 000000900376423
    cliente = Cliente.query(Cliente.nit == processNIT(nit)).fetch()
    if not cliente:
        print 'WARNING: NO SE PUDO INDENTIFICAR EL CLIENTE: ', clienteString
        return
    return cliente[0]


def csv2Record(record):
    fecha = processDateString(record[0])# 'Marzo 18 de 2016'
    tipo = processTipoString(record[2])# Deposito en cheque local
    oficina = record[3]       
    monto =  processMontoString(record[4])#$922.896,00
    info = processInfoString(record[6])#000000900376423  PROVEEDOR 000000900376423
    values =  {'fecha':fecha, 'tipoMovimiento':tipo, 'oficina':oficina,'monto':monto, 
            'info':info}
    movimiento = dataStoreInterface.create_entity('MovimientoDeEfectivo',values)
    return movimiento

def processNIT(nitString):
    nit = nitString.lstrip('0').replace('.','').replace('-','')[:9]
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

def processTipoString(string):
    if 'Transferencia' in string: 
        return 'TRANSFERENCIA'
    if 'cheque' in string: 
        return 'CHEQUE'
    if 'Abono nomina y/o proveed' in string:
        return 'TRANSFERENCIA'
    return 'EFECTIVO'
    
def processMontoString(string):
    return string.strip().replace('$','').replace('.','').replace(',','')

def processClienteString(string):
    if string.strip() == '': return ''
    nit = string.split()[0].lstrip('0')
    return nit

def processInfoString(string):
    return string.strip()