#!/usr/bin/python2
# -*- coding: utf-8 -*-

import locations3
import unittest
import json

class LocationsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = locations3.app.test_client()

    def test_finland(self):
        rv = self.app.get('/address/91.229.137.36')
        result = json.loads(rv.data)
        self.assertEqual(result['country_code'], 'FI')
        self.assertEqual(result['continent'], 'EU')


if __name__ == '__main__':
    locations3.db.upgrade_db()
    unittest.main()
