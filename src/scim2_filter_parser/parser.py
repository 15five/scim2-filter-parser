'''
This file defines the parser class that is used to parse a given SCIM query.

See https://tools.ietf.org/html/rfc7644#section-3.4.2.2 for more details.

   SCIM filters MUST conform to the following ABNF [RFC5234] rules as
   specified below:

     FILTER    = attrExp / logExp / valuePath / *1"not" "(" FILTER ")"

     valuePath = attrPath "[" valFilter "]"
                 ; FILTER uses sub-attributes of a parent attrPath

     valFilter = attrExp / logExp / *1"not" "(" valFilter ")"

     attrExp   = (attrPath SP "pr") /
                 (attrPath SP compareOp SP compValue)

     logExp    = FILTER SP ("and" / "or") SP FILTER

     compValue = false / null / true / number / string
                 ; rules from JSON (RFC 7159)

     compareOp = "eq" / "ne" / "co" /
                        "sw" / "ew" /
                        "gt" / "lt" /
                        "ge" / "le"

     attrPath  = [URI ":"] ATTRNAME *1subAttr
                 ; SCIM attribute name
                 ; URI is SCIM "schema" URI

     ATTRNAME  = ALPHA *(nameChar)

     nameChar  = "-" / "_" / DIGIT / ALPHA

     subAttr   = "." ATTRNAME
                 ; a sub-attribute of a complex attribute

               Figure 1: ABNF Specification of SCIM Filters

   In the above ABNF rules, the "compValue" (comparison value) rule is
   built on JSON Data Interchange format ABNF rules as specified in
   [RFC7159], "DIGIT" and "ALPHA" are defined per Appendix B.1 of
   [RFC5234], and "URI" is defined per Appendix A of [RFC3986].

   Filters MUST be evaluated using the following order of operations, in
   order of precedence:

   1.  Grouping operators

   2.  Logical operators - where "not" takes precedence over "and",
       which takes precedence over "or"

   3.  Attribute operators

   If the specified attribute in a filter expression is a multi-valued
   attribute, the filter matches if any of the values of the specified
   attribute match the specified criterion; e.g., if a User has multiple
   "emails" values, only one has to match for the entire User to match.
   For complex attributes, a fully qualified sub-attribute MUST be
   specified using standard attribute notation (Section 3.10).  For
   example, to filter by userName, the parameter value is "userName".
   To filter by first name, the parameter value is "name.givenName".

   When applying a comparison (e.g., "eq") or presence filter (e.g.,
   "pr") to a defaulted attribute, the service provider SHALL use the
   value that was returned to the client that last created or modified
   the attribute.

   Providers MAY support additional filter operations if they choose.
   Providers MUST decline to filter results if the specified filter
   operation is not recognized and return an HTTP 400 error with a
   "scimType" error of "invalidFilter" and an appropriate human-readable
   response as per Section 3.12.  For example, if a client specified an
   unsupported operator named 'regex', the service provider should
   specify an error response description identifying the client error,
   e.g., 'The operator 'regex' is not supported.'

   When comparing attributes of type String, the case sensitivity for
   String type attributes SHALL be determined by the attribute's
   "caseExact" characteristic (see Section 2.2 of [RFC7643]).

   Clients MAY query by schema or schema extensions by using a filter
   expression including the "schemas" attribute (as shown in Figure 2).
'''
from sly import Parser

from . import ast
from . import lexer


class SCIMParser(Parser):
    #debugfile = 'debug.log'

    # Same token set as defined in the lexer
    tokens = lexer.SCIMLexer.tokens

    # Operator precedence table.
    #   Filters MUST be evaluated using the following order of operations, in
    #   order of precedence:
    #   1.  Grouping operators
    #   2.  Logical operators - where "not" takes precedence over "and",
    #       which takes precedence over "or"
    #   3.  Attribute operators
    precedence = (
        ('nonassoc', OR),
        ('nonassoc', AND),
        ('nonassoc', NOT),
    )

    # FILTER    = attrExp / logExp / valuePath / *1"not" "(" FILTER ")"
    #                                           ; 0 or 1 "not"s
    @_('attr_exp')
    def filter(self, p):
        return (p[0],)

    @_('log_exp')
    def filter(self, p):
        return (p[0],)

    @_('value_path')
    def filter(self, p):
        return (p[0],)

    @_('LPAREN filter RPAREN')
    def filter(self, p):
        return (p.filter,)

    @_('filter NOT filter')
    def filter(self, p):
        return (p.filter,)

    # valuePath = attrPath "[" valFilter "]"
    #            ; FILTER uses sub-attributes of a parent attrPath
    @_('attr_path LBRACKET value_filter RBRACKET')
    def value_path(self, p):
        pass

    # valFilter = attrExp / logExp / *1"not" "(" valFilter ")"
    #                               ; 0 or 1 "not"s
    @_('attr_exp')
    def value_filter(self, p):
        pass

    @_('log_exp')
    def value_filter(self, p):
        pass

    @_('NOT LPAREN value_filter RPAREN')
    def value_filter(self, p):
        pass

    # attrExp   = (attrPath SP "pr") /
    #             (attrPath SP compareOp SP compValue)
    @_('attr_path PR')
    def attr_exp(self, p):
        pass

    @_('attr_path EQ comp_value',
       'attr_path NE comp_value',
       'attr_path CO comp_value',
       'attr_path SW comp_value',
       'attr_path EW comp_value',
       'attr_path GT comp_value',
       'attr_path LT comp_value',
       'attr_path GE comp_value',
       'attr_path LE comp_value')
    def attr_exp(self, p):
        pass

    # logExp    = FILTER SP ("and" / "or") SP FILTER
    @_('filter OR filter',
       'filter AND filter')
    def log_exp(self, p):
        pass

    # compValue = false / null / true / number / string
    #            ; rules from JSON (RFC 7159)
    @_('FALSE',
       'NULL',
       'TRUE',
       'NUMBER',
       'COMP_VALUE')
    def comp_value(self, p):
        pass

    # attrPath  = [URI ":"] ATTRNAME *1subAttr
    #             ; SCIM attribute name
    #             ; URI is SCIM "schema" URI
    @_('ATTRNAME',
       'ATTRNAME sub_attr',
       'SCHEMA_URI ATTRNAME',
       'SCHEMA_URI ATTRNAME sub_attr')
    def attr_path(self, p):
        pass

    # subAttr   = "." ATTRNAME
    #             ; a sub-attribute of a complex attribute
    @_('DOT ATTRNAME')
    def sub_attr(self, p):
        pass


def main():
    '''
    Main program. Used for testing.
    '''
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python -m scim2_filter_parser.parser')
        raise SystemExit(1)

    token_stream = lexer.SCIMLexer().tokenize(sys.argv[1])
    ast_nodes = SCIMParser().parse(token_stream)

    # Output the resulting parse tree structure
    for depth, node in ast.flatten(ast_nodes):
        print('    ' * depth, node)


if __name__ == '__main__':
    main()

