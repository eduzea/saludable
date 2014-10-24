from google.appengine.ext import ndb

DEFAULT_CLIENTBOOK_NAME = 'default_clientbook'

def clientbook_key(clientbook_name=DEFAULT_CLIENTBOOK_NAME):
    """Constructs a Datastore key for a Clientbook entity with clientbook_name."""
    return ndb.Key('Clientbook', clientbook_name)

class Client(ndb.Model):
    """Models an individual Client."""
    nombre = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    diasPago = ndb.IntegerProperty()
    
