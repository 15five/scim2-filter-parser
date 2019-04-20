"""
This file contains the lexer class that is used to tokenize a given SCIM
filter query.

See https://tools.ietf.org/html/rfc7644#section-3.4.2.2 for more details.

   The operators supported in the expression are listed in Table 3.

   +----------+-------------+------------------------------------------+
   | Operator | Description | Behavior                                 |
   +----------+-------------+------------------------------------------+
   | eq       | equal       | The attribute and operator values must   |
   |          |             | be identical for a match.                |
   |          |             |                                          |
   | ne       | not equal   | The attribute and operator values are    |
   |          |             | not identical.                           |
   |          |             |                                          |
   | co       | contains    | The entire operator value must be a      |
   |          |             | substring of the attribute value for a   |
   |          |             | match.                                   |
   |          |             |                                          |
   | sw       | starts with | The entire operator value must be a      |
   |          |             | substring of the attribute value,        |
   |          |             | starting at the beginning of the         |
   |          |             | attribute value.  This criterion is      |
   |          |             | satisfied if the two strings are         |
   |          |             | identical.                               |
   |          |             |                                          |
   | ew       | ends with   | The entire operator value must be a      |
   |          |             | substring of the attribute value,        |
   |          |             | matching at the end of the attribute     |
   |          |             | value.  This criterion is satisfied if   |
   |          |             | the two strings are identical.           |
   |          |             |                                          |
   | pr       | present     | If the attribute has a non-empty or      |
   |          | (has value) | non-null value, or if it contains a      |
   |          |             | non-empty node for complex attributes,   |
   |          |             | there is a match.                        |
   |          |             |                                          |
   | gt       | greater     | If the attribute value is greater than   |
   |          | than        | the operator value, there is a match.    |
   |          |             | The actual comparison is dependent on    |
   |          |             | the attribute type.  For string          |
   |          |             | attribute types, this is a               |
   |          |             | lexicographical comparison, and for      |
   |          |             | DateTime types, it is a chronological    |
   |          |             | comparison.  For integer attributes, it  |
   |          |             | is a comparison by numeric value.        |
   |          |             | Boolean and Binary attributes SHALL      |
   |          |             | cause a failed response (HTTP status     |
   |          |             | code 400) with "scimType" of             |
   |          |             | "invalidFilter".                         |
   |          |             |                                          |
   | ge       | greater     | If the attribute value is greater than   |
   |          | than or     | or equal to the operator value, there is |
   |          | equal to    | a match.  The actual comparison is       |
   |          |             | dependent on the attribute type.  For    |
   |          |             | string attribute types, this is a        |
   |          |             | lexicographical comparison, and for      |
   |          |             | DateTime types, it is a chronological    |
   |          |             | comparison.  For integer attributes, it  |
   |          |             | is a comparison by numeric value.        |
   |          |             | Boolean and Binary attributes SHALL      |
   |          |             | cause a failed response (HTTP status     |
   |          |             | code 400) with "scimType" of             |
   |          |             | "invalidFilter".                         |
   |          |             |                                          |
   | lt       | less than   | If the attribute value is less than the  |
   |          |             | operator value, there is a match.  The   |
   |          |             | actual comparison is dependent on the    |
   |          |             | attribute type.  For string attribute    |
   |          |             | types, this is a lexicographical         |
   |          |             | comparison, and for DateTime types, it   |
   |          |             | is a chronological comparison.  For      |
   |          |             | integer attributes, it is a comparison   |
   |          |             | by numeric value.  Boolean and Binary    |
   |          |             | attributes SHALL cause a failed response |
   |          |             | (HTTP status code 400) with "scimType"   |
   |          |             | of "invalidFilter".                      |
   |          |             |                                          |
   | le       | less than   | If the attribute value is less than or   |
   |          | or equal to | equal to the operator value, there is a  |
   |          |             | match.  The actual comparison is         |
   |          |             | dependent on the attribute type.  For    |
   |          |             | string attribute types, this is a        |
   |          |             | lexicographical comparison, and for      |
   |          |             | DateTime types, it is a chronological    |
   |          |             | comparison.  For integer attributes, it  |
   |          |             | is a comparison by numeric value.        |
   |          |             | Boolean and Binary attributes SHALL      |
   |          |             | cause a failed response (HTTP status     |
   |          |             | code 400) with "scimType" of             |
   |          |             | "invalidFilter".                         |
   +----------+-------------+------------------------------------------+

                       Table 3: Attribute Operators

   +----------+-------------+------------------------------------------+
   | Operator | Description | Behavior                                 |
   +----------+-------------+------------------------------------------+
   | and      | Logical     | The filter is only a match if both       |
   |          | "and"       | expressions evaluate to true.            |
   |          |             |                                          |
   | or       | Logical     | The filter is a match if either          |
   |          | "or"        | expression evaluates to true.            |
   |          |             |                                          |
   | not      | "Not"       | The filter is a match if the expression  |
   |          | function    | evaluates to false.                      |
   +----------+-------------+------------------------------------------+

                        Table 4: Logical Operators


   +----------+-------------+------------------------------------------+
   | Operator | Description | Behavior                                 |
   +----------+-------------+------------------------------------------+
   | ( )      | Precedence  | Boolean expressions MAY be grouped using |
   |          | grouping    | parentheses to change the standard order |
   |          |             | of operations, i.e., to evaluate logical |
   |          |             | "or" operators before logical "and"      |
   |          |             | operators.                               |
   |          |             |                                          |
   | [ ]      | Complex     | Service providers MAY support complex    |
   |          | attribute   | filters where expressions MUST be        |
   |          | filter      | applied to the same value of a parent    |
   |          | grouping    | attribute specified immediately before   |
   |          |             | the left square bracket ("[").  The      |
   |          |             | expression within square brackets ("["   |
   |          |             | and "]") MUST be a valid filter          |
   |          |             | expression based upon sub-attributes of  |
   |          |             | the parent attribute.  Nested            |
   |          |             | expressions MAY be used.  See examples   |
   |          |             | below.                                   |
   +----------+-------------+------------------------------------------+

                        Table 5: Grouping Operators

"""
# flake8: noqa: F821
from sly import Lexer


