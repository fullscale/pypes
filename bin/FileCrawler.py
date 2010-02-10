#!/usr/bin/env python

import urllib
import urllib2
import mimetools, mimetypes
import os, stat
from os.path import join
import sys
import getopt
from cStringIO import StringIO
import zlib

class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable

# Controls how sequences are uncoded. If true, elements 
# may be given multiple values by assigning a sequence.
doseq = 1

class MultipartPostHandler(urllib2.BaseHandler):
    handler_order = urllib2.HTTPHandler.handler_order - 10 # needs to run first

    def http_request(self, request):
        data = request.get_data()
        if data is not None and type(data) != str:
            v_files = []
            v_vars = []
            try:
                 for(key, value) in data.items():
                     if type(value) == file:
                         v_files.append((key, value))
                     else:
                         v_vars.append((key, value))
            except TypeError:
                systype, value, traceback = sys.exc_info()
                raise TypeError, "not a valid non-string sequence or mapping object", traceback

            if len(v_files) == 0:
                data = urllib.urlencode(v_vars, doseq)
            else:
                boundary, data = self.multipart_encode(v_vars, v_files)

                contenttype = 'multipart/form-data; boundary=%s' % boundary
                if(request.has_header('Content-Type')
                   and request.get_header('Content-Type').find('multipart/form-data') != 0):
                    print "Replacing %s with %s" % (request.get_header('content-type'), 'multipart/form-data')
                request.add_unredirected_header('Content-Type', contenttype)

                if compress:
                    request.add_unredirected_header('Content-Encoding', 'gzip')

            request.add_data(data)
        
        return request

    def multipart_encode(vars, files, boundary = None, buf = None):
        if boundary is None:
            boundary = mimetools.choose_boundary()
        if buf is None:
            buf = StringIO()
        for(key, value) in vars:
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"' % key)
            buf.write('\r\n\r\n' + value + '\r\n')
        for(key, fd) in files:
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
            filename = fd.name.split('/')[-1:][0]
            contenttype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            buf.write('--%s\r\n' % boundary)
            buf.write('Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename))
            buf.write('Content-Type: %s\r\n' % contenttype)

            fd.seek(0)
            if compress:
                buf.write('\r\n' + zlib.compress(fd.read()) + '\r\n')
            else:
                buf.write('\r\n' + fd.read() + '\r\n')

        buf.write('--' + boundary + '--\r\n\r\n')
        buf = buf.getvalue()
        return boundary, buf
    multipart_encode = Callable(multipart_encode)

    https_request = http_request

if __name__=="__main__":
    usage = """Usage: FileCrawler [options] root_dir

Options:
    -h HOST         Set the hostname
    -p PORT         Set the port
    -u PATH         Set the path
    -e EXTENSIONS   Comma separated list of extensions to crawl
    -r              Recursively crawl
    -c              Compress data
"""

    try:
        count = 1
        opts, args = getopt.getopt(sys.argv[1:], "h:p:u:e:rcv")
    except:
        print usage
    else:
        host = 'localhost'
        port = 5000
        path = '/docs'
        extensions = []
        recursive = False
        compress = False
        verbose = False
        for option, arg in opts:
            if option == '-h':
                host = arg
            elif option == '-p':
                port = arg
            elif option == '-u':
                path = arg
            elif option == '-e':
                try:
                    extensions = ['.%s' % x.strip() for x in arg.split(',') if x]
                except:
                    assert False, 'Invalid extensions: %s' % arg
            elif option == '-r':
                recursive = True
            elif option == '-c':
                compress = True
            elif option == '-v':
                verbose = True
            else:
                assert False, 'Invalid option: %s' % o

        if len(args) != 1:
            print usage
        else:
            dir = args[0]
            url = 'http://%s:%s%s' % (host, port, path)
            
            for root, dirs, files in os.walk(dir):
                
                if recursive == False and root != dir:
                    continue
                
                for name in files:
                    if not extensions or name[name.rfind('.'):] in extensions:
                        fpath = join(root, name)
                        if verbose:
                            print '%s%s' % (('%s:' % count).ljust(15), fpath)

                        params = { "document" : open(fpath, 'rb') }
                        poster = urllib2.build_opener(MultipartPostHandler)
                        poster.open(url, params)
                        count += 1
