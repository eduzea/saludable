from google.appengine.ext import ndb

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)

class Greeting(ndb.Model):
    """Models an individual Guestbook entry."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

############################################################################

DEFAULT_CLIENTBOOK_NAME = 'default_clientbook'

def clientbook_key(clientbook_name=DEFAULT_CLIENTBOOK_NAME):
    """Constructs a Datastore key for a Clientbook entity with clientbook_name."""
    return ndb.Key('Guestbook', clientbook_name)

class Client(ndb.Model):
    """Models an individual Client."""
    name = ndb.StringProperty(indexed=True)
    address = ndb.StringProperty(indexed=True)
    phone = ndb.IntegerProperty
    city = ndb.StringProperty(indexed=True)
    NIT = ndb.IntegerProperty
    days2pay = ndb.IntegerProperty
    
