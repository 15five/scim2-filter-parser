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

#from . import ast
from . import lexer

class SCIMParser(Parser):

    # Same token set as defined in the lexer
    tokens = lexer.SCIMLexer

    # Operator precedence table.
    #precedence = (
    #    ('left', LOR),
    #    ('left', LAND),
    #    ('nonassoc', LT, LE, GT, GE, EQ, NE),
    #    ('left', PLUS, MINUS),
    #    ('left', TIMES, DIVIDE),
    #    ('right', DEREF, GROW, UNARY),
    #)

    # FILTER    = attrExp / logExp / valuePath / *1"not" "(" FILTER ")"
    @_('attr_exp')
    def filter(self, p):
        return (p[0],)

    @_('filter NOT LPAREN filter RPAREN')
    def filter(self, p):
        return (p.filter,)


    # valuePath = attrPath "[" valFilter "]"
    #            ; FILTER uses sub-attributes of a parent attrPath

    # valFilter = attrExp / logExp / *1"not" "(" valFilter ")"

    # attrExp   = (attrPath SP "pr") /
    #             (attrPath SP compareOp SP compValue)

    # logExp    = FILTER SP ("and" / "or") SP FILTER

    # compValue = false / null / true / number / string
    #            ; rules from JSON (RFC 7159)

    # compareOp = "eq" / "ne" / "co" /
    #                    "sw" / "ew" /
    #                    "gt" / "lt" /
    #                    "ge" / "le"

    # attrPath  = [URI ":"] ATTRNAME *1subAttr
    #             ; SCIM attribute name
    #             ; URI is SCIM "schema" URI

    # ATTRNAME  = ALPHA *(nameChar)

    # nameChar  = "-" / "_" / DIGIT / ALPHA

    # subAttr   = "." ATTRNAME
    #             ; a sub-attribute of a complex attribute



    #@_('statements')
    #def basicblock(self, p):
    #    return p.statements

    #@_('')
    #def basicblock(self, p):
    #    return []

    #@_('statements statement')
    #def statements(self, p):
    #    p.statements.append(p.statement)
    #    return p.statements

    #@_('statement')
    #def statements(self, p):
    #    return [ p.statement ]

    #@_('print_statement',
    #   'const_declaration',
    #   'var_declaration',
    #   'assignment_statement',
    #   'if_statement',
    #   'while_statement',
    #   'func_declaration',
    #   'return_statement',)
    #def statement(self, p):
    #    return p[0] #p[0]

    #@_('PRINT expression SEMI')
    #def print_statement(self, p):
    #    return PrintStatement(p.expression, lineno=p.lineno)

    #@_('CONST ID ASSIGN expression SEMI')
    #def const_declaration(self, p):
    #    return ConstDeclaration(p.ID, p.expression, lineno=p.lineno)

    #@_('VAR ID datatype SEMI')
    #def var_declaration(self, p):
    #    return VarDeclaration(p.ID, p.datatype, None, lineno=p.lineno)

    #@_('VAR ID datatype ASSIGN expression SEMI')
    #def var_declaration(self, p):
    #    return VarDeclaration(p.ID, p.datatype, p.expression, lineno=p.lineno)

    #@_('location ASSIGN expression SEMI')
    #def assignment_statement(self, p):
    #    return Assignment(p.location, p.expression, lineno=p.lineno)

    #@_('literal')
    #def expression(self, p):
    #    return p.literal

    #@_('INTEGER')
    #def literal(self, p):
    #    if p.INTEGER[0:2] == '0x':
    #        base = 16
    #    else:
    #        base = 10
    #    return IntegerLiteral(int(p.INTEGER,base), lineno=p.lineno)

    #@_('FLOAT')
    #def literal(self, p):
    #    return FloatLiteral(float(p.FLOAT), lineno=p.lineno)

    #@_('CHAR')
    #def literal(self, p):
    #    return CharLiteral(eval(p.CHAR), lineno=p.lineno)

    #@_('TRUE')
    #def literal(self, p):
    #    return BoolLiteral(True, lineno=p.lineno)

    #@_('FALSE')
    #def literal(self, p):
    #    return BoolLiteral(False, lineno=p.lineno)

    #@_('expression PLUS expression',
    #   'expression MINUS expression',
    #   'expression TIMES expression',
    #   'expression DIVIDE expression',
    #   'expression LE expression',
    #   'expression LT expression',
    #   'expression GE expression',
    #   'expression GT expression',
    #   'expression EQ expression',
    #   'expression NE expression',
    #   'expression LAND expression',
    #   'expression LOR expression')
    #def expression(self, p):
    #    return BinOp(p[1], p.expression0, p.expression1, lineno=p.lineno)

    #@_('PLUS expression',
    #   'MINUS expression',
    #   'LNOT expression %prec UNARY')
    #def expression(self, p):
    #    return UnaryOp(p[0], p.expression, lineno=p.lineno)

    #@_('LPAREN expression RPAREN')
    #def expression(self, p):
    #    return p.expression

    #@_('location')
    #def expression(self, p):
    #    return ReadValue(p.location, lineno=p.location.lineno)

    #@_('GROW expression')
    #def expression(self, p):
    #    return GrowMemory(p.expression, lineno=p.lineno)

    #@_('ID')
    #def datatype(self, p):
    #    return SimpleType(p.ID, lineno=p.lineno)

    #@_('ID')
    #def location(self, p):
    #    return SimpleLocation(p.ID, lineno=p.lineno)

    #@_('DEREF expression')
    #def location(self, p):
    #    return MemoryLocation(p.expression, lineno=p.lineno)

    #@_('IF expression LBRACE basicblock RBRACE ELSE LBRACE basicblock RBRACE')
    #def if_statement(self, p):
    #    return IfStatement(p.expression, p.basicblock0, p.basicblock1, lineno=p.lineno)

    #@_('IF expression LBRACE basicblock RBRACE')
    #def if_statement(self, p):
    #    return IfStatement(p.expression, p.basicblock, [], lineno=p.lineno)

    #@_('WHILE expression LBRACE basicblock RBRACE')
    #def while_statement(self, p):
    #    return WhileStatement(p.expression, p.basicblock, lineno=p.lineno)

    #@_('FUNC ID LPAREN parameters RPAREN datatype LBRACE basicblock RBRACE')
    #def func_declaration(self, p):
    #    return FuncDeclaration(p.ID, p.parameters, p.datatype, p.basicblock, lineno=p.lineno)

    #@_('IMPORT FUNC ID LPAREN parameters RPAREN datatype SEMI')
    #def func_declaration(self, p):
    #    return FuncDeclaration(p.ID, p.parameters, p.datatype, [], lineno=p.lineno, body=None)

    #@_('RETURN expression SEMI')
    #def return_statement(self, p):
    #    return ReturnStatement(p.expression, lineno=p.lineno)

    #@_('parmlist')
    #def parameters(self, p):
    #    return p.parmlist

    #@_('')
    #def parameters(self, p):
    #    return [ ]

    #@_('parmlist COMMA parm')
    #def parmlist(self, p):
    #    p.parmlist.append(p.parm)
    #    return p.parmlist

    #@_('parm')
    #def parmlist(self, p):
    #    return [ p.parm ]

    #@_('ID datatype')
    #def parm(self, p):
    #    return Parameter(p.ID, p.datatype, lineno=p.lineno)

    #@_('ID LPAREN arguments RPAREN')
    #def expression(self, p):
    #    if typesys.lookup_type(p.ID) and len(p.arguments) == 1:
    #        return TypeCast(p.ID, p.arguments[0], lineno=p.lineno)
    #    else:
    #        return FunctionCall(p.ID, p.arguments, lineno=p.lineno)

    #@_('arglist')
    #def arguments(self, p):
    #    return p.arglist

    #@_('')
    #def arguments(self, p):
    #    return []

    #@_('arglist COMMA expression')
    #def arglist(self, p):
    #    p.arglist.append(p.expression)
    #    return p.arglist

    #@_('expression')
    #def arglist(self, p):
    #    return [ p.expression ]

    # catch-all error handling.   The following function gets called on any
    # bad input.  p is the offending token or None if end-of-file (EOF).
    def error(self, p):
        if p:
            error(p.lineno, f"Syntax error in input at token '{p.value}'")
        else:
            error('EOF','Syntax error. No more input.')


def main():
    '''
    Main program. Used for testing.
    '''
    import sys

     if len(sys.argv) != 2:
        sys.stderr.write('Usage: python \n')
        raise SystemExit(1)

    lexer = SCIMLexer()
    parser = SCIMParser()
    ast = parser.parse(lexer.tokenize(source))

    # Output the resulting parse tree structure
    for depth, node in flatten(ast):
        print(' '*(4*depth), node)


if __name__ == '__main__':
    main()

