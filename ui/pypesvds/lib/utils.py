from webob.exc import status_map 
    
def abort(status_code=None, detail="", headers=None, comment=None):
    exc = status_map[status_code](detail=detail, headers=headers, 
                                      comment=comment)
    exc.content_type = 'application/json'
    exc.body = detail
    raise exc.exception

def file_modified((file,ts)):
    mtime = os.stat(file)[8]
    return (mtime > ts, mtime)