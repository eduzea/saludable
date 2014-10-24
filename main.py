import webapp2
from views.views import *

application = webapp2.WSGIApplication([
    ('/clients',Clients),
    ('/home',Home),
    ('/addClient',AddClient)
], debug=True)