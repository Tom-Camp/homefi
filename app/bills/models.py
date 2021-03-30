from flask_login import current_user

from app import db
from app.auth.models import Base


class Account(Base):

    __tablename__ = "account"

    name = db.Column(db.String(128), nullable=False)
    recurrence = db.Column(db.String(128), nullable=False)
    pay_period = db.Column(db.String(128), nullable=True)
    status = db.Column(db.SmallInteger, nullable=True)
    outstanding = db.Column(db.Numeric, nullable=True)
    apr = db.Column(db.Numeric, nullable=True)
    tag = db.Column(db.String(128), nullable=False)
    url = db.Column(db.String(128), nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"))
    transactions = db.relationship("Transaction")

    def __init__(
        self, name, recurrence, pay_period, outstanding, apr, tag, url, uid, status
    ):
        self.name = name
        self.recurrence = recurrence
        self.pay_period = pay_period
        self.outstanding = outstanding
        self.tag = tag
        self.apr = apr
        self.url = url
        self.uid = current_user.id
        self.status = 1

    def __repr__(self):
        return "<Bill %r>" % (self.name)


class Transaction(Base):

    __tablename__ = "transactions"

    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(128), nullable=True)
    date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp(),
    )
    aid = db.Column(db.Integer, db.ForeignKey("account.id"))
    uid = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, amount, status, date, aid):
        self.amount = amount
        self.status = status
        self.date = date
        self.aid = aid
        self.uid = current_user.id

    def __repr__(self):
        return "<Transaction %r>" % (self.id)
