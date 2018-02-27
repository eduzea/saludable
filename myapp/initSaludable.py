## The purpose of this file is to initialize application global python objects ##

from model.datastorelogic import DataStoreInterface
from model import models
from myapp.model.models import Empleado

if 'dataStoreInterface' not in globals():
    dataStoreInterface = DataStoreInterface(models.classModels,models.keyDefs, models.singletons)
    
## END Initialize the DataStore interface with this application's object model ##


## INITILIZAE FIXED LISTS ##########
def initSaludable():
    init = models.Initialized.query().fetch()
    if len(init) == 0:
        print "initializing..."
        entity = Empleado(**{'nombre':'admin','apellido':'admin','writePermission':True,'email':'admin@salud-able.com'} )
        entity.put()

        predefined = [{'Fila':['A','B','C','D','E','F','G','H','I','Z']}, 
                      {'Columna':[1,2,3,4,5,6,7,8,9,10,11,12]}, 
                      {'Nivel':[1,2,3,4,5,6,7,8,9,10,11]}]
        
        for initObj in predefined:
            entityClass = initObj.keys()[0]
            for instance in initObj[entityClass]:
                entity = models.classModels[entityClass](**{'id':instance ,'nombre' : instance})
                entity.put()
        initObj = models.Initialized()
        initObj.put()
        
        
        
####################################
