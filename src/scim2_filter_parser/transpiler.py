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

    def visit_LogExpr(self, node):
        expr1 = self.visit(node.expr1)
        expr2 = self.visit(node.expr2)
        op = node.op.upper()

        return f'({expr1}) {op} ({expr2})'

    def visit_AttrExpr(self, node):
        attr = self.visit(node.attr_path)
        op_sql = self.visit(node.op)

        if not node.comp_value:
            return f'{attr} {op_sql}'

        # There is a comp_value, so visit node and build SQL.
        item_id = len(self.params)

        # prep item_id to be a str replacement placeholder
        item_id_placeholder = '{' + str(item_id) + '}'

        if '{}' in op_sql:
            self.params[item_id] = self.visit(node.comp_value).strip("'")

            return attr + ' ' + op_sql.format(f'{item_id_placeholder}')
        else:
            self.params[item_id] = self.visit(node.comp_value)

            return f"{attr} {op_sql} {item_id_placeholder}"

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

        # Handle timestamps!

        return f"'{node.value}'"

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
        ('username', None, None): 'users.username',
        ('name', 'familyname', None): 'users.family_name',
        ('meta', 'lastmodified', None): 'update_ts',
    }
    sql, params = SCIMToSQLTranspiler(attr_map).transpile(ast)

    print(sql)
    print(params)


if __name__ == '__main__':
    main()

