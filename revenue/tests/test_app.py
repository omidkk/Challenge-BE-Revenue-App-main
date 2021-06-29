import pytest

from revenue.app import app


@pytest.fixture(scope='session')
def test_app():
    """
    Creates an instance of the app.

    session scope
    """
    app.config['TESTING'] = True

    yield app


@pytest.fixture(scope='function')
def test_client(test_app):
    """
    Creates a client with a new request context.

    test scope
    """
    app_context = test_app.app_context()
    app_context.push()

    return test_app.test_client()


class TestRoutes:
    def test_index(self, test_client):
        """Test Index."""

        rv = test_client.get('/')
        assert {"hello": "Hello"} == rv.json
