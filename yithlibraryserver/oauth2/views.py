import bson
from deform import Form, ValidationFailure

from pyramid.httpexceptions import HTTPBadRequest, HTTPFound, HTTPNotFound
from pyramid.view import view_config

from yithlibraryserver.oauth2.application import create_client_id_and_secret
from yithlibraryserver.oauth2.schemas import ApplicationSchema

@view_config(route_name='oauth2_applications',
             renderer='templates/applications.pt')
def applications(request):
    return {
        'applications': request.db.applications.find()
        }


@view_config(route_name='oauth2_application_new',
             renderer='templates/application_new.pt')
def application_new(request):
    schema = ApplicationSchema()
    form = Form(schema, buttons=('submit', ))

    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            return {'form': e.render()}

        # the data is fine, save into the db
        application = {
            'name': appstruct['name'],
            'main_url': appstruct['main_url'],
            'callback_url': appstruct['callback_url'],
            }
        create_client_id_and_secret(application)

        request.db.applications.insert(application, safe=True)
        return HTTPFound(location=request.route_url('oauth2_applications'))

    # this is a GET
    return {'form': form.render()}


@view_config(route_name='oauth2_application_view',
             renderer='templates/application_view.pt')
def application_view(request):
    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    return {'app': app}


@view_config(route_name='oauth2_application_delete',
             renderer='templates/application_delete.pt')
def application_delete(request):
    try:
        app_id = bson.ObjectId(request.matchdict['app'])
    except bson.errors.InvalidId:
        return HTTPBadRequest(body='Invalid application id')

    app = request.db.applications.find_one(app_id)
    if app is None:
        return HTTPNotFound()

    if 'submit' in request.POST:
        request.db.applications.remove(app_id, safe=True)
        return HTTPFound(location=request.route_url('oauth2_applications'))

    return {'app': app}
