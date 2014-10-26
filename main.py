import webapp2
from views.views import *

application = webapp2.WSGIApplication([
    ('/home', Home),
    ('/addEntity',AddEntity),
    ('/saveEntity', SaveEntity),
    ('/clients',Clients),
    ('/clientData', ClientData),
    ('/deleteClient', DeleteClient),
    ('/test',TestClient)
], debug=True)