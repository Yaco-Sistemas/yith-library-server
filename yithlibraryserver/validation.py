import json


def validate_password(rawdata, encoding, _id=None):
    errors = []

    try:
        data = json.loads(rawdata.decode(encoding))
    except TypeError:
        errors.append('Not valid JSON')
    except ValueError:
        errors.append('No JSON object could be decoded')

    # if we have errors here, we can't proceed
    if errors:
        return {}, errors

    password = {}

    # check the password id is the same as in the URL
    if _id is not None:
        if '_id' not in data:
            errors.append('The password id must be in the body')
        else:
            if data['_id'] != str(_id):
                errors.append('The password id does not match the URL')
            else:
                password['_id'] = _id

    # white list submission attributes ignoring anything else
    # first required attributes
    try:
        password['secret'] = data['secret']
    except KeyError:
        errors.append('Secret is required')

    try:
        password['service'] = data['service']
    except KeyError:
        errors.append('Service is required')

    # then optional attributes
    password['account'] = data.get('account')
    password['expiration'] = data.get('expiration')
    password['notes'] = data.get('notes')
    password['tags'] = data.get('tags')

    return password, errors
