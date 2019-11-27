import sys
import unittest
from io import StringIO

import scim2_filter_parser.queries.django as queries_django


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        queries_django.main(['userName eq "bjensen"'])
        result = self.test_stdout.getvalue()
        expected = 'Q(username__iexact="bjensen")\n'
        self.assertEqual(result, expected)
