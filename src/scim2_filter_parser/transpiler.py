"""
This module builds SQL queries based on SCIM queries
"""
import ast

from sly import Parser


class SCIMTranspiler(ast.NodeTransformer):
    pass




class SCIMToSQLTranspiler(SCIMTranspiler):

    def __init__(self, attr_map, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params = {}
        self.attr_map = attr_map

    def transpile(self, ast) -> str:
        sql = self.visit(ast)

        return sql, self.params

    def visit_Filter(self, node):
        expr1 = self.visit(node.expr1)
        expr2 = None
        if node.expr2:
            expr2 = self.visit(node.expr2)
        negated = node.negated

        return expr1

    def visit_AttrExpr(self, node):
        attr = self.visit(node.attr_path)
        op_sql = self.visit(node.op)

        if not node.comp_value:
            return f'{attr} {op_sql}'

        # There is a comp_value, so visit node and build SQL.
        item_id = len(self.params)
        self.params[item_id] = self.visit(node.comp_value)

        # prep item_id to be a str replacement placeholder
        item_id = '{' + str(item_id) + '}'

        if '{}' in op_sql:
            op_sql = op_sql.format(f'{item_id}')
            return f'{attr} {op_sql}'
        else:
            return f"{attr} {op_sql} '{item_id}'"

    def lookup_attr(self, attr_name, sub_attr, uri):
        # Convert attr_name to another value based on map.
        # Otherwise, return value.
        value = self.attr_map.get(attr_name)
        if isinstance(value, dict):
            value = value.get(sub_attr)

            if isinstance(value, dict):
                return value.get(uri)

            else:
                return value

        else:
            return value

    def visit_AttrPath(self, node):
        return self.lookup_attr(node.attr_name, node.sub_attr, node.uri)

    def visit_CompValue(self, node):
        return node.value

    def lookup_op(self, node_value):
        sql = {
            'eq': '=',
            'ne': '!=',
            'co': "LIKE '%{}%'",
            'sw': "LIKE '{}%'",
            'ew': "LIKE '%{}'",
            'pr': 'IS NOT NULL',
            'gt': '>',
            'ge': '>=',
            'lt': '<',
            'le': '=<',
        }.get(node_value.lower())

        return sql or node_value

    def visit_AttrExprOp(self, node):
        return self.lookup_op(node.value)



def main():
    '''
    Main program. Used for testing.
    '''
    import sys

    from .lexer import SCIMLexer
    from .parser import SCIMParser

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python -m scim2_filter_parser.transpiler <filter>\n')
        raise SystemExit(1)

    token_stream = SCIMLexer().tokenize(sys.argv[1])
    ast = SCIMParser().parse(token_stream)
    attr_map = {
        'userName': 'users.username',
    }
    sql, params = SCIMToSQLTranspiler(attr_map).transpile(ast)

    print(sql)
    print(params)


if __name__ == '__main__':
    main()

