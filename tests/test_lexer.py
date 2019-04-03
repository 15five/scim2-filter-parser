from unittest import TestCase

from scim2_filter_parser.lexer import SCIMLexer


class RFCExamples(TestCase):
    def setUp(self):
        self.lexer = SCIMLexer()

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
            ('DOT', '.'),
            ('ATTRNAME', 'familyName'),
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
            ('SCHEMA_URI', 'urn:ietf:params:scim:schemas:core:2.0:User:userName'),
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
            ('DOT', '.'),
            ('ATTRNAME', 'lastModified'),
            ('GT', 'gt'),
            ('COMP_VALUE', '2011-05-13T04:42:34Z'),
        ]
        self.assertTokens(query, expected)

    def test_meta_last_modified_ge(self):
        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        expected = [
            ('ATTRNAME', 'meta'),
            ('DOT', '.'),
            ('ATTRNAME', 'lastModified'),
            ('GE', 'ge'),
            ('COMP_VALUE', '2011-05-13T04:42:34Z'),
        ]
        self.assertTokens(query, expected)

    def test_meta_last_modified_lt(self):
        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        expected = [
            ('ATTRNAME', 'meta'),
            ('DOT', '.'),
            ('ATTRNAME', 'lastModified'),
            ('LT', 'lt'),
            ('COMP_VALUE', '2011-05-13T04:42:34Z'),
        ]
        self.assertTokens(query, expected)

    def test_meta_last_modified_le(self):
        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        expected = [
            ('ATTRNAME', 'meta'),
            ('DOT', '.'),
            ('ATTRNAME', 'lastModified'),
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
            ('DOT', '.'),
            ('ATTRNAME', 'value'),
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
            ('DOT', '.'),
            ('ATTRNAME', 'value'),
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
            ('DOT', '.'),
            ('ATTRNAME', 'type'),
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

