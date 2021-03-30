from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import DecimalField
from wtforms import SelectField
from wtforms import StringField
from wtforms import validators
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import URLField


class AccountCreate(FlaskForm):
    name = StringField(u"Name", [validators.DataRequired()])
    recurrence = SelectField(
        u"Recurrence",
        choices=[
            ("monthly", "Monthly"),
            ("other", "Other"),
        ],
    )
    pay_period = SelectField(
        default="-",
        choices=[
            ("", "-"),
            (10, "10th"),
            (25, "25th"),
        ],
    )
    status = BooleanField(
        u"Active",
        default=True,
        render_kw={"value": "1"},
    )
    outstanding = DecimalField(u"Outstanding", default=0)
    tag = StringField(u"Label")
    apr = DecimalField(u"APR", default=0)
    url = URLField(
        u"URL",
        [
            validators.URL(message="URL validation error."),
        ],
    )


class TransactionCreate(FlaskForm):
    amount = DecimalField(u"Amount")
    status = SelectField(
        "pending",
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
        ],
    )
    date = DateField(u"Date", format="%Y-%m-%d")
