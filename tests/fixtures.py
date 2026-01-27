import datetime
from unittest.mock import MagicMock
import pytest
from app import create_flask_app
from modelos import db


@pytest.fixture(autouse=True)
def app():
    application = create_flask_app()
    application.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": 'sqlite:///admon_reservas_test.db'
    })
    db.init_app(application)
    db.create_all()

    yield application
    db.session.rollback()
    db.session.close()
    db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def mock_datetime_now(monkeypatch):

    def datetime_mock_func(fake_time):
        datetime_mock = MagicMock(wraps=datetime.datetime)
        datetime_mock.now.return_value = fake_time

        monkeypatch.setattr(datetime, "datetime", datetime_mock)
    return datetime_mock_func
