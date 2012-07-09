import json

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound


def password_not_found(msg='Password not found'):
    return HTTPNotFound(body=json.dumps({'message': msg}),
                        content_type='application/json')

def invalid_password_id(msg='Invalid password id'):
    return HTTPBadRequest(body=json.dumps({'message': msg}),
                          content_type='application/json')
