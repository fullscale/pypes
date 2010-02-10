import logging
import traceback
import json
from pylons import request, response, session, tmpl_context as c
from pylons import app_globals
from pylons.controllers.util import abort, redirect_to

# added for auth
from authkit.authorize.pylons_adaptors import authorize
from authkit.permissions import RemoteUser, ValidAuthKitUser, UserIn

from pypesvds.lib.base import BaseController, render

log = logging.getLogger(__name__)

class ProjectController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('project', 'project')
    #@authorize(ValidAuthKitUser())
    def index(self, format='html'):
        """GET /project: All items in the collection"""
        # url('project')
        return render('/pypesvds.mako')

    def create(self):
        """POST /project: Create a new item"""
        # url('project')
        try:
            config = request.params.getall('config')[0]
        except:
            traceback.print_exc()
            # added because authkit seems to try posting after login
            # need toinvestigate further...
            return render('/pypesvds.mako')
        else:
            return app_globals.dfg.update(config)

    def new(self, format='html'):
        """GET /project/new: Form to create a new item"""
        # url('new_project')

    def update(self, id):
        """PUT /project/id: Update an existing item"""
        pass
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('project', id=ID),
        #           method='put')
        # url('project', id=ID)

    def delete(self, id):
        """DELETE /project/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('project', id=ID),
        #           method='delete')
        # url('project', id=ID)

    def show(self, id, format='html'):
        """GET /project/id: Show a specific item"""
        # url('project', id=ID)
        if id == 'current':
            return json.dumps(app_globals.dfg.Config)
        else:
            return ''

    def edit(self, id, format='html'):
        """GET /project/id/edit: Form to edit an existing item"""
        # url('edit_project', id=ID)

