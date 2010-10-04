import logging
import urllib
import datetime

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from pylons import app_globals

from pypesvds.lib.base import BaseController, render
from pypesvds.lib.packet import Packet

log = logging.getLogger(__name__)

class TextController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""

    def index(self, format='html'):
        """GET /text: All items in the collection"""
        pass

    def create(self):
        """POST /text: Create a new item"""
        status = 'An Undefined Error Has Occurred'
        try:
            content_encoding = request.headers.get('Content-Encoding', None)
            content_type = request.headers.get('Content-Type', None)
            content_length = request.headers.get('Content-Length', None)
            request_body = request.body
        except:
            (type, value, traceback) = sys.exc_info()[0]
            status = 'Exception (type=%s, value=%s)' % (type, value)
            log.debug('Exception in TextController:\n%s\n' % (traceback))
        else:
            # expect the body to be a payload of data not some
            # form encoded key/value pairs
            if content_type == 'application/x-www-form-urlencoded':
                status = 'You must supply a content type'
                response.content_type='application/json'
                response.status=415
                response.write('{"error":"Invalid or unspecified content-type (%s)"}'
                               % content_type)
                return

            if len(request_body) > 0:
                packet = Packet()
                packet.add('data', request_body)
                packet.set_meta('contentlength', content_length)
                packet.set_meta('mimetype', content_type)
                packet.set_meta('url', '')
                packet.set_meta('processingtime', unicode(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
                status = app_globals.dfg.send(packet)
            else:
                status = 'Error: empty request body'
                
        return status

    def new(self, format='html'):
        """GET /text/new: Form to create a new item"""
        # url('new_text')

    def update(self, id):
        """PUT /text/id: Update an existing item"""
        pass

    def delete(self, id):
        """DELETE /text/id: Delete an existing item"""
        pass

    def show(self, id, format='html'):
        """GET /text/id: Show a specific item"""
        pass

    def edit(self, id, format='html'):
        """GET /text/id/edit: Form to edit an existing item"""
        pass
