from google.appengine.ext import ndb

class Client(ndb.Model):
    """Models an individual Client."""
    nombre = ndb.StringProperty(indexed=True)
    negocio = ndb.StringProperty(indexed=True)
    nit = ndb.StringProperty(indexed=True)
    direccion = ndb.StringProperty(indexed=True)
    telefono = ndb.StringProperty(indexed=True)
    ciudad = ndb.StringProperty(indexed=True)
    diasPago = ndb.IntegerProperty()
    
class Fruta(ndb.Model):
    nombre = ndb.StringProperty(indexed=True)

class Porcion(ndb.Model):
    valor = ndb.IntegerProperty()
    unidades = ndb.StringProperty(indexed=True)
    

class Precios(ndb.Model):
    fruta = ndb.KeyProperty(kind=Fruta)
    porcion = ndb.KeyProperty(kind=Porcion)
    cliente = ndb.KeyProperty(kind=Client)