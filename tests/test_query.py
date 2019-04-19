import sqlite3
from unittest import TestCase

from scim2_filter_parser.query import SQLiteQuery


class RFCExamples(TestCase):

    CREATE_TABLE_USER = '''
    CREATE TABLE users
    (
        id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        title TEXT,
        update_ts DATETIME,
        user_type TEXT
    )
    '''

    INSERT_USERS = '''
    INSERT INTO users
        (username, first_name, last_name, title, update_ts, user_type)
    VALUES
        ('bjenson', 'Brie', 'Jenson', 'CEO', '2018-10-15 12:00:51.123', 'Employee'),
        ('momalley', 'Mike', 'O''Malley', 'Teacher', '2018-10-15 12:00:51.123', 'Employee')
    '''

    CREATE_TABLE_EMAIL = '''
    CREATE TABLE emails
    (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        text TEXT,
        type TYPE,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    '''

    CREATE_TABLE_IMS = '''
    CREATE TABLE ims
    (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        text TEXT,
        type TYPE,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    '''

    ATTR_MAP = {
        # attr_name, sub_attr, uri: table name
        ('username', None, None): 'username',
    }

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.CREATE_TABLE_USER)
        self.cursor.execute(self.CREATE_TABLE_EMAIL)
        self.cursor.execute(self.CREATE_TABLE_IMS)
        self.cursor.execute(self.INSERT_USERS)
        self.conn.commit()

    def assertSQL(self, query, expected_rows):
        q = SQLiteQuery(query, 'users', self.ATTR_MAP)
        self.cursor.execute(q.sql, q.params)
        results = self.cursor.fetchall()

        self.assertEqual(expected_rows, results)

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        expected_rows = [
            (1, 'bjenson', 'Brie', 'Jenson', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertSQL(query, expected_rows)

#    def test_family_name_contains(self):
#        query = '''name.familyName co "O'Malley"'''
#        sql = "name.familyname LIKE '%{0}%'"
#        params = {0: "O'Malley"}
#        self.assertSQL(query, sql, params)
#
#    def test_username_startswith(self):
#        query = 'userName sw "J"'
#        sql = "username LIKE '{0}%'"
#        params = {0: 'J'}
#        self.assertSQL(query, sql, params)
#
#    def test_schema_username_startswith(self):
#        query = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
#        sql = "username LIKE '{0}%'"
#        params = {0: 'J'}
#        self.assertSQL(query, sql, params)
#
#    def test_title_has_value(self):
#        query = 'title pr'
#        sql = 'title IS NOT NULL'
#        params = {}
#        self.assertSQL(query, sql, params)
#
#    def test_meta_last_modified_gt(self):
#        query = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
#        sql = 'meta.lastmodified > {0}'
#        params = {0: "'2011-05-13T04:42:34Z'"}
#        self.assertSQL(query, sql, params)
#
#    def test_meta_last_modified_ge(self):
#        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
#        sql = 'meta.lastmodified >= {0}'
#        params = {0: "'2011-05-13T04:42:34Z'"}
#        self.assertSQL(query, sql, params)
#
#    def test_meta_last_modified_lt(self):
#        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
#        sql = 'meta.lastmodified < {0}'
#        params = {0: "'2011-05-13T04:42:34Z'"}
#        self.assertSQL(query, sql, params)
#
#    def test_meta_last_modified_le(self):
#        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
#        sql = 'meta.lastmodified =< {0}'
#        params = {0: "'2011-05-13T04:42:34Z'"}
#        self.assertSQL(query, sql, params)
#
#    def test_title_has_value_and_user_type_eq(self):
#        query = 'title pr and userType eq "Employee"'
#        sql = '(title IS NOT NULL) AND (usertype = {0})'
#        params = {0: "'Employee'"}
#        self.assertSQL(query, sql, params)
#
#    def test_title_has_value_or_user_type_eq(self):
#        query = 'title pr or userType eq "Intern"'
#        sql = '(title IS NOT NULL) OR (usertype = {0})'
#        params = {0: "'Intern'"}
#        self.assertSQL(query, sql, params)
#
#    def test_schemas_eq(self):
#        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
#        sql = 'schemas = {0}'
#        params = {0: "'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User'"}
#        self.assertSQL(query, sql, params)
#
#    def test_user_type_eq_and_email_contains_or_email_contains(self):
#        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
#        sql = "(usertype = {0}) AND ((emails LIKE '%{1}%') OR (emails.value LIKE '%{2}%'))"
#        params = {0: "'Employee'", 1: 'example.com', 2: 'example.org'}
#        self.assertSQL(query, sql, params)
#
#    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
#        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
#        sql = "(usertype != {0}) AND (NOT ((emails LIKE '%{1}%') OR (emails.value LIKE '%{2}%')))"
#        params = {0: "'Employee'", 1: 'example.com', 2: 'example.org'}
#        self.assertSQL(query, sql, params)
#
#    def test_user_type_eq_and_not_email_type_eq(self):
#        query = 'userType eq "Employee" and (emails.type eq "work")'
#        sql = '(usertype = {0}) AND (emails.type = {1})'
#        params = {0: "'Employee'", 1: "'work'"}
#        self.assertSQL(query, sql, params)
#
#    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
#        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
#        sql = "(usertype = {0}) AND ((emails.type = {1}) AND (emails.value LIKE '%{2}%'))"
#        params = {0: "'Employee'", 1: "'work'", 2: '@example.com'}
#        self.assertSQL(query, sql, params)
#
#    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians(self):
#        query = ('emails[type eq "work" and value co "@example.com"] or '
#                 'ims[type eq "xmpp" and value co "@foo.com"]')
#        sql = "((emails.type = {0}) AND (emails.value LIKE '%{1}%')) OR ((ims.type = {2}) AND (ims.value LIKE '%{3}%'))"
#        params = {0: "'work'", 1: '@example.com', 2: "'xmpp'", 3: '@foo.com'}
#        self.assertSQL(query, sql, params)
#
