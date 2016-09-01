import logging
from models import *
from google.appengine.ext import deferred
from google.appengine.ext import db

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.

def UpdateSchema(cursor=None, num_updated=0):
    query = models.Egreso.all()
    if cursor:
        query.with_cursor(cursor)

    to_put = []
    for egreso in query.fetch(limit=BATCH_SIZE):
        egreso.resumen = egreso.resumen.upper()
        to_put.append(egreso)

    if to_put:
        db.put(to_put)
        num_updated += len(to_put)
        logging.debug(
            'Put %d entities to Datastore for a total of %d',
            len(to_put), num_updated)
        deferred.defer(
            UpdateSchema, cursor=query.cursor(), num_updated=num_updated)
    else:
        logging.debug(
            'UpdateSchema complete with %d updates!', num_updated)