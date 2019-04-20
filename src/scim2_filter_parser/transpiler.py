"""
The logic in this module builds a portion of a WHERE SQL
clause based on a SCIM filter.
"""
import ast

from sly import Parser

from . import ast as scim2ast


class SCIMTranspiler(ast.NodeTransformer):
    pass


class SCIMToSQLTranspiler(SCIMTranspiler):
    """
    Transpile a SCIM AST into a SQL WHERE clause (not including the "WHERE" keyword)
    """

    def __init__(self, attr_map, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params = {}
        self.attr_map = attr_map

    def transpile(self, ast) -> str:
        sql = self.visit(ast)

        return sql, self.params

    def visit_Filter(self, node):
        if node.namespace:
            # rebuild node with namespace from value path
            if isinstance(node.expr, scim2ast.Filter):
                node.expr = scim2ast.Filter(node.expr.expr, node.expr.negated, node.namespace)
            elif isinstance(node.expr, scim2ast.LogExpr):
                expr1 = scim2ast.Filter(node.expr.expr1.expr, node.expr.expr1.negated, node.namespace)
                expr2 = scim2ast.Filter(node.expr.expr2.expr, node.expr.expr2.negated, node.namespace)
                node.expr = scim2ast.LogExpr(node.expr.op, expr1, expr2)
            elif isinstance(node.expr, scim2ast.AttrExpr):
                # namespace takes place of previous attr_name in attr_path
                sub_attr = scim2ast.SubAttr(node.expr.attr_path.attr_name)
                attr_path = scim2ast.AttrPath(node.namespace.attr_name, sub_attr, node.expr.attr_path.uri)
                node.expr = scim2ast.AttrExpr(node.expr.value, attr_path, node.expr.comp_value)
            else:
                raise NotImplementedError(f'Node {node} can not pass on namespace')

        expr = self.visit(node.expr)
        negated = node.negated

        if node.negated:
            expr = f'NOT ({expr})'

        return expr

    def visit_LogExpr(self, node):
        expr1 = self.visit(node.expr1)
        expr2 = self.visit(node.expr2)
        op = node.op.upper()

        return f'({expr1}) {op} ({expr2})'

    def visit_AttrExpr(self, node):
        attr = self.visit(node.attr_path)
        op_sql = self.lookup_op(node.value)

        if not node.comp_value:
            return f'{attr} {op_sql}'

        # There is a comp_value, so visit node and build SQL.
        item_id = len(self.params)

        # prep item_id to be a str replacement placeholder
        item_id_placeholder = '{' + str(item_id) + '}'

        if 'LIKE' == op_sql:
            # Add appropriate % signs to values in LIKE clause
            prefix, suffix = self.lookup_like_fixes(node.value)
            value = prefix + self.visit(node.comp_value) + suffix
        else:
            value = self.visit(node.comp_value)

        self.params[item_id] = value

        return f'{attr} {op_sql} {item_id_placeholder}'

    def lookup_attr(self, attr_name, sub_attr, uri):
        # Convert attr_name to another value based on map.
        # Otherwise, return value.
        value = self.attr_map.get((attr_name, sub_attr, uri))
        if value:
            return value

        if sub_attr:
            return attr_name + '.' + sub_attr

        return attr_name

    def visit_AttrPath(self, node):
        attr_name_value = node.attr_name.lower()

        sub_attr_value = None
        if node.sub_attr:
            sub_attr_value = node.sub_attr.value.lower()

        uri_value = None
        if node.uri:
            uri_value = node.uri.lower()

        return self.lookup_attr(attr_name_value, sub_attr_value, uri_value)

    def visit_CompValue(self, node):
        if node.value in ('true', 'false', 'null'):
            return node.value.upper()

        # TODO: Handle timestamps!

        return node.value

    def lookup_op(self, node_value):
        op_code = node_value.lower()

        sql = {
            'eq': '=',
            'ne': '!=',
            'co': 'LIKE',
            'sw': 'LIKE',
            'ew': 'LIKE',
            'pr': 'IS NOT NULL',
            'gt': '>',
            'ge': '>=',
            'lt': '<',
            'le': '<=',
        }.get(op_code)

        if not sql:
            raise ValueError(f'Unknown SQL op {op_code}')

        return sql or node_value

    def lookup_like_fixes(self, node_value):
        op_code = node_value.lower()

        sql = {
            'co': ('%', '%'),
            'sw': ('', '%'),
            'ew': ('%', ''),
        }.get(op_code)

        if not sql:
            raise ValueError(f'Unknown SQL LIKE op {op_code}')

        return sql


def main(argv=None):
    '''
    Main program. Used for testing.
    '''
    import argparse
    import sys

    from scim2_filter_parser.lexer import SCIMLexer
    from scim2_filter_parser.parser import SCIMParser

    argv = argv or sys.argv[1:]

    parser = argparse.ArgumentParser('SCIM 2.0 Filter Parser Transpiler')
    parser.add_argument('filter', help="""Eg. 'userName eq "bjensen"'""")
    args = parser.parse_args(argv)

    token_stream = SCIMLexer().tokenize(args.filter)
    ast = SCIMParser().parse(token_stream)
    attr_map = {
        # (attr_name, sub_attr, uri)
        ('username', None, None): 'users.username',
        ('name', 'familyname', None): 'users.family_name',
        ('meta', 'lastmodified', None): 'update_ts',
    }
    sql, params = SCIMToSQLTranspiler(attr_map).transpile(ast)

    print('SQL:', sql)
    print('PARAMS:', params)


if __name__ == '__main__':
    main()

