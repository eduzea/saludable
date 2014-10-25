import webapp2
from views.views import *

application = webapp2.WSGIApplication([
    ('/clients',Clients),
    ('/home', Home),
    ('/addClient', AddClient),
    ('/saveClient', SaveClient),
    ('/clientData', ClientData),
    ('/deleteClient', DeleteClient),
    ('/test',TestClient)
], debug=True)