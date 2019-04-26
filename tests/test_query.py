from io import StringIO
import sqlite3
import sys
import unittest

from scim2_filter_parser import query as scim2_query


class RFCExamples(unittest.TestCase):
    maxDiff = None

    CREATE_TABLE_USERS = '''
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
        (id, username, first_name, last_name, title, update_ts, user_type)
    VALUES
        (1, 'bjensen', 'Brie', 'Jensen', NULL, NULL, NULL),
        (2, 'momalley', 'Mike', 'O''Malley', NULL, NULL, NULL),
        (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', NULL, 'Employee'),
        (4, 'crobertson', 'Carly', 'Robertson', NULL, NULL, 'Intern'),

        (5, 'gt', 'Gina', 'Taylor', NULL, '2012-05-13T04:42:34Z', NULL),
        (6, 'ge', 'Greg', 'Edgar', NULL, '2011-05-13T04:42:34Z', NULL),
        (7, 'lt', 'Lisa', 'Ting', NULL, '2010-05-13T04:42:34Z', NULL),
        (8, 'le', 'Linda', 'Euler', NULL, '2011-05-13T04:42:34Z', NULL)
    '''

    CREATE_TABLE_EMAILS = '''
    CREATE TABLE emails
    (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        text TEXT,
        type TYPE,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    '''

    INSERT_EMAILS = '''
    INSERT INTO emails
        (id, user_id, text, type)
    VALUES
        (1, 3, 'jacob@example.com', 'work'),
        (2, 4, 'carly@example.net', 'home')
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

    INSERT_IMS = '''
    INSERT INTO ims
        (id, user_id, text, type)
    VALUES
        (1, 1, 'brie@foo.com', 'xmpp')
    '''

    CREATE_TABLE_SCHEMAS = '''
    CREATE TABLE schemas
    (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        text TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    '''

    INSERT_SCHEMAS = '''
    INSERT INTO schemas
        (id, user_id, text)
    VALUES
        (1, 4, 'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User')
    '''

    ATTR_MAP = {
        # attr_name, sub_attr, uri: table name
        ('title', None, None): 'users.title',
        ('username', None, None): 'users.username',
        ('usertype', None, None): 'users.user_type',
        ('name', 'familyname', None): 'users.last_name',
        ('meta', 'lastmodified', None): 'users.update_ts',
        ('emails', None, None): 'emails.text',
        ('emails', 'value', None): 'emails.text',
        ('emails', 'type', None): 'emails.type',
        ('ims', 'value', None): 'ims.text',
        ('ims', 'type', None): 'ims.type',
        ('schemas', None, None): 'schemas.text',
        ('username', None, 'urn:ietf:params:scim:schemas:core:2.0:user'): 'username',
    }

    JOINS = (
        'LEFT JOIN emails ON emails.user_id = users.id',
        'LEFT JOIN ims ON ims.user_id = users.id',
        'LEFT JOIN schemas ON schemas.user_id = users.id',
    )

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.CREATE_TABLE_USERS)
        self.cursor.execute(self.INSERT_USERS)
        self.cursor.execute(self.CREATE_TABLE_EMAILS)
        self.cursor.execute(self.INSERT_EMAILS)
        self.cursor.execute(self.CREATE_TABLE_IMS)
        self.cursor.execute(self.INSERT_IMS)
        self.cursor.execute(self.CREATE_TABLE_SCHEMAS)
        self.cursor.execute(self.INSERT_SCHEMAS)
        self.conn.commit()

    def assertRows(self, query, expected_rows):
        q = scim2_query.SQLiteQuery(query, 'users', self.ATTR_MAP, self.JOINS)
        self.cursor.execute(q.sql, q.params)
        results = self.cursor.fetchall()

        self.assertEqual(expected_rows, results)

    def test_username_eq(self):
        query = 'userName eq "bjensen"'
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', None, None, None)
        ]
        self.assertRows(query, expected_rows)

    def test_family_name_contains(self):
        query = '''name.familyName co "O'Malley"'''
        expected_rows = [
            (2, 'momalley', 'Mike', "O'Malley", None, None, None),
        ]
        self.assertRows(query, expected_rows)

    def test_username_startswith(self):
        query = 'userName sw "J"'
        expected_rows = [
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
        ]
        self.assertRows(query, expected_rows)

    def test_schema_username_startswith(self):
        query = 'urn:ietf:params:scim:schemas:core:2.0:User:userName sw "J"'
        expected_rows = [
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
        ]
        self.assertRows(query, expected_rows)

    def test_title_has_value(self):
        query = 'title pr'
        expected_rows = [
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
        ]
        self.assertRows(query, expected_rows)

    def test_meta_last_modified_gt(self):
        query = 'meta.lastModified gt "2011-05-13T04:42:34Z"'
        expected_rows = [
            (5, 'gt', 'Gina', 'Taylor', None, '2012-05-13T04:42:34Z', None),
        ]
        self.assertRows(query, expected_rows)

    def test_meta_last_modified_ge(self):
        query = 'meta.lastModified ge "2011-05-13T04:42:34Z"'
        expected_rows = [
            (5, 'gt', 'Gina', 'Taylor', None, '2012-05-13T04:42:34Z', None),
            (6, 'ge', 'Greg', 'Edgar', None, '2011-05-13T04:42:34Z', None),
            (8, 'le', 'Linda', 'Euler', None, '2011-05-13T04:42:34Z', None)
        ]
        self.assertRows(query, expected_rows)

    def test_meta_last_modified_lt(self):
        query = 'meta.lastModified lt "2011-05-13T04:42:34Z"'
        expected_rows = [
            (7, 'lt', 'Lisa', 'Ting', None, '2010-05-13T04:42:34Z', None),
        ]
        self.assertRows(query, expected_rows)

    def test_meta_last_modified_le(self):
        query = 'meta.lastModified le "2011-05-13T04:42:34Z"'
        expected_rows = [
            (6, 'ge', 'Greg', 'Edgar', None, '2011-05-13T04:42:34Z', None),
            (7, 'lt', 'Lisa', 'Ting', None, '2010-05-13T04:42:34Z', None),
            (8, 'le', 'Linda', 'Euler', None, '2011-05-13T04:42:34Z', None)
        ]
        self.assertRows(query, expected_rows)

    def test_title_has_value_and_user_type_eq(self):
        query = 'title pr and userType eq "Employee"'
        expected_rows = [
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
        ]
        self.assertRows(query, expected_rows)

    def test_title_has_value_or_user_type_eq(self):
        query = 'title pr or userType eq "Intern"'
        expected_rows = [
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
            (4, 'crobertson', 'Carly', 'Robertson', None, None, 'Intern'),
        ]
        self.assertRows(query, expected_rows)

    def test_schemas_eq(self):
        query = 'schemas eq "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"'
        expected_rows = [
            (4, 'crobertson', 'Carly', 'Robertson', None, None, 'Intern'),
        ]
        self.assertRows(query, expected_rows)

    def test_user_type_eq_and_email_contains_or_email_contains(self):
        query = 'userType eq "Employee" and (emails co "example.com" or emails.value co "example.org")'
        expected_rows = [
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
        ]
        self.assertRows(query, expected_rows)

    def test_user_type_ne_and_not_email_contains_or_email_contains(self):
        query = 'userType ne "Employee" and not (emails co "example.com" or emails.value co "example.org")'
        expected_rows = [
            (4, 'crobertson', 'Carly', 'Robertson', None, None, 'Intern'),
        ]
        self.assertRows(query, expected_rows)

    def test_user_type_eq_and_not_email_type_eq(self):
        query = 'userType eq "Employee" and (emails.type eq "work")'
        expected_rows = [
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
        ]
        self.assertRows(query, expected_rows)

    def test_user_type_eq_and_not_email_type_eq_work_and_value_contains(self):
        query = 'userType eq "Employee" and emails[type eq "work" and value co "@example.com"]'
        expected_rows = [
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
        ]
        self.assertRows(query, expected_rows)

    def test_emails_type_eq_work_value_contians_or_ims_type_eq_and_value_contians(self):
        query = ('emails[type eq "work" and value co "@example.com"] or '
                 'ims[type eq "xmpp" and value co "@foo.com"]')
        expected_rows = [
            (1, 'bjensen', 'Brie', 'Jensen', None, None, None),
            (3, 'Jacob', 'Jacob', 'Jingleheimer', 'Friend', None, 'Employee'),
        ]
        self.assertRows(query, expected_rows)


class AzureQueries(unittest.TestCase):
    maxDiff = None

    CREATE_TABLE_USERS = '''
    CREATE TABLE users
    (
        id INTEGER PRIMARY KEY,
        external_id TEXT
    )
    '''

    INSERT_USERS = '''
    INSERT INTO users
        (id, external_id)
    VALUES
        (1, '4d32ab19-ae09-4236-82fa-15768bc48a08'),
        (2, '5ef40940-ae09-4236-82fa-ab184843992c'),
        (3, '83901010-ae09-4236-82fa-576381818313')
    '''

    CREATE_TABLE_EMAILS = '''
    CREATE TABLE emails
    (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        text TEXT,
        type TYPE,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    '''

    INSERT_EMAILS = '''
    INSERT INTO emails
        (id, user_id, text, type)
    VALUES
        (1, 1, '001750ca-8202-47cd-b553-c63f4f245940', 'Primary'),
        (2, 1, 'carly@example.net', 'home'),
        (3, 2, 'james@example.net', 'home'),
        (4, 3, '9438932a-8202-47cd-b553-85afc2939193', 'Primary')
    '''

    ATTR_MAP = {
        # attr_name, sub_attr, uri: table name
        ('externalid', None, None): 'users.external_id',
        ('emails', None, None): 'emails.text',
        ('emails', 'value', None): 'emails.text',
        ('emails', 'type', None): 'emails.type',
    }

    JOINS = (
        'LEFT JOIN emails ON emails.user_id = users.id',
    )

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.CREATE_TABLE_USERS)
        self.cursor.execute(self.INSERT_USERS)
        self.cursor.execute(self.CREATE_TABLE_EMAILS)
        self.cursor.execute(self.INSERT_EMAILS)
        self.conn.commit()

    def assertRows(self, query, expected_rows):
        q = scim2_query.SQLiteQuery(query, 'users', self.ATTR_MAP, self.JOINS)
        self.cursor.execute(q.sql, q.params)
        results = self.cursor.fetchall()
        self.assertEqual(expected_rows, results)
 
    def test_email_type_eq_primary_value_eq_uuid(self):
        query = 'emails[type eq "Primary"].value eq "9438932a-8202-47cd-b553-85afc2939193"'
        expected_rows = [
            (3, '83901010-ae09-4236-82fa-576381818313')
        ]
        self.assertRows(query, expected_rows)

    def test_external_id_from_azure(self):
        query = 'externalId eq "5ef40940-ae09-4236-82fa-ab184843992c"'
        expected_rows = [
            (2, '5ef40940-ae09-4236-82fa-ab184843992c')
        ]
        self.assertRows(query, expected_rows)

    def test_parse_simple_email_filter_with_uuid(self):
        query = 'emails.value eq "001750ca-8202-47cd-b553-c63f4f245940"'
        expected_rows = [
            (1, '4d32ab19-ae09-4236-82fa-15768bc48a08')
        ]
        self.assertRows(query, expected_rows)


class GeneralQueries(unittest.TestCase):
    maxDiff = None

    CREATE_TABLE_USERS = '''
    CREATE TABLE users
    (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    '''

    INSERT_USERS = '''
    INSERT INTO users
        (id, name)
    VALUES
        (1, 'Paul'),
        (2, 'Chris'),
        (3, 'Eileen')
    '''

    CREATE_TABLE_EMAILS = '''
    CREATE TABLE emails
    (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        text TEXT,
        type TYPE,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    '''

    INSERT_EMAILS = '''
    INSERT INTO emails
        (id, user_id, text, type)
    VALUES
        (1, 1, 'paul@example.net', 'home'),
        (2, 1, 'paul@example.net', 'work')
    '''

    ATTR_MAP = {
        # attr_name, sub_attr, uri: table name
        ('emails', 'value', None): 'emails.text',
    }

    JOINS = (
        'LEFT JOIN emails ON emails.user_id = users.id',
    )

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.CREATE_TABLE_USERS)
        self.cursor.execute(self.INSERT_USERS)
        self.cursor.execute(self.CREATE_TABLE_EMAILS)
        self.cursor.execute(self.INSERT_EMAILS)
        self.conn.commit()

    def assertRows(self, query, expected_rows):
        q = scim2_query.SQLiteQuery(query, 'users', self.ATTR_MAP, self.JOINS)
        self.cursor.execute(q.sql, q.params)
        results = self.cursor.fetchall()
        self.assertEqual(expected_rows, results)

    def test_ensure_distinct_rows_fetched(self):
        query = 'emails.value eq "paul@example.net"'
        expected_rows = [
            (1, 'Paul')
        ]
        self.assertRows(query, expected_rows)


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = self.test_stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_command_line(self):
        scim2_query.main(['userName eq "bjensen"'])
        result = self.test_stdout.getvalue().strip().split('\n')

        expected = [
            '>>> DO NOT USE THIS OUTPUT DIRECTLY',
            '>>> SQL INJECTION ATTACK RISK',
            '>>> SQL PREVIEW:',
            '    SELECT DISTINCT users.*',
            '    FROM users',
            '    LEFT JOIN emails ON emails.user_id = users.id',
            '    LEFT JOIN schemas ON schemas.user_id = users.id',
            '    WHERE users.username = bjensen;'
        ]
        self.assertEqual(result, expected)

