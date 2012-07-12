import bson


def jsonable(mongo_object):
    """Makes a mongodb object jsonable.

    This function modifies the argument in place.
    """
    new_obj = {}
    for key, value in mongo_object.items():
        if isinstance(value, bson.ObjectId):
            # bson.ObjectId is not JSON serializable
            new_obj[key] = str(value)
        else:
            new_obj[key] = value
    return new_obj