class SCIMLexer(Lexer):
    tokens = {
        # Attribute Operators
        EQ, NE,
        GT, GE, LT, LE,
        CO, SW, EW, PR,

        # Logical Operators
        AND, OR, NOT,
        FALSE, TRUE,
        NULL,

        # Grouping Operators
        LPAREN, RPAREN,
        LBRACKET, RBRACKET,

        # Other
        NUMBER,
        COMP_VALUE,
        ATTRNAME,
        DOT,
        SCHEMA_URI,
    }

    # Filters MUST be evaluated using the following order of operations, in
    # order of precedence:
    # 1.  Grouping operators
    # 2.  Logical operators - where "not" takes precedence over "and",
    #     which takes precedence over "or"
    # 3.  Attribute operators

    ignore = ' \t'

    # Attribute Operators
    EQ = r'(E|e)(Q|q)'
    NE = r'(N|n)(E|e)'
    CO = r'(C|c)(O|o)'
    SW = r'(S|s)(W|w)'
    EW = r'(E|e)(W|w)'
    PR = r'(P|p)(R|r)'
    GT = r'(G|g)(T|t)'
    GE = r'(G|g)(E|e)'
    LT = r'(L|l)(T|t)'
    LE = r'(L|l)(E|e)'

    # Logical Operators
    AND = r'(A|a)(N|n)(D|d)'
    OR = r'(O|o)(R|r)'
    NOT = r'(N|n)(O|o)(T|t)'

    # Grouping Operators
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACKET = r'\['
    RBRACKET = r'\]'

    # compValue literals
    # false / null / true / number / string
    # Rules from https://tools.ietf.org/html/rfc7159
    FALSE = r'false'
    TRUE = r'true'
    NULL = r'null'
    NUMBER = r'[0-9]' # only support integers at this time

    # attrPath parts
    @_(r'[a-zA-Z]+:[a-zA-Z0-9:\._-]+:')
    def SCHEMA_URI(self, t):
        t.value = t.value.rstrip(':')
        return t

    ATTRNAME = r'[a-zA-Z][a-zA-Z0-9_-]*'

    # Other characters
    DOT = r'\.'

    @_(r'"([^"]*)"')
    def COMP_VALUE(self, t):
        t.value = t.value.strip('"')
        return t

    def error(self, t):
        raise ValueError(f"Illegal character in filter query '{t.value[0]}'")


def main(argv=None):
    '''
    Main program. Used for testing.
    '''
    import argparse
    import sys

    argv = argv or sys.argv[1:]

    parser = argparse.ArgumentParser('SCIM 2.0 Filter Parser Lexer')
    parser.add_argument('filter', help="""Eg. 'userName eq "bjensen"'""")
    args = parser.parse_args(argv)

    token_stream = SCIMLexer().tokenize(args.filter)
    for token in token_stream:
        print(token)


if __name__ == '__main__':
    main()

