import logging
from models.models import *
from google.appengine.ext import deferred
from google.appengine.datastore.datastore_query import Cursor
from datetime import date
from google.appengine.ext import ndb

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def UpdateSchema(cursor=None, num_updated=0):
    query = Cliente.query()
    if not cursor: 
        cursor = Cursor(urlsafe=cursor)
    entities,cursor,more = query.fetch_page(BATCH_SIZE, start_cursor = cursor )
    for entity in entities:
        entity.ciudad = ndb.Key('Ciudad',entity.ciudad.id().upper())
        entity.sucursal = ndb.Key('Sucursal',entity.sucursal.id().upper())
        entity.email = 'eduzea@gmail.com'
        entity.put()
    num_updated += len(entities)
    logging.debug('Put %d entities to Datastore for a total of %d',len(entities), num_updated)
    if more:
        deferred.defer(UpdateSchema, cursor=cursor, num_updated=num_updated)
    else:
        logging.debug('UpdateSchema complete with %d updates!', num_updated)