import re
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from . import db


# Raw SQL tables aren't created by Django migrations, so we create them manually.
def create_game_tables():
    db.execute("""
        CREATE TABLE IF NOT EXISTS user_login (
            user_id CHAR(36) NOT NULL PRIMARY KEY,
            name VARCHAR(100) DEFAULT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id CHAR(36) NOT NULL PRIMARY KEY,
            points BIGINT NOT NULL DEFAULT 0,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)


# Settings that disable CSRF enforcement and Secure cookies for test client (HTTP)
NO_CSRF = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'UNAUTHENTICATED_USER': None,
}


@override_settings(
    REST_FRAMEWORK=NO_CSRF,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
class UserEndpointTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_game_tables()

    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        res = self.client.get('/api/user/me/')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data['points'], 0)
        self.assertIsNotNone(res.data['user_id'])

    def test_session_persistence(self):
        res1 = self.client.get('/api/user/me/')
        res2 = self.client.get('/api/user/me/')
        self.assertEqual(res1.data['user_id'], res2.data['user_id'])
        self.assertEqual(res2.status_code, 200)

    def test_orphaned_session(self):
        res1 = self.client.get('/api/user/me/')
        old_id = res1.data['user_id']
        # Delete user from DB but session still has the ID
        db.execute("DELETE FROM players WHERE user_id = %s", [old_id])
        db.execute("DELETE FROM user_login WHERE user_id = %s", [old_id])
        res2 = self.client.get('/api/user/me/')
        self.assertEqual(res2.status_code, 201)
        self.assertNotEqual(res2.data['user_id'], old_id)

    def test_response_shape(self):
        res = self.client.get('/api/user/me/')
        self.assertEqual(set(res.data.keys()), {'user_id', 'name', 'points', 'created_at'})


@override_settings(
    REST_FRAMEWORK=NO_CSRF,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
class PointsEndpointTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_game_tables()

    def setUp(self):
        self.client = APIClient()
        self.client.get('/api/user/me/')  # create user + session

    def test_add_points(self):
        res = self.client.post('/api/user/me/points/', {'amount': 5}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['points'], 5)

    def test_accumulate_points(self):
        self.client.post('/api/user/me/points/', {'amount': 5}, format='json')
        res = self.client.post('/api/user/me/points/', {'amount': 10}, format='json')
        self.assertEqual(res.data['points'], 15)

    def test_no_session(self):
        fresh_client = APIClient()
        res = fresh_client.post('/api/user/me/points/', {'amount': 1}, format='json')
        self.assertEqual(res.status_code, 401)

    def test_invalid_amount_string(self):
        res = self.client.post('/api/user/me/points/', {'amount': 'abc'}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_invalid_amount_negative(self):
        res = self.client.post('/api/user/me/points/', {'amount': -1}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_invalid_amount_zero(self):
        res = self.client.post('/api/user/me/points/', {'amount': 0}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_default_amount(self):
        res = self.client.post('/api/user/me/points/', {}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['points'], 1)


@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class CsrfTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_game_tables()

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def test_get_returns_csrf_cookie(self):
        res = self.client.get('/api/user/me/')
        self.assertIn('agame_csrf', res.cookies)

    def test_post_without_csrf_rejected(self):
        self.client.get('/api/user/me/')
        res = self.client.post('/api/user/me/points/', {'amount': 1}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_post_with_csrf_accepted(self):
        get_res = self.client.get('/api/user/me/')
        csrf_token = get_res.cookies['agame_csrf'].value
        res = self.client.post(
            '/api/user/me/points/',
            {'amount': 1},
            format='json',
            headers={'X-CSRFToken': csrf_token},
        )
        self.assertEqual(res.status_code, 200)


@override_settings(
    REST_FRAMEWORK=NO_CSRF,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
)
class DatabaseTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_game_tables()

    def setUp(self):
        self.client = APIClient()

    def test_both_tables_populated(self):
        res = self.client.get('/api/user/me/')
        user_id = res.data['user_id']
        count_login = db.fetch_one(
            "SELECT COUNT(*) FROM user_login WHERE user_id = %s",
            [user_id],
        )[0]
        self.assertEqual(count_login, 1)
        count_players = db.fetch_one(
            "SELECT COUNT(*) FROM players WHERE user_id = %s",
            [user_id],
        )[0]
        self.assertEqual(count_players, 1)

    def test_user_id_is_uuid(self):
        res = self.client.get('/api/user/me/')
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        self.assertRegex(res.data['user_id'], uuid_pattern)
