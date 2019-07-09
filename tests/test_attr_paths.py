import json
from io import StringIO
import sys
from unittest import TestCase

from scim2_filter_parser import attr_paths as attr_paths_mod


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

    def assertAttrPaths(self, query, expected_attr_paths):
        attr_paths = attr_paths_mod.AttrPaths(query, self.attr_map)

        self.assertEqual(expected_attr_paths, list(attr_paths))

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        attr_paths = [
            ('userName', None, None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_family_name_contains(self):
        query = '''name.familyName co "O'Malley"'''
        attr_paths = [
            ('name', 'familyName', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_username_startswith(self):
        query = 'userName sw "J"'
        attr_paths = [
            ('userName', None, None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_schema_username_startswith(self):
        query = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
        attr_paths = [
            ('userName', None, 'urn:ietf:params:scim:schemas:core:2.0:User'),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_title_has_value(self):
        query = 'title pr'
        attr_paths = [
            ('title', None, None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_meta_last_modified_gt(self):
        query = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
        attr_paths = [
            ('meta', 'lastModified', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_meta_last_modified_ge(self):
        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        attr_paths = [
            ('meta', 'lastModified', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_meta_last_modified_lt(self):
        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        attr_paths = [
            ('meta', 'lastModified', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_meta_last_modified_le(self):
        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        attr_paths = [
            ('meta', 'lastModified', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_title_has_value_and_user_type_eq(self):
        query = 'title pr and userType eq "Employee"'
        attr_paths = [
            ('title', None, None),
            ('userType', None, None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_title_has_value_or_user_type_eq(self):
        query = 'title pr or userType eq "Intern"'
        attr_paths = [
            ('title', None, None),
            ('userType', None, None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        attr_paths = [
            ('schemas', None, None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        attr_paths = [
            ('userType', None, None),
            ('emails', None, None),
            ('emails', 'value', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        attr_paths = [
            ('userType', None, None),
            ('emails', None, None),
            ('emails', 'value', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_user_type_eq_and_not_email_type_eq(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        attr_paths = [
            ('userType', None, None),
            ('emails', 'type', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        attr_paths = [
            ('userType', None, None),
            ('emails', 'type', None),
            ('emails', 'value', None),
        ]
        self.assertAttrPaths(query, attr_paths)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        attr_paths = [
            ('emails', 'type', None),
            ('emails', 'value', None),
            ('ims', 'type', None),
            ('ims', 'value', None),
        ]
        self.assertAttrPaths(query, attr_paths)


class AzureQueries(TestCase):
    attr_map = {
        ('emails', 'type', None): 'emails.type',
        ('emails', 'value', None): 'emails.value',
    }

    def assertAttrPaths(self, query, expected_attr_paths):
        attr_paths = attr_paths_mod.AttrPaths(query, self.attr_map)

        self.assertEqual(expected_attr_paths, list(attr_paths))

    def test_email_type_eq_primary_value_eq_uuid(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        attr_paths = [
            ('emails', 'type', None),
            ('emails', 'value', None),
        ]
        self.assertAttrPaths(query, attr_paths)


class CommandLine(TestCase):

    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        attr_paths_mod.main(['userName eq "bjensen"'])
        result = self.test_stdout.getvalue().strip()
        expected = [['userName', None, None]]
        self.assertEqual(json.loads(result), expected)

