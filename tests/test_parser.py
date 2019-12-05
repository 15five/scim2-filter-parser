from io import StringIO
import sys
from unittest import TestCase

from scim2_filter_parser import lexer
from scim2_filter_parser import parser


class RegressionTestQueries(TestCase):
    maxDiff = None

    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        parser.main(['members[value eq "6784"] eq ""'])
        result = self.test_stdout.getvalue().strip().split('\n')
        expected = [
            "Filter(expr=AttrExpr, negated=False, namespace=None)",
            "     AttrExpr(value='eq', attr_path=AttrPath, comp_value=CompValue)",
            "         AttrPath(attr_name=Filter, sub_attr=None, uri=None)",
            "             Filter(expr=Filter, negated=False, namespace=AttrPath)",
            "                 Filter(expr=AttrExpr, negated=False, namespace=None)",
            "                     AttrExpr(value='eq', attr_path=AttrPath, comp_value=CompValue)",
            "                         AttrPath(attr_name='value', sub_attr=None, uri=None)",
            "                         CompValue(value='6784')",
            "                 AttrPath(attr_name='members', sub_attr=None, uri=None)",
            "         CompValue(value='')",
        ]
        self.assertEqual(result, expected)


class BuggyQueries(TestCase):
    def setUp(self):
        self.lexer = lexer.SCIMLexer()
        self.parser = parser.SCIMParser()

    def test_no_quotes_around_comp_value(self):
        query = 'userName eq example@example.com'

        token_stream = self.lexer.tokenize(query)

        with self.assertRaises(parser.SCIMParesrError):
            self.parser.parse(token_stream)


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
