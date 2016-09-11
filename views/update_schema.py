import logging
from models.models import Egreso
from google.appengine.ext import deferred
from google.appengine.datastore.datastore_query import Cursor
from datetime import date
from google.appengine.ext import ndb

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def UpdateSchema(cursor=None, num_updated=0):
    query = Egreso.query(Egreso.fecha >= date(2014,01,01))
    if not cursor: 
        cursor = Cursor(urlsafe=cursor)
    entities,cursor,more = query.fetch_page(BATCH_SIZE, start_cursor = cursor )
    if more:
        for entity in entities:
                entity.resumen = entity.resumen.upper()
                entity.sucursal = ndb.Key('Sucursal',entity.sucursal.id().upper())
                for compra in entity.compras:
                    compra.bienoservicio = ndb.Key('Bienoservicio',compra.bienoservicio.id().upper())
                entity.put() 

        num_updated += len(entities)
        logging.debug(
                'Put %d entities to Datastore for a total of %d',
                len(entities), num_updated)
        deferred.defer(
                UpdateSchema, cursor=cursor, num_updated=num_updated)
    else:
        logging.debug(
            'UpdateSchema complete with %d updates!', num_updated)