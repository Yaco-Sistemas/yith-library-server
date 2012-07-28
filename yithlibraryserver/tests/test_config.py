import os
import unittest

from yithlibraryserver.config import read_setting_from_env


class ConfigTests(unittest.TestCase):

    def test_read_setting_from_env(self):
        settings = {
            'foo_bar': '1',
            }

        self.assertEqual('1', read_setting_from_env(settings, 'foo_bar'))

        self.assertEqual('default',
                         read_setting_from_env(settings, 'new_option', 'default'))
        self.assertEqual(None,
                         read_setting_from_env(settings, 'new_option'))

        os.environ['FOO_BAR'] = '2'
        self.assertEqual('2', read_setting_from_env(settings, 'foo_bar'))
