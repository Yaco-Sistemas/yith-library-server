import json

import bson

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from pyramid.view import view_config, view_defaults
from pyramid.response import Response

from yithlibraryserver.utils import jsonable
from yithlibraryserver.validation import validate_password


@view_defaults(route_name='password_collection_view', renderer='json')
class PasswordCollectionRESTView(object):

    def __init__(self, request):
        self.request = request
        self.user = self.request.matchdict['user']

    @view_config(request_method='OPTIONS', renderer='string')
    def options(self):
        headers = self.request.response.headers
        headers['Access-Control-Allow-Methods'] = 'GET, POST'
        headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept'
        return ''

    @view_config(request_method='GET')
    def get(self):
        return [jsonable(p) for p in self.request.db.passwords.find()]

    @view_config(request_method='POST')
    def post(self):
        password, errors = validate_password(self.request.body,
                                             self.request.charset)

        if errors:
            result = {'message': ','.join(errors)}
            return HTTPBadRequest(body=json.dumps(result),
                                  content_type='application/json')

        # add the password to the database
        _id = self.request.db.passwords.insert(password)
        password['_id'] = str(_id)

        return password


@view_defaults(route_name='password_view', renderer='json')
class PasswordRESTView(object):

    def __init__(self, request):
        self.request = request
        self.user = self.request.matchdict['user']
        self.password_id = self.request.matchdict['password']

    @view_config(request_method='OPTIONS', renderer='string')
    def options(self):
        headers = self.request.response.headers
        headers['Access-Control-Allow-Methods'] = 'GET, PUT, DELETE'
        headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept'
        return ''

    @view_config(request_method='GET')
    def get(self):
        try:
            _id = bson.ObjectId(self.password_id)
        except bson.errors.InvalidId:
            result = {'message': 'Invalid password id'}
            return HTTPBadRequest(body=json.dumps(result),
                                  content_type='application/json')

        password = self.request.db.passwords.find_one(_id)

        if password is None:
            result = {'message': 'Password not found'}
            return HTTPNotFound(body=json.dumps(result),
                                content_type='application/json')
        else:
            return jsonable(password)

    @view_config(request_method='PUT')
    def put(self):
        return Response('put password')

    @view_config(request_method='DELETE')
    def delete(self):
        return Response('delete password')
