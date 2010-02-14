import logging
import mimetypes
import os
import datetime
from pylons import request, response, session, tmpl_context as c
from pylons import app_globals
from pylons.controllers.util import abort, redirect_to
from pypesvds.lib.base import BaseController, render
from pypesvds.lib.packet import Packet
import zlib

log = logging.getLogger(__name__)
mimes = os.path.join(os.path.dirname(__file__), 'mime.types')
mimetypes.init([mimes])

class DocsController(BaseController):
    """REST Controller styled on the Atom Publishing Protocol"""
    # To properly map this controller, ensure your config/routing.py
    # file has a resource setup:
    #     map.resource('doc', 'docs')

    def index(self, format='html'):
        """GET /docs: All items in the collection"""
        # url('docs')
        pass

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
                ##permanent_file = open(os.path.join(permanent_store, fname), 'w')
                ##shutil.copyfileobj(this_file.file, permanent_file)
                ##status = app_globals.dfg.send(('http://www.esr-technologies.com:5000/sink/' + fname, fname))
                doc = Packet()
                doc.add('data', filedata)
                doc.set_meta('contentlength', filelen)
                doc.set_meta('mimetype', contenttype)
                doc.set_meta('url', fname)
                doc.set_meta('processingtime', unicode(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
                status = app_globals.dfg.send(doc)
                #                               #{'data': filedata,
                #                               #'contentlength': filelen,
                #                               #'mimetype': contenttype,
                #                               #'url': fname,
                #                               #'processingtime':unicode(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))})
                #                              #'processingtime': unicode(datetime.datetime.utcnow().__str__())})
            else:
                status = 'Empty File Sent'
        return status


    def new(self, format='html'):
        """GET /docs/new: Form to create a new item"""
        # url('new_doc')
        pass

    def update(self, id):
        """PUT /docs/id: Update an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="PUT" />
        # Or using helpers:
        #    h.form(url('doc', id=ID),
        #           method='put')
        # url('doc', id=ID)

    def delete(self, id):
        """DELETE /docs/id: Delete an existing item"""
        # Forms posted to this method should contain a hidden field:
        #    <input type="hidden" name="_method" value="DELETE" />
        # Or using helpers:
        #    h.form(url('doc', id=ID),
        #           method='delete')
        # url('doc', id=ID)
        pass

    def show(self, id, format='html'):
        """GET /docs/id: Show a specific item"""
        # url('doc', id=ID)
        pass

    def edit(self, id, format='html'):
        """GET /docs/id/edit: Form to edit an existing item"""
        # url('edit_doc', id=ID)
        pass
