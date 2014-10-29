import webapp2
from views.views import *

application = webapp2.WSGIApplication([
    ('/test', Test),
    ('/home', Home),
    ('/addEntity',AddEntity),
    ('/saveEntity', SaveEntity),
    ('/showEntities',ShowEntities),
    ('/entityData', EntityData),
    ('/deleteEntity', DeleteEntity),
], debug=True)