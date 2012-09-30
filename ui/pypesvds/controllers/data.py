import logging
import traceback
import urllib
import datetime
import mimetypes
import os
import sys
import zlib
import gzip
import StringIO
import json

from pylons import request, response, session, tmpl_context as c
from pylons import app_globals

from pypesvds.lib.base import BaseController, render
from pypesvds.lib.packet import Packet
from pypesvds.lib.utils import abort

log = logging.getLogger(__name__)
mimes = os.path.join(os.path.dirname(__file__), 'mime.types')
mimetypes.init([mimes])

class DataController(BaseController):

    def _decompress(self, encoding, data):
        """ decompress data if it is gzipped """
        filedata = data
        if encoding == 'gzip':
            log.debug('Found gzipped data, decompressing')
            # gzip files have a header preceding the zlib stream.
            # try with zlib (streams compressed on the fly) and if
            # that fails, try the gzip module
            try:
                filedata = zlib.decompress(data)
            except:
                gz_data = StringIO.StringIO(data)
                filedata = gzip.GzipFile(fileobj=gz_data).read()

        return filedata

    def create(self, route=None, id=None):
        status = {}
        
        try:
            content_encoding = request.headers.get('Content-Encoding', None)
            content_type = request.headers.get('Content-Type', None)
            content_length = request.headers.get('Content-Length', None)
            log.debug('content_encoding: %s' % content_encoding)
            log.debug('content_type: %s' % content_type)
            log.debug('content_length: %s' % content_length)
            
        except Exception as e:
            log.error('Controller Exception: %s' % self.__class__.__name__)
            log.error('Reason: %s' % str(e))                    
            log.debug(traceback.print_exc())
            abort(500, str(e))
            
        else:
            # bad content-type
            if content_type == 'application/x-www-form-urlencoded':
                abort(415, "Invalid or Unspecified Content-Type")
            
            try:
                packet = Packet()
            
                # indicates a file upload
                if content_type.startswith('multipart/form-data;'):
                    log.debug('found multipart form data, attempting to find source filename')
                    part = request.POST['document']
                    if part.filename:
                        fname = unicode(part.filename.lstrip(os.sep))
                        packet.set_meta('filename', fname)

                        # update content type based on filename
                        content_type = unicode(mimetypes.guess_type(fname)[0])
              
                    data = part.value
                else:
                    data = request.body

                
                # decompress if compressed 
                filedata = self._decompress(content_encoding, data)
 
                # update content length since we might be decompressed now
                content_length = len(filedata)
                if content_length > 0:        
                    packet.add('data', filedata)
                else:
                    abort(400, 'Empty Request')
            
                # set optional user provided id
                if id is not None:
                    log.debug('id: %s' % id)
                    packet.set_meta('id', id)
                    
                # set optional user provided routing info
                if route is not None:
                    log.debug('route: %s' % route)
                    packet.set_meta('route', route)
            
                # set some common meta attributes on the packet
                packet.set_meta('requestmethod', request.method)
                packet.set_meta('contentlength', content_length)
                packet.set_meta('mimetype', content_type)
                packet.set_meta('processingtime', unicode(
                                datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
                
                status = app_globals.dfg.send(packet)
                
                # calls into pypes core are asynchronous so we respond as such
                if status['status'] == 'success':
                    response.status = 202
                
            except Exception as e:
                log.error('Controller Exception: %s' % self.__class__.__name__)
                log.error('Reason: %s' % str(e))                    
                log.debug(traceback.print_exc())
                abort(500, str(e))
          
        # return empty body on success otherwise return status object    
        return None if status['status'] == 'success' else json.dumps(status) 

    def delete(self, route, id):
        status = {}
        try:
            packet = Packet()
                
            # set packet meta attributes
            packet.set_meta('id', id)
            packet.set_meta('requestmethod', request.method)
            packet.set_meta('processingtime', unicode(
                datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
            
            status = app_globals.dfg.send(packet)
            
            # calls into pypes core are asynchronous so we respond as such
            if status['status'] == 'success':
                response.status = 202
            
        except Exception as e:
            status = 'An Undefined Error Has Occurred'
            log.error('Controller Exception: %s' % self.__class__.__name__)
            log.error('Reason: %s' % str(e))                    
            log.debug(traceback.print_exc())
            abort(500, str(e))
            
        # return empty body on success otherwise return status object      
        return None if status['status'] == 'success' else json.dumps(status) 
    
    def get(self, route=None, id=None):
        status = {}
        try:
            packet = Packet()
                
            # set packet meta attributes
            if id is not None:
                packet.set_meta('id', id)
                
            # set optional user provided routing info
            if route is not None:
                packet.set_meta('route', route)
            
            packet.set_meta('requestmethod', request.method)
            packet.set_meta('processingtime', unicode(
                datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')))
            
            status = app_globals.dfg.send(packet)
            
            # calls into pypes core are asynchronous so we respond as such
            if status['status'] == 'success':
                response.status = 202
            
        except Exception as e:
            status = 'An Undefined Error Has Occurred'
            log.error('Controller Exception: %s' % self.__class__.__name__)
            log.error('Reason: %s' % str(e))                    
            log.debug(traceback.print_exc())
            response.content_type = 'application/json'
            response.status = 500
            status['error'] = str(e)
            abort(500, str(e))
                
        # return empty body on success otherwise return status object      
        return None if status['status'] == 'success' else json.dumps(status)    

