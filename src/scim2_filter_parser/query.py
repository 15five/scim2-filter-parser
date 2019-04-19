"""
The logic in this module builds a full SQL query based on a SCIM filter.
"""
from .lexer import SCIMLexer
from .parser import SCIMParser
from .transpiler import SCIMToSQLTranspiler


class Query:
    placeholder = '%s'

    def __init__(self, filter_, table_name, attr_map, joins=()):
        self.filter: str = filter_
        self.table_name: str = table_name
        self.attr_map: dict = attr_map
        self.joins = joins
        self.where_sql: str = None
        self.where_params: dict = None
        self.params: list = None

        self.build_where_sql()

    def build_where_sql(self):
        token_stream = SCIMLexer().tokenize(self.filter)
        ast = SCIMParser().parse(token_stream)
        sql, params = SCIMToSQLTranspiler(self.attr_map).transpile(ast)

        self.where_sql = sql
        self.where_params = params

        self.params = [params.get(i) for i in range(len(params))]

    @property
    def sql(self) -> str:
        # Replace {#} with placeholder string. Different database
        # connectors can override this with their own placeholder character.
        placeholders = [self.placeholder for i in range(len(self.params))]
        where_sql = self.where_sql.format(*placeholders)
        # Stitch all joins together
        joins = '\n'.join(self.joins)
        if joins:
            joins += '\n'
        return f'''
        SELECT {self.table_name}.*
        FROM {self.table_name}
        {joins}WHERE {where_sql};
        '''.strip()

    def __str__(self) -> str:
        orig_placeholder = self.placeholder
        self.placeholder = '{}'
        sql = self.sql.format(*self.params)
        self.placeholder = orig_placeholder

        # Wrap the SQL in invalid characters so users don't accidentally
        # walk into a SQL Injection vulnerability.
        return '>>>' + sql + '<<<'


class SQLiteQuery(Query):
    placeholder = '?'


def main():
    '''
    Main program. Used for testing.
    '''
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python -m scim2_filter_parser.query <filter>\n')
        raise SystemExit(1)

    attr_map = {
        ('username', None, None): 'users.username',
        ('name', 'familyname', None): 'users.family_name',
        ('meta', 'lastmodified', None): 'update_ts',
    }

    joins = (
        'LEFT JOIN emails ON emails.user_id = users.id',
        'LEFT JOIN schemas ON schemas.user_id = users.id',
    )

    q = SQLiteQuery(sys.argv[1], 'users', attr_map, joins)

    print(q)


if __name__ == '__main__':
    main()

