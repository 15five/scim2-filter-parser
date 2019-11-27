"""
The logic in this module builds a full SQL query based on a SCIM filter.
"""
from ..lexer import SCIMLexer
from ..parser import SCIMParser
from ..transpilers.django import Transpiler


class DjangoQuery:

    def __init__(self, filter_: str, attr_map: dict):
        self.filter = filter_
        self.attr_map = attr_map
        self.params_dict: dict = {}
        self.q = None
        self.token_stream = None
        self.ast = None
        self.transpiler = None

        self.build()

    def build(self):
        self.token_stream = SCIMLexer().tokenize(self.filter)
        self.ast = SCIMParser().parse(self.token_stream)
        self.transpiler = Transpiler(self.attr_map)
        self.q, self.params_dict = self.transpiler.transpile(self.ast)

    def __str__(self) -> str:
        return self.q.format(**self.params_dict)


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

    q = DjangoQuery(args.filter, attr_map)

    print(q)


if __name__ == '__main__':
    main()
