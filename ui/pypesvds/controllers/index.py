import logging

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

# added for auth
from authkit.authorize.pylons_adaptors import authorize
from authkit.permissions import RemoteUser, ValidAuthKitUser, UserIn

from pypesvds.lib.base import BaseController, render

log = logging.getLogger(__name__)

class IndexController(BaseController):
    @authorize(ValidAuthKitUser())
    def index(self):
        # Return a rendered template
        #return render('/index.mako')
        # or, return a response
        return render('/pypesvds.mako')

    def signout(self):
        return render('/signin.html')
