import unittest

import bson

from yithlibraryserver.utils import jsonable


class UtilsTests(unittest.TestCase):

    def test_jsonable(self):
        _id = bson.ObjectId()
        obj = {'attr1': 1, 'attr2': 2, '_id': _id}
        jobj = jsonable(obj)

        self.assertTrue(isinstance(jobj['_id'], str))
        self.assertEqual(str(_id), jobj['_id'])
