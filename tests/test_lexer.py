from io import StringIO
import sys
from unittest import TestCase

from scim2_filter_parser import lexer


class RFCExamples(TestCase):
    def setUp(self):
        self.lexer = lexer.SCIMLexer()

    def get_token_tuples(self, query):
        return self.lexer.tokenize(query)

    def assertTokens(self, query, expected):
        token_tuples = [
            (token.type, token.value) for token in self.get_token_tuples(query)
        ]
        self.assertEqual(expected, token_tuples)

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        expected = [
            ('ATTRNAME', 'userName'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'bjensen'),
        ]
        self.assertTokens(query, expected)

    def test_family_name_contains(self):
        query = '''name.familyName co "O'Malley"'''
        expected = [
            ('ATTRNAME', 'name'),
            ('SUBATTR', 'familyName'),
            ('CO', 'co'),
            ('COMP_VALUE', "O'Malley")
        ]
        self.assertTokens(query, expected)

    def test_username_startswith(self):
        query = 'userName sw "J"'
        expected = [
            ('ATTRNAME', 'userName'),
            ('SW', 'sw'),
            ('COMP_VALUE', 'J'),
        ]
        self.assertTokens(query, expected)

    def test_schema_username_startswith(self):
        query = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
        expected = [
            ('SCHEMA_URI', 'urn:ietf:params:scim:schemas:core:2.0:User'),
            ('ATTRNAME', 'userName'),
            ('SW', 'sw'),
            ('COMP_VALUE', 'J'),
        ]
        self.assertTokens(query, expected)

    def test_title_has_value(self):
        query = 'title pr'
        expected = [
            ('ATTRNAME', 'title'),
            ('PR', 'pr')
        ]
        self.assertTokens(query, expected)

    def test_meta_last_modified_gt(self):
        query = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
        expected = [
            ('ATTRNAME', 'meta'),
            ('SUBATTR', 'lastModified'),
            ('GT', 'gt'),
            ('COMP_VALUE', '2011-05-13T04:42:34Z'),
        ]
        self.assertTokens(query, expected)

    def test_meta_last_modified_ge(self):
        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        expected = [
            ('ATTRNAME', 'meta'),
            ('SUBATTR', 'lastModified'),
            ('GE', 'ge'),
            ('COMP_VALUE', '2011-05-13T04:42:34Z'),
        ]
        self.assertTokens(query, expected)

    def test_meta_last_modified_lt(self):
        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        expected = [
            ('ATTRNAME', 'meta'),
            ('SUBATTR', 'lastModified'),
            ('LT', 'lt'),
            ('COMP_VALUE', '2011-05-13T04:42:34Z'),
        ]
        self.assertTokens(query, expected)

    def test_meta_last_modified_le(self):
        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        expected = [
            ('ATTRNAME', 'meta'),
            ('SUBATTR', 'lastModified'),
            ('LE', 'le'),
            ('COMP_VALUE', '2011-05-13T04:42:34Z'),
        ]
        self.assertTokens(query, expected)

    def test_title_has_value_and_user_type_eq(self):
        query = 'title pr and userType eq "Employee"'
        expected = [
            ('ATTRNAME', 'title'),
            ('PR', 'pr'),
            ('AND', 'and'),
            ('ATTRNAME', 'userType'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'Employee')
        ]
        self.assertTokens(query, expected)

    def test_title_has_value_or_user_type_eq(self):
        query = 'title pr or userType eq "Intern"'
        expected = [
            ('ATTRNAME', 'title'),
            ('PR', 'pr'),
            ('OR', 'or'),
            ('ATTRNAME', 'userType'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'Intern')
        ]
        self.assertTokens(query, expected)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        expected = [
            ('ATTRNAME', 'schemas'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User')
        ]
        self.assertTokens(query, expected)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        expected = [
            ('ATTRNAME', 'userType'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'Employee'),
            ('AND', 'and'),
            ('LPAREN', '('),
            ('ATTRNAME', 'emails'),
            ('CO', 'co'),
            ('COMP_VALUE', 'example.com'),
            ('OR', 'or'),
            ('ATTRNAME', 'emails'),
            ('SUBATTR', 'value'),
            ('CO', 'co'),
            ('COMP_VALUE', 'example.org'),
            ('RPAREN', ')')
        ]
        self.assertTokens(query, expected)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        expected = [
            ('ATTRNAME', 'userType'),
            ('NE', 'ne'),
            ('COMP_VALUE', 'Employee'),
            ('AND', 'and'),
            ('NOT', 'not'),
            ('LPAREN', '('),
            ('ATTRNAME', 'emails'),
            ('CO', 'co'),
            ('COMP_VALUE', 'example.com'),
            ('OR', 'or'),
            ('ATTRNAME', 'emails'),
            ('SUBATTR', 'value'),
            ('CO', 'co'),
            ('COMP_VALUE', 'example.org'),
            ('RPAREN', ')')
        ]
        self.assertTokens(query, expected)

    def test_user_type_eq_and_not_email_type_eq(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        expected = [
            ('ATTRNAME', 'userType'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'Employee'),
            ('AND', 'and'),
            ('LPAREN', '('),
            ('ATTRNAME', 'emails'),
            ('SUBATTR', 'type'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'work'),
            ('RPAREN', ')')
        ]
        self.assertTokens(query, expected)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        expected = [
            ('ATTRNAME', 'userType'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'Employee'),
            ('AND', 'and'),
            ('ATTRNAME', 'emails'),
            ('LBRACKET', '['),
            ('ATTRNAME', 'type'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'work'),
            ('AND', 'and'),
            ('ATTRNAME', 'value'),
            ('CO', 'co'),
            ('COMP_VALUE', '@example.com'),
            ('RBRACKET', ']')
        ]
        self.assertTokens(query, expected)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        expected = [
            ('ATTRNAME', 'emails'),
            ('LBRACKET', '['),
            ('ATTRNAME', 'type'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'work'),
            ('AND', 'and'),
            ('ATTRNAME', 'value'),
            ('CO', 'co'),
            ('COMP_VALUE', '@example.com'),
            ('RBRACKET', ']'),
            ('OR', 'or'),
            ('ATTRNAME', 'ims'),
            ('LBRACKET', '['),
            ('ATTRNAME', 'type'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'xmpp'),
            ('AND', 'and'),
            ('ATTRNAME', 'value'),
            ('CO', 'co'),
            ('COMP_VALUE', '@foo.com'),
            ('RBRACKET', ']')
        ]
        self.assertTokens(query, expected)


class RegressionTestQueries(TestCase):
    def setUp(self):
        self.lexer = lexer.SCIMLexer()

    def get_token_tuples(self, query):
        return self.lexer.tokenize(query)

    def assertTokens(self, query, expected):
        token_tuples = [
            (token.type, token.value) for token in self.get_token_tuples(query)
        ]
        self.assertEqual(expected, token_tuples)

    def test_co_after_dot_not_considered_CO_token(self):
        query = 'addresses[type eq "work"].country eq ""'
        expected = [
            ('ATTRNAME', 'addresses'),
            ('LBRACKET', '['),
            ('ATTRNAME', 'type'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'work'),
            ('RBRACKET', ']'),
            ('SUBATTR', 'country'),
            ('EQ', 'eq'),
            ('COMP_VALUE', '')
        ]
        self.assertTokens(query, expected)

    def test_members(self):
        query = 'members[value eq "6784"] eq ""'
        expected = [
            ('ATTRNAME', 'members'),
            ('LBRACKET', '['),
            ('ATTRNAME', 'value'),
            ('EQ', 'eq'),
            ('COMP_VALUE', '6784'),
            ('RBRACKET', ']'),
            ('EQ', 'eq'),
            ('COMP_VALUE', '')
        ]
        self.assertTokens(query, expected)


class TokenNotMistakenAsOperatorTestQueries(TestCase):
    def setUp(self):
        self.lexer = lexer.SCIMLexer()

    def get_token_tuples(self, query):
        return self.lexer.tokenize(query)

    def assertTokens(self, query, expected):
        token_tuples = [
            (token.type, token.value) for token in self.get_token_tuples(query)
        ]
        self.assertEqual(expected, token_tuples)

    def test_pr_in_preferred_not_considered_pr_token(self):
        query = 'preferredLanguage eq ""'
        expected = [
            ('ATTRNAME', 'preferredLanguage'),
            ('EQ', 'eq'),
            ('COMP_VALUE', ''),
        ]
        self.assertTokens(query, expected)

    def test_cap_pr_token(self):
        query = 'lang Pr'
        expected = [
            ('ATTRNAME', 'lang'),
            ('PR', 'Pr'),
        ]
        self.assertTokens(query, expected)

    def test_token_startswith_op_code(self):
        op_codes = {
            'eg', 'ne', 'co', 'sw', 'ew', 'pr', 'gt', 'ge', 'lt', 'le',
            'and', 'or', 'not'
        }
        for op_code in op_codes:
            for permuation in self.get_op_permutation(op_code):
                attrname = permuation + 'ing'  # Add any suffix to make token an attrname
                attr_token, eq_token, comp_token = self.get_token_tuples(attrname + ' eq ""')

                self.assertEqual(attr_token.type, 'ATTRNAME')
                self.assertEqual(attr_token.value, attrname)
                self.assertEqual(eq_token.type, 'EQ')
                self.assertEqual(comp_token.type, 'COMP_VALUE')

    def get_op_permutation(self, op_code):
        """
        Get all the capitalization permutations for a specific op_code.
        """
        permuations = []
        for i in range(2 ** len(op_code)):
            # use bits as indices to capitalize
            mask = str(bin(i)).replace('0b', '').zfill(len(op_code))

            permuation = ''
            for j, char in enumerate(op_code):
                if mask[j:j+1] == '1':
                    permuation += char.upper()
                else:
                    permuation += char.lower()

            permuations.append(permuation)

        return permuations


class AzureQueries(TestCase):
    def setUp(self):
        self.lexer = lexer.SCIMLexer()

    def get_token_tuples(self, query):
        return self.lexer.tokenize(query)

    def assertTokens(self, query, expected):
        token_tuples = [
            (token.type, token.value) for token in self.get_token_tuples(query)
        ]
        self.assertEqual(expected, token_tuples)

    def test_email_type_eq_primary_value_eq_uuid(self):
        query = 'emails[type eq "Primary"].value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        expected = [
            ('ATTRNAME', 'emails'),
            ('LBRACKET', '['),
            ('ATTRNAME', 'type'),
            ('EQ', 'eq'),
            ('COMP_VALUE', 'Primary'),
            ('RBRACKET', ']'),
            ('SUBATTR', 'value'),
            ('EQ', 'eq'),
            ('COMP_VALUE', '001750ca-8202-47cd-b553-c63f4f245940')
        ]
        self.assertTokens(query, expected)

    def test_external_id_from_azure(self):
        query = 'externalId eq "4d32ab19-ae09-4236-82fa-15768bc48a08"'
        expected = [
            ('ATTRNAME', 'externalId'),
            ('EQ', 'eq'),
            ('COMP_VALUE', '4d32ab19-ae09-4236-82fa-15768bc48a08')
        ]
        self.assertTokens(query, expected)

    def test_parse_simple_email_filter_with_uuid(self):
        query = 'emails.value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        expected = [
            ('ATTRNAME', 'emails'),
            ('SUBATTR', 'value'),
            ('EQ', 'eq'),
            ('COMP_VALUE', '001750ca-8202-47cd-b553-c63f4f245940')
        ]
        self.assertTokens(query, expected)


class CommandLine(TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        lexer.main(['userName eq "bjensen"'])
        result = self.test_stdout.getvalue().strip().split('\n')
        expected = [
            "Token(type='ATTRNAME', value='userName', lineno=1, index=0)",
            "Token(type='EQ', value='eq', lineno=1, index=9)",
            "Token(type='COMP_VALUE', value='bjensen', lineno=1, index=12)",
        ]
        self.assertEqual(result, expected)

