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
        ('bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee'),
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

    def assertRows(self, query, expected_rows):
        q = SQLiteQuery(query, 'users', self.ATTR_MAP)
        self.cursor.execute(q.sql, q.params)
        results = self.cursor.fetchall()

        self.assertEqual(expected_rows, results)

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_family_name_contains(self):
        query = '''name.familyName co "O'Malley"'''
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_username_startswith(self):
        query = 'userName sw "J"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_schema_username_startswith(self):
        query = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_title_has_value(self):
        query = 'title pr'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_meta_last_modified_gt(self):
        query = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_meta_last_modified_ge(self):
        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_meta_last_modified_lt(self):
        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_meta_last_modified_le(self):
        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_title_has_value_and_user_type_eq(self):
        query = 'title pr and userType eq "Employee"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_title_has_value_or_user_type_eq(self):
        query = 'title pr or userType eq "Intern"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_user_type_eq_and_not_email_type_eq(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', 'CEO', '2018-10-15 12:00:51.123', 'Employee')
        ]
        self.assertRows(query, expected_rows)

