from io import StringIO
import sys
from unittest import TestCase

from scim2_filter_parser.lexer import SCIMLexer
from scim2_filter_parser.parser import SCIMParser
import scim2_filter_parser.transpilers.sql as transpile_sql


class RFCExamples(TestCase):
    attr_map = {
        ('name', 'familyName', None): 'name.familyname',
        ('emails', None, None): 'emails',
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
        ('userName', None, None): 'username',
        ('nickName', None, None): 'nickname',
        ('title', None, None): 'title',
        ('userType', None, None): 'usertype',
        ('schemas', None, None): 'schemas',
        ('userName', None, 'urn:ietf:params:scim:schemas:core:2.0:User'): 'username',
        ('nickName', None, 'urn:ietf:params:scim:schemas:core:2.0:User'): 'nickname',
        ('meta', 'lastModified', None): 'meta.lastmodified',
        ('ims', 'type', None): 'ims.type',
        ('ims', 'value', None): 'ims.value',
    }

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()
        self.transpiler = transpile_sql.Transpiler(self.attr_map)

    def assertSQL(self, query, expected_sql, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        sql, params = self.transpiler.transpile(ast)

        self.assertEqual(expected_sql, sql, query)
        self.assertEqual(expected_params, params, query)

    def test_attr_paths_are_created(self):
        query = 'userName eq "bjensen"'
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        self.transpiler.transpile(ast)

        self.assertEqual(len(self.transpiler.attr_paths), 1)
        for path in self.transpiler.attr_paths:
            self.assertTrue(isinstance(path, transpile_sql.AttrPath))

    # userName is always case-insensitive
    # https://datatracker.ietf.org/doc/html/rfc7643#section-4.1.1
    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        sql = "username ILIKE {a}"
        params = {'a': 'bjensen'}
        self.assertSQL(query, sql, params)

    def test_nickname_eq(self):
        query = 'nickName eq "Bob"'
        sql = "nickname = {a}"
        params = {'a': 'Bob'}
        self.assertSQL(query, sql, params)

    def test_family_name_contains(self):
        query = '''name.familyName co "O'Malley"'''
        sql = "name.familyname LIKE {a}"
        params = {'a': "%O'Malley%"}
        self.assertSQL(query, sql, params)

    def test_username_startswith(self):
        query = 'userName sw "J"'
        sql = "username ILIKE {a}"
        params = {'a': 'J%'}
        self.assertSQL(query, sql, params)

    def test_nickname_startswith(self):
        query = 'nickName sw "J"'
        sql = "nickname LIKE {a}"
        params = {'a': 'J%'}
        self.assertSQL(query, sql, params)

    def test_schema_username_startswith(self):
        query = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
        sql = "username ILIKE {a}"
        params = {'a': 'J%'}
        self.assertSQL(query, sql, params)

    def test_schema_nickname_startswith(self):
        query = 'urn:ietf:params:scim:schemas:core:2.0:User:nickName sw "J"'
        sql = "nickname LIKE {a}"
        params = {'a': 'J%'}
        self.assertSQL(query, sql, params)

    def test_title_has_value(self):
        query = 'title pr'
        sql = 'title IS NOT NULL'
        params = {'a': None}
        self.assertSQL(query, sql, params)

    def test_meta_last_modified_gt(self):
        query = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
        sql = "meta.lastmodified > {a}"
        params = {'a': '2011-05-13T04:42:34Z'}
        self.assertSQL(query, sql, params)

    def test_meta_last_modified_ge(self):
        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        sql = "meta.lastmodified >= {a}"
        params = {'a': '2011-05-13T04:42:34Z'}
        self.assertSQL(query, sql, params)

    def test_meta_last_modified_lt(self):
        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        sql = "meta.lastmodified < {a}"
        params = {'a': '2011-05-13T04:42:34Z'}
        self.assertSQL(query, sql, params)

    def test_meta_last_modified_le(self):
        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        sql = "meta.lastmodified <= {a}"
        params = {'a': '2011-05-13T04:42:34Z'}
        self.assertSQL(query, sql, params)

    def test_title_has_value_and_user_type_eq(self):
        query = 'title pr and userType eq "Employee"'
        sql = "(title IS NOT NULL) AND (usertype = {b})"
        params = {'a': None, 'b': 'Employee'}
        self.assertSQL(query, sql, params)

    def test_title_has_value_or_user_type_eq(self):
        query = 'title pr or userType eq "Intern"'
        sql = "(title IS NOT NULL) OR (usertype = {b})"
        params = {'a': None, 'b': 'Intern'}
        self.assertSQL(query, sql, params)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        sql = "schemas = {a}"
        params = {'a': "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"}
        self.assertSQL(query, sql, params)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        sql = "(usertype = {a}) AND ((emails LIKE {b}) OR (emails.value LIKE {c}))"
        params = {'a': 'Employee', 'b': '%example.com%', 'c': '%example.org%'}
        self.assertSQL(query, sql, params)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        sql = "(usertype != {a}) AND (NOT ((emails LIKE {b}) OR (emails.value LIKE {c})))"
        params = {'a': 'Employee', 'b': '%example.com%', 'c': '%example.org%'}
        self.assertSQL(query, sql, params)

    def test_user_type_eq_and_not_email_type_eq(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        sql = "(usertype = {a}) AND (emails.type = {b})"
        params = {'a': 'Employee', 'b': 'work'}
        self.assertSQL(query, sql, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        sql = "(usertype = {a}) AND ((emails.type = {b}) AND (emails.value LIKE {c}))"
        params = {'a': 'Employee', 'b': 'work', 'c': '%@example.com%'}
        self.assertSQL(query, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "((emails.type = {a}) AND (emails.value LIKE {b})) OR ((ims.type = {c}) AND (ims.value LIKE {d}))"
        params = {'a': 'work', 'b': '%@example.com%', 'c': 'xmpp', 'd': '%@foo.com%'}
        self.assertSQL(query, sql, params)


class UndefinedAttributes(TestCase):

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()

    def assertSQL(self, query, attr_map, expected_sql, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        sql, params = transpile_sql.Transpiler(attr_map).transpile(ast)

        self.assertEqual(expected_sql, sql, query)
        self.assertEqual(expected_params, params, query)

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        sql = None
        params = {}
        attr_map = {}
        self.assertSQL(query, attr_map, sql, params)

    def test_title_has_value_and_user_type_eq_1(self):
        query = 'title pr and userType eq "Employee"'
        sql = "title IS NOT NULL"
        params = {'a': None}
        attr_map = {
            ('title', None, None): 'title',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_title_has_value_and_user_type_eq_2(self):
        query = 'title pr and userType eq "Employee"'
        sql = "usertype = {a}"
        params = {'a': 'Employee'}
        attr_map = {
            ('userType', None, None): 'usertype',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        sql = None
        params = {}
        attr_map = {}
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        sql = "(usertype = {a}) AND ((emails LIKE {b}) OR (emails.value LIKE {c}))"
        params = {'a': 'Employee', 'b': '%example.com%', 'c': '%example.org%'}
        attr_map = {
            ('userType', None, None): 'usertype',
            ('emails', None, None): 'emails',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        sql = "(usertype != {a}) AND (NOT ((emails LIKE {b}) OR (emails.value LIKE {c})))"
        params = {'a': 'Employee', 'b': '%example.com%', 'c': '%example.org%'}
        attr_map = {
            ('userType', None, None): 'usertype',
            ('emails', None, None): 'emails',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_1(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        sql = "usertype = {a}"
        params = {'a': 'Employee'}
        attr_map = {
            ('userType', None, None): 'usertype',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_2(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        sql = "emails.type = {a}"
        params = {'a': 'work'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_1(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        sql = "usertype = {a}"
        params = {'a': 'Employee'}
        attr_map = {
            ('userType', None, None): 'usertype',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_2(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        sql = "emails.type = {a}"
        params = {'a': 'work'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_3(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        sql = "(emails.type = {a}) AND (emails.value LIKE {b})"
        params = {'a': 'work', 'b': '%@example.com%'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_1(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "(emails.value LIKE {a}) OR (ims.type = {b})"
        params = {'a': '%@example.com%', 'b': 'xmpp'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('ims', 'type', None): 'ims.type',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_2(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "(emails.value LIKE {a}) OR ((ims.type = {b}) AND (ims.value LIKE {c}))"
        params = {'a': '%@example.com%', 'b': 'xmpp', 'c': '%@foo.com%'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('ims', 'type', None): 'ims.type',
            ('ims', 'value', None): 'ims.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_3(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "((emails.type = {a}) AND (emails.value LIKE {b})) OR (ims.type = {c})"
        params = {'a': 'work', 'b': '%@example.com%', 'c': 'xmpp'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('emails', 'type', None): 'emails.type',
            ('ims', 'type', None): 'ims.type',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_4(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "(emails.type = {a}) OR (ims.value LIKE {b})"
        params = {'a': 'work', 'b': '%@foo.com%'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
            ('ims', 'value', None): 'ims.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_email_type_eq_primary_value_eq_uuid_1(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        sql = "emails.value = {a}"
        params = {'a': '001750ca-8202-47cd-b553-c63f4f245940'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_email_type_eq_primary_value_eq_uuid_2(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        sql = "emails.type = {a}"
        params = {'a': 'Primary'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertSQL(query, attr_map, sql, params)


class AzureQueries(TestCase):
    attr_map = {
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
        ('externalId', None, None): 'externalid',
    }

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()
        self.transpiler = transpile_sql.Transpiler(self.attr_map)

    def assertSQL(self, query, expected_sql, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        sql, params = self.transpiler.transpile(ast)

        self.assertEqual(expected_sql, sql, query)
        self.assertEqual(expected_params, params, query)

    def test_email_type_eq_primary_value_eq_uuid(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        sql = "(emails.type = {a} AND emails.value = {b})"
        params = {'a': 'Primary', 'b': '001750ca-8202-47cd-b553-c63f4f245940'}
        self.assertSQL(query, sql, params)

    def test_external_id_from_azure(self):
        query = 'externalId eq "4d32ab19-ae09-4236-82fa-15768bc48a08"'
        sql = "externalid = {a}"
        params = {'a': '4d32ab19-ae09-4236-82fa-15768bc48a08'}
        self.assertSQL(query, sql, params)

    def test_parse_simple_email_filter_with_uuid(self):
        query = 'emails.value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        sql = "emails.value = {a}"
        params = {'a': '001750ca-8202-47cd-b553-c63f4f245940'}
        self.assertSQL(query, sql, params)


class GitHubBugsQueries(TestCase):
    attr_map = {
        ('emails', 'type', None): 'emails.type',
    }

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()
        self.transpiler = transpile_sql.Transpiler(self.attr_map)

    def assertSQL(self, query, expected_sql, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        sql, params = self.transpiler.transpile(ast)

        self.assertEqual(expected_sql, sql, query)
        self.assertEqual(expected_params, params, query)

    def test_g15_ne_op(self):
        query = 'emails[type ne "work"]'
        sql = "emails.type != {a}"
        params = {'a': 'work'}
        self.assertSQL(query, sql, params)


class CommandLine(TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        transpile_sql.main(['userName eq "bjensen"'])
        result = self.test_stdout.getvalue().strip().split('\n')
        expected = [
            'SQL: username ILIKE {a}',
            "PARAMS: {'a': 'bjensen'}"
        ]
        self.assertEqual(result, expected)

