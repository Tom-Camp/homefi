import pytest
from app.auth.models import User
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

    yield app

    db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def load_db():
    users = get_users()

    for us in users:
        u = User(name=us.name, email=us.email, password=us.password)
        db.session.add(u)
        db.session.commit()


def get_users():
    return [
        {
            "name": "Test User",
            "email": "test@test.com",
            "password": "pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f",
        },
        {
            "name": "Other User",
            "email": "test@testcom",
            "password": "pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79",
        },
    ]
