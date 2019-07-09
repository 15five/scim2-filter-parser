"""
The logic in this module extracts the path sent in a filter query.

RFC 7644, Figure 7: SCIM PATCH PATH Rule, ABNF:

    PATH = attrPath / valuePath [subAttr]
"""
import json

from .lexer import SCIMLexer
from .parser import SCIMParser
from .transpilers.sql import Transpiler


class AttrPaths:
    def __init__(self, filter_, attr_map):
        self.filter: str = filter_
        self.attr_map: dict = attr_map

        self.token_stream = None
        self.ast = None
        self.transpiler = None

        self.build()

    def build(self):
        self.token_stream = SCIMLexer().tokenize(self.filter)
        self.ast = SCIMParser().parse(self.token_stream)
        self.transpiler = Transpiler(self.attr_map)
        self.transpiler.transpile(self.ast)

    def __iter__(self):
        return iter(self.transpiler.attr_paths)

    def __str__(self) -> str:
        return json.dumps(self.transpiler.attr_paths, sort_keys=True, indent='    ')


def main(argv=None):
    '''
    Main program. Used for testing.
    '''
    import argparse
    import sys

    argv = argv or sys.argv[1:]

    parser = argparse.ArgumentParser('SCIM 2.0 Filter Parser Transpiler')
    parser.add_argument('filter', help="""Eg. 'userName eq "bjensen"'""")
    args = parser.parse_args(argv)

    attr_map = {
        ('name', 'familyname', None): 'name.familyname',
        ('emails', None, None): 'emails',
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
        ('userName', None, None): 'username',
        ('title', None, None): 'title',
        ('userType', None, None): 'usertype',
        ('schemas', None, None): 'schemas',
        ('userName', None, 'urn:ietf:params:scim:schemas:core:2.0:User'): 'username',
        ('meta', 'lastModified', None): 'meta.lastmodified',
        ('ims', 'type', None): 'ims.type',
        ('ims', 'value', None): 'ims.value',
    }

    q = AttrPaths(args.filter, attr_map)

    print(q)


if __name__ == '__main__':
    main()

