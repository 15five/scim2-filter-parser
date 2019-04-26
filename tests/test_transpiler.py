from io import StringIO
import sys
from unittest import TestCase

from scim2_filter_parser import transpiler
from scim2_filter_parser.lexer import SCIMLexer
from scim2_filter_parser.parser import SCIMParser


class RFCExamples(TestCase):
    attr_map = {
        ('name', 'familyname', None): 'name.familyname',
        ('emails', None, None): 'emails',
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
        ('username', None, None): 'username',
        ('title', None, None): 'title',
        ('usertype', None, None): 'usertype',
        ('schemas', None, None): 'schemas',
        ('username', None, 'urn:ietf:params:scim:schemas:core:2.0:user'): 'username',
        ('meta', 'lastmodified', None): 'meta.lastmodified',
        ('ims', 'type', None): 'ims.type',
        ('ims', 'value', None): 'ims.value',
    }

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()
        self.transpiler = transpiler.SCIMToSQLTranspiler(self.attr_map)

    def assertSQL(self, query, expected_sql, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        sql, params = self.transpiler.transpile(ast)

        self.assertEqual(expected_sql, sql, query)
        self.assertEqual(expected_params, params, query)

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        sql = "username = {0}"
        params = {0: 'bjensen'}
        self.assertSQL(query, sql, params)

    def test_family_name_contains(self):
        query = '''name.familyName co "O'Malley"'''
        sql = "name.familyname LIKE {0}"
        params = {0: "%O'Malley%"}
        self.assertSQL(query, sql, params)

    def test_username_startswith(self):
        query = 'userName sw "J"'
        sql = "username LIKE {0}"
        params = {0: 'J%'}
        self.assertSQL(query, sql, params)

    def test_schema_username_startswith(self):
        query = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
        sql = "username LIKE {0}"
        params = {0: 'J%'}
        self.assertSQL(query, sql, params)

    def test_title_has_value(self):
        query = 'title pr'
        sql = 'title IS NOT NULL'
        params = {}
        self.assertSQL(query, sql, params)

    def test_meta_last_modified_gt(self):
        query = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
        sql = "meta.lastmodified > {0}"
        params = {0: '2011-05-13T04:42:34Z'}
        self.assertSQL(query, sql, params)

    def test_meta_last_modified_ge(self):
        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        sql = "meta.lastmodified >= {0}"
        params = {0: '2011-05-13T04:42:34Z'}
        self.assertSQL(query, sql, params)

    def test_meta_last_modified_lt(self):
        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        sql = "meta.lastmodified < {0}"
        params = {0: '2011-05-13T04:42:34Z'}
        self.assertSQL(query, sql, params)

    def test_meta_last_modified_le(self):
        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        sql = "meta.lastmodified <= {0}"
        params = {0: '2011-05-13T04:42:34Z'}
        self.assertSQL(query, sql, params)

    def test_title_has_value_and_user_type_eq(self):
        query = 'title pr and userType eq "Employee"'
        sql = "(title IS NOT NULL) AND (usertype = {0})"
        params = {0: 'Employee'}
        self.assertSQL(query, sql, params)

    def test_title_has_value_or_user_type_eq(self):
        query = 'title pr or userType eq "Intern"'
        sql = "(title IS NOT NULL) OR (usertype = {0})"
        params = {0: 'Intern'}
        self.assertSQL(query, sql, params)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        sql = "schemas = {0}"
        params = {0: "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"}
        self.assertSQL(query, sql, params)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        sql = "(usertype = {0}) AND ((emails LIKE {1}) OR (emails.value LIKE {2}))"
        params = {0: 'Employee', 1: '%example.com%', 2: '%example.org%'}
        self.assertSQL(query, sql, params)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        sql = "(usertype != {0}) AND (NOT ((emails LIKE {1}) OR (emails.value LIKE {2})))"
        params = {0: 'Employee', 1: '%example.com%', 2: '%example.org%'}
        self.assertSQL(query, sql, params)

    def test_user_type_eq_and_not_email_type_eq(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        sql = "(usertype = {0}) AND (emails.type = {1})"
        params = {0: 'Employee', 1: 'work'}
        self.assertSQL(query, sql, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        sql = "(usertype = {0}) AND ((emails.type = {1}) AND (emails.value LIKE {2}))"
        params = {0: 'Employee', 1: 'work', 2: '%@example.com%'}
        self.assertSQL(query, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "((emails.type = {0}) AND (emails.value LIKE {1})) OR ((ims.type = {2}) AND (ims.value LIKE {3}))"
        params = {0: 'work', 1: '%@example.com%', 2: 'xmpp', 3: '%@foo.com%'}
        self.assertSQL(query, sql, params)


class UndefinedAttributes(TestCase):

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()

    def assertSQL(self, query, attr_map, expected_sql, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        sql, params = transpiler.SCIMToSQLTranspiler(attr_map).transpile(ast)

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
        params = {}
        attr_map = {
            ('title', None, None): 'title',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_title_has_value_and_user_type_eq_2(self):
        query = 'title pr and userType eq "Employee"'
        sql = "usertype = {0}"
        params = {0: 'Employee'}
        attr_map = {
            ('usertype', None, None): 'usertype',
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
        sql = "(usertype = {0}) AND ((emails LIKE {1}) OR (emails.value LIKE {2}))"
        params = {0: 'Employee', 1: '%example.com%', 2: '%example.org%'}
        attr_map = {
            ('usertype', None, None): 'usertype',
            ('emails', None, None): 'emails',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        sql = "(usertype != {0}) AND (NOT ((emails LIKE {1}) OR (emails.value LIKE {2})))"
        params = {0: 'Employee', 1: '%example.com%', 2: '%example.org%'}
        attr_map = {
            ('usertype', None, None): 'usertype',
            ('emails', None, None): 'emails',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_1(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        sql = "usertype = {0}"
        params = {0: 'Employee'}
        attr_map = {
            ('usertype', None, None): 'usertype',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_2(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        sql = "emails.type = {0}"
        params = {0: 'work'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_1(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        sql = "usertype = {0}"
        params = {0: 'Employee'}
        attr_map = {
            ('usertype', None, None): 'usertype',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_2(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        sql = "emails.type = {0}"
        params = {0: 'work'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_3(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        sql = "(emails.type = {0}) AND (emails.value LIKE {1})"
        params = {0: 'work', 1: '%@example.com%'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_1(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "(emails.value LIKE {0}) OR (ims.type = {1})"
        params = {0: '%@example.com%', 1: 'xmpp'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('ims', 'type', None): 'ims.type',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_2(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "(emails.value LIKE {0}) OR ((ims.type = {1}) AND (ims.value LIKE {2}))"
        params = {0: '%@example.com%', 1: 'xmpp', 2: '%@foo.com%'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('ims', 'type', None): 'ims.type',
            ('ims', 'value', None): 'ims.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_3(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "((emails.type = {0}) AND (emails.value LIKE {1})) OR (ims.type = {2})"
        params = {0: 'work', 1: '%@example.com%', 2: 'xmpp'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('emails', 'type', None): 'emails.type',
            ('ims', 'type', None): 'ims.type',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_4(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        sql = "(emails.type = {0}) OR (ims.value LIKE {1})"
        params = {0: 'work', 1: '%@foo.com%'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
            ('ims', 'value', None): 'ims.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_email_type_eq_primary_value_eq_uuid_1(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        sql = "emails.value = {0}"
        params = {0: '001750ca-8202-47cd-b553-c63f4f245940'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
        }
        self.assertSQL(query, attr_map, sql, params)

    def test_email_type_eq_primary_value_eq_uuid_2(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        sql = "emails.type = {0}"
        params = {0: 'Primary'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertSQL(query, attr_map, sql, params)


class AzureQueries(TestCase):
    attr_map = {
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
        ('externalid', None, None): 'externalid',
    }

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()
        self.transpiler = transpiler.SCIMToSQLTranspiler(self.attr_map)

    def assertSQL(self, query, expected_sql, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        sql, params = self.transpiler.transpile(ast)

        self.assertEqual(expected_sql, sql, query)
        self.assertEqual(expected_params, params, query)

    def test_email_type_eq_primary_value_eq_uuid(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        sql = "(emails.type = {0} AND emails.value = {1})"
        params = {0: 'Primary', 1: '001750ca-8202-47cd-b553-c63f4f245940'}
        self.assertSQL(query, sql, params)

    def test_external_id_from_azure(self):
        query = 'externalId eq "4d32ab19-ae09-4236-82fa-15768bc48a08"'
        sql = "externalid = {0}"
        params = {0: '4d32ab19-ae09-4236-82fa-15768bc48a08'}
        self.assertSQL(query, sql, params)

    def test_parse_simple_email_filter_with_uuid(self):
        query = 'emails.value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        sql = "emails.value = {0}"
        params = {0: '001750ca-8202-47cd-b553-c63f4f245940'}
        self.assertSQL(query, sql, params)


class CommandLine(TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        transpiler.main(['userName eq "bjensen"'])
        result = self.test_stdout.getvalue().strip().split('\n')
        expected = [
            'SQL: users.username = {0}',
            "PARAMS: {0: 'bjensen'}"
        ]
        self.assertEqual(result, expected)

