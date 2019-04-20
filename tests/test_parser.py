from io import StringIO
import sys
from unittest import TestCase

from scim2_filter_parser import parser


class CommandLine(TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        parser.main(['userName eq "bjensen"'])
        result = self.test_stdout.getvalue().strip().split('\n')
        expected = [
           'Filter(expr=AttrExpr, negated=False, namespace=None)',
           "     AttrExpr(value='eq', attr_path=AttrPath, comp_value=CompValue)",
           "         AttrPath(attr_name='userName', sub_attr=None, uri=None)",
           "         CompValue(value='bjensen')"
        ]
        self.assertEqual(result, expected)

