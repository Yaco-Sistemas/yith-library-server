from pyramid.view import view_config, view_defaults
from pyramid.response import Response


@view_defaults(route_name='password_collection_view')
class PasswordCollectionRESTView(object):

    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        return Response('get password collection')

    @view_config(request_method='POST')
    def post(self):
        return Response('post password collection')


@view_defaults(route_name='password_view')
class PasswordRESTView(object):

    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        return Response('get password')

    @view_config(request_method='PUT')
    def put(self):
        return Response('put password')

    @view_config(request_method='DELETE')
    def delete(self):
        return Response('delete password')
