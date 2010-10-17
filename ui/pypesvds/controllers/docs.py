import logging
import mimetypes
import os
import datetime
from pylons import request, response, session, tmpl_context as c
from pylons import app_globals
from pylons.controllers.util import abort
from pypesvds.lib.base import BaseController, render
from pypesvds.lib.packet import Packet
import zlib

log = logging.getLogger(__name__)
mimes = os.path.join(os.path.dirname(__file__), 'mime.types')
mimetypes.init([mimes])

class DocsController(BaseController):

    def create(self):
        """POST /docs: Create a new item"""
        # url('docs')
        status = 'An Undefined Error Has Occurred'
        permanent_store = 'pypesvds/public/sink/'
        try:
            encoding = request.headers.get('Content-Encoding', None)
            this_file = request.POST['document']
        except:
            print 'Error: missing document payload.'
        else:
            ## file upload via POST
            # mime detection
            fname = unicode(this_file.filename.lstrip(os.sep))
            contenttype = unicode(mimetypes.guess_type(fname)[0])
            if encoding == 'gzip':
                gz_filedata = this_file.value
                filedata = zlib.decompress(gz_filedata)
            else:
                filedata = this_file.value

            filelen = len(filedata)
    
            if filelen > 0:        
                doc = Packet()
                doc.add('data', filedata)
                doc.set_meta('contentlength', filelen)
                doc.set_meta('mimetype', contenttype)
                doc.set_meta('url', fname)
                doc.set_meta('processingtime', unicode(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
                status = app_globals.dfg.send(doc)

            else:
                status = 'Empty File Sent'
        return status


    def new(self, format='html'):
        """GET /docs/new: Form to create a new item"""

    def update(self, id):
        """PUT /docs/id: Update an existing item"""


    def delete(self, id):
        """DELETE /docs/id: Delete an existing item"""

    def show(self, id, format='html'):
        """GET /docs/id: Show a specific item"""

    def edit(self, id, format='html'):
        """GET /docs/id/edit: Form to edit an existing item"""

