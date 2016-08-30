'''
Created on Aug 29, 2016

@author: eduze_000
'''
from easydict import EasyDict as edict
from datastorelogic import DataStoreInterface


############# Init the instance! ################# There's probably a better way!
if 'dataStoreInterface' not in globals():
    dataStoreInterface = DataStoreInterface()

##################### FORMULAS PUNTO DE EQUILIBRIO ##################################

def getUnidadesVendidas(fechaDesde, fechaHasta):
    qryParams = {'fechaDesde':fechaDesde,
                 'fechaHasta': fechaHasta}
    entities = dataStoreInterface.buildQuery('Factura', qryParams).fetch()
    
def getPrecioKilo(fruta,porcion,cliente):
    qryParams = {'producto':fruta,
                 'porcion': porcion,
                 'cliente': cliente}
    precio = dataStoreInterface.buildQuery('Precio', qryParams).fecth()
    return precio[0]



