import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    register_url = '/auth/register'
    data = {
        'username': 'a',
        'password': 'a',
    }
    assert client.get(register_url).status_code == 200
    response = client.post(
        register_url,
        data=data
    )
    assert response.headers['Location'] == '/auth/login'

    with app.app_context():
        assert get_db().execute(
            'SELECT * FROM user WHERE username = \'a\'',
        ).fetchone() is not None


@pytest.mark.parametrize(
    ('username', 'password', 'message'),
    (
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
    )
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username':username, 'password':password}
    )
    assert message in response.data


def test_login(client, auth):
    # To test that the page renders successfully
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
