import json
from webob.exc import status_map 
    
def abort(status_code=None, detail="", headers=None, comment=None):
    exc = status_map[status_code](detail=detail, headers=headers, 
                                      comment=comment)
    exc.content_type = 'application/json'
    exc.body = detail
    raise exc.exception