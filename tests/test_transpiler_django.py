import sys
from io import StringIO
from unittest import TestCase

from django.db.models import Q

import scim2_filter_parser.transpilers.django as transpile_django
from scim2_filter_parser.lexer import SCIMLexer
from scim2_filter_parser.parser import SCIMParser


class RFCExamples(TestCase):
    attr_map = {
        ('name', 'familyName', None): 'name.familyname',
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

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()
        self.transpiler = transpile_django.Transpiler(self.attr_map)

    def assertQ(self, query, expected_django, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        django, params = self.transpiler.transpile(ast)
        self.assertEqual(expected_django, django, query)
        self.assertEqual(expected_params, params, query)
        self.assertEqual(type(eval(django.format(**params))), Q)

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        django = "Q(username__iexact={a})"
        params = {'a': '"bjensen"'}
        self.assertQ(query, django, params)
        self.assertEqual(django.format(**params), 'Q(username__iexact="bjensen")')

    def test_family_name_contains(self):
        query = '''name.familyName co "O'Malley"'''
        django = "Q(name__familyname__icontains={a})"
        params = {'a': "\"O'Malley\""}
        self.assertQ(query, django, params)
        self.assertEqual(django.format(**params), """Q(name__familyname__icontains="O'Malley")""")

    def test_username_startswith(self):
        query = 'userName sw "J"'
        django = "Q(username__istartswith={a})"
        params = {'a': '"J"'}
        self.assertQ(query, django, params)

    def test_schema_username_startswith(self):
        query = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
        django = "Q(username__istartswith={a})"
        params = {'a': '"J"'}
        self.assertQ(query, django, params)

    def test_title_has_value(self):
        query = 'title pr'
        django = 'Q(title__isnull=False)'
        params = {'a': None}
        self.assertQ(query, django, params)

    def test_meta_last_modified_gt(self):
        query = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
        django = "Q(meta__lastmodified__gt={a})"
        params = {'a': '"2011-05-13T04:42:34Z"'}
        self.assertQ(query, django, params)

    def test_meta_last_modified_ge(self):
        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        django = "Q(meta__lastmodified__gte={a})"
        params = {'a': '"2011-05-13T04:42:34Z"'}
        self.assertQ(query, django, params)

    def test_meta_last_modified_lt(self):
        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        django = "Q(meta__lastmodified__lt={a})"
        params = {'a': '"2011-05-13T04:42:34Z"'}
        self.assertQ(query, django, params)

    def test_meta_last_modified_le(self):
        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        django = "Q(meta__lastmodified__lte={a})"
        params = {'a': '"2011-05-13T04:42:34Z"'}
        self.assertQ(query, django, params)

    def test_title_has_value_and_user_type_eq(self):
        query = 'title pr and userType eq "Employee"'
        django = "Q(title__isnull=False) & Q(usertype__iexact={b})"
        params = {'a': None, 'b': '"Employee"'}
        self.assertQ(query, django, params)

    def test_title_has_value_or_user_type_eq(self):
        query = 'title pr or userType eq "Intern"'
        django = "Q(title__isnull=False) | Q(usertype__iexact={b})"
        params = {'a': None, 'b': '"Intern"'}
        self.assertQ(query, django, params)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        django = "Q(schemas__iexact={a})"
        params = {'a': '"urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'}
        self.assertQ(query, django, params)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        django = "Q(usertype__iexact={a}) & (Q(emails__icontains={b}) | Q(emails__value__icontains={c}))"
        params = {'a': '"Employee"', 'b': '"example.com"', 'c': '"example.org"'}
        self.assertQ(query, django, params)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        django = "~Q(usertype__iexact={a}) & ~(Q(emails__icontains={b}) | Q(emails__value__icontains={c}))"
        params = {'a': '"Employee"', 'b': '"example.com"', 'c': '"example.org"'}
        self.assertQ(query, django, params)

    def test_user_type_eq_and_not_email_type_eq(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        django = "Q(usertype__iexact={a}) & Q(emails__type__iexact={b})"
        params = {'a': '"Employee"', 'b': '"work"'}
        self.assertQ(query, django, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        django = "Q(usertype__iexact={a}) & (Q(emails__type__iexact={b}) & Q(emails__value__icontains={c}))"
        params = {'a': '"Employee"', 'b': '"work"', 'c': '"@example.com"'}
        self.assertQ(query, django, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        django = "(Q(emails__type__iexact={a}) & Q(emails__value__icontains={b})) | (Q(ims__type__iexact={c}) & Q(ims__value__icontains={d}))"
        params = {'a': '"work"', 'b': '"@example.com"', 'c': '"xmpp"', 'd': '"@foo.com"'}
        self.assertQ(query, django, params)


class UndefinedAttributes(TestCase):

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()

    def assertQ(self, query, attr_map, expected_django, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        django, params = transpile_django.Transpiler(attr_map).transpile(ast)
        self.assertEqual(expected_django, django, query)
        self.assertEqual(expected_params, params, query)
        if django:
            self.assertEqual(type(eval(django.format(**params))), Q)

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        django = None
        params = {}
        attr_map = {}
        self.assertQ(query, attr_map, django, params)

    def test_title_has_value_and_user_type_eq_1(self):
        query = 'title pr and userType eq "Employee"'
        django = "Q(title__isnull=False)"
        params = {'a': None}
        attr_map = {
            ('title', None, None): 'title',
        }
        self.assertQ(query, attr_map, django, params)

    def test_title_has_value_and_user_type_eq_2(self):
        query = 'title pr and userType eq "Employee"'
        django = "Q(usertype__iexact={a})"
        params = {'a': '"Employee"'}
        attr_map = {
            ('userType', None, None): 'usertype',
        }
        self.assertQ(query, attr_map, django, params)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        django = None
        params = {}
        attr_map = {}
        self.assertQ(query, attr_map, django, params)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        django = "Q(usertype__iexact={a}) & (Q(emails__icontains={b}) | Q(emails__value__icontains={c}))"
        params = {'a': '"Employee"', 'b': '"example.com"', 'c': '"example.org"'}
        attr_map = {
            ('userType', None, None): 'usertype',
            ('emails', None, None): 'emails',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertQ(query, attr_map, django, params)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        django = "~Q(usertype__iexact={a}) & ~(Q(emails__icontains={b}) | Q(emails__value__icontains={c}))"
        params = {'a': '"Employee"', 'b': '"example.com"', 'c': '"example.org"'}
        attr_map = {
            ('userType', None, None): 'usertype',
            ('emails', None, None): 'emails',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertQ(query, attr_map, django, params)

    def test_user_type_eq_and_not_email_type_eq_1(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        django = "Q(usertype__iexact={a})"
        params = {'a': '"Employee"'}
        attr_map = {
            ('userType', None, None): 'usertype',
        }
        self.assertQ(query, attr_map, django, params)

    def test_user_type_eq_and_not_email_type_eq_2(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        django = "Q(emails__type__iexact={a})"
        params = {'a': '"work"'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertQ(query, attr_map, django, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_1(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        django = "Q(usertype__iexact={a})"
        params = {'a': '"Employee"'}
        attr_map = {
            ('userType', None, None): 'usertype',
        }
        self.assertQ(query, attr_map, django, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_2(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        django = "Q(emails__type__iexact={a})"
        params = {'a': '"work"'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertQ(query, attr_map, django, params)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains_3(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        django = "Q(emails__type__iexact={a}) & Q(emails__value__icontains={b})"
        params = {'a': '"work"', 'b': '"@example.com"'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
            ('emails', 'value', None): 'emails.value',
        }
        self.assertQ(query, attr_map, django, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_1(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        django = "Q(emails__value__icontains={a}) | Q(ims__type__iexact={b})"
        params = {'a': '"@example.com"', 'b': '"xmpp"'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('ims', 'type', None): 'ims.type',
        }
        self.assertQ(query, attr_map, django, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_2(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        django = "Q(emails__value__icontains={a}) | (Q(ims__type__iexact={b}) & Q(ims__value__icontains={c}))"
        params = {'a': '"@example.com"', 'b': '"xmpp"', 'c': '"@foo.com"'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('ims', 'type', None): 'ims.type',
            ('ims', 'value', None): 'ims.value',
        }
        self.assertQ(query, attr_map, django, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_3(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        django = "(Q(emails__type__iexact={a}) & Q(emails__value__icontains={b})) | Q(ims__type__iexact={c})"
        params = {'a': '"work"', 'b': '"@example.com"', 'c': '"xmpp"'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
            ('emails', 'type', None): 'emails.type',
            ('ims', 'type', None): 'ims.type',
        }
        self.assertQ(query, attr_map, django, params)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians_4(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        django = "Q(emails__type__iexact={a}) | Q(ims__value__icontains={b})"
        params = {'a': '"work"', 'b': '"@foo.com"'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
            ('ims', 'value', None): 'ims.value',
        }
        self.assertQ(query, attr_map, django, params)

    def test_email_type_eq_primary_value_eq_uuid_1(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        django = "Q(emails__value__iexact={a})"
        params = {'a': '"001750ca-8202-47cd-b553-c63f4f245940"'}
        attr_map = {
            ('emails', 'value', None): 'emails.value',
        }
        self.assertQ(query, attr_map, django, params)

    def test_email_type_eq_primary_value_eq_uuid_2(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        django = "Q(emails__type__iexact={a})"
        params = {'a': '"Primary"'}
        attr_map = {
            ('emails', 'type', None): 'emails.type',
        }
        self.assertQ(query, attr_map, django, params)


class AzureQueries(TestCase):
    attr_map = {
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
        ('externalId', None, None): 'externalid',
    }

    def setUp(self):
        self.lexer = SCIMLexer()
        self.parser = SCIMParser()
        self.transpiler = transpile_django.Transpiler(self.attr_map)

    def assertQ(self, query, expected_django, expected_params):
        tokens = self.lexer.tokenize(query)
        ast = self.parser.parse(tokens)
        django, params = self.transpiler.transpile(ast)
        self.assertEqual(expected_django, django, query)
        self.assertEqual(expected_params, params, query)
        self.assertEqual(type(eval(django.format(**params))), Q)

    def test_email_type_eq_primary_value_eq_uuid(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        django = "Q(emails__type__iexact={a}) & Q(emails__value__iexact={b})"
        params = {'a': '"Primary"', 'b': '"001750ca-8202-47cd-b553-c63f4f245940"'}
        self.assertQ(query, django, params)

    def test_external_id_from_azure(self):
        query = 'externalId eq "4d32ab19-ae09-4236-82fa-15768bc48a08"'
        django = "Q(externalid__iexact={a})"
        params = {'a': '"4d32ab19-ae09-4236-82fa-15768bc48a08"'}
        self.assertQ(query, django, params)

    def test_parse_simple_email_filter_with_uuid(self):
        query = 'emails.value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        django = "Q(emails__value__iexact={a})"
        params = {'a': '"001750ca-8202-47cd-b553-c63f4f245940"'}
        self.assertQ(query, django, params)


class CommandLine(TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        transpile_django.main(['userName eq "bjensen"'])
        result = self.test_stdout.getvalue().strip().split('\n')
        expected = [
            'Django: Q(username__iexact={a})',
            """PARAMS: {'a': '"bjensen"'}"""
        ]
        self.assertEqual(result, expected)
