def jsonable(mongo_object):
    """Makes a mongodb object jsonable.

    This function modifies the argument in place.
    """
    # the _id attribute is not serializable to JSON
    mongo_object['_id'] = str(mongo_object['_id'])
    return mongo_object
