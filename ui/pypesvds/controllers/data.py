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

    def create(self, route=None, id=None):
        status = {}
        
        try:
            content_encoding = request.headers.get('Content-Encoding', None)
            content_type = request.headers.get('Content-Type', None)
            content_length = request.headers.get('Content-Length', None)
            
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
                    this_file = request.POST['document']
                    fname = unicode(this_file.filename.lstrip(os.sep))
                    content_type = unicode(mimetypes.guess_type(fname)[0])
                
                    # check if file is compressed
                    if content_encoding == 'gzip':
                        gz_filedata = this_file.value
                        
                        # gzip files have a header preceding the zlib stream.
                        # try with zlib (streams compressed on the fly) and if
                        # that fails, try the gzip module
                        try:
                            filedata = zlib.decompress(gz_filedata)
                        except:
                            gz_data = StringIO.StringIO(gz_filedata)
                            filedata = gzip.GzipFile(fileobj=gz_data).read()
                    else:
                        filedata = this_file.value

                    content_length = len(filedata)
                    if content_length > 0:        
                        packet.add('data', filedata)
                        packet.set_meta('filename', fname)
                    else:
                        abort(400, 'Empty File')
                
                else:
                    # request body contains data payload
                    request_body = request.body
                    if len(request_body) > 0:
                        packet.add('data', request_body)
                    else:
                        abort(400, 'Empty Request Body')
            
                # set optional user provided id
                if id is not None:
                    packet.set_meta('id', id)
                    
                # set optional user provided routing info
                if route is not None:
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

