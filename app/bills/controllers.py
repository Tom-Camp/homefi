import datetime

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from sqlalchemy import exc
from sqlalchemy import inspect

from app import db
from app.auth.forms import DeleteForm
from app.bills.forms import AccountCreate
from app.bills.forms import TransactionCreate
from app.bills.models import Account
from app.bills.models import Transaction

bills = Blueprint("bills", __name__)


@bills.route("/account/create", methods=["GET"])
@login_required
def account_create():
    form = AccountCreate(request.form)
    return render_template("bills/acct_form.html", form=form, title=u"Create Account")


@bills.route("/account/create", methods=["POST"])
@login_required
def account_create_submit():
    form = AccountCreate(request.form)
    if not form.validate_on_submit():
        return render_template(
            "bills/acct_form.html", form=form, title=u"Create Account"
        )

    new_acct = Account(
        name=request.form.get("name"),
        recurrence=request.form.get("recurrence"),
        pay_period=request.form.get("pay_period"),
        status=request.form.get("status"),
        outstanding=request.form.get("outstanding"),
        apr=request.form.get("apr"),
        tag=request.form.get("tag"),
        url=request.form.get("url"),
        uid=current_user.id,
    )
    db.session.add(new_acct)
    db.session.commit()
    flash("Account Created", "is-success")
    return redirect(url_for("bills.account_show", aid=new_acct.id))


@bills.route("/account/<aid>/delete", methods=["GET"])
@login_required
def account_delete(aid):
    form = DeleteForm()
    try:
        a = db.session.query(Account).get(aid)
    except exc.SQLAlchemyError:
        flash("Error Loading Account", "is-danger")
        return redirect(url_for("bills.account_list"))
    message = str(
        "Are you sure that you want to delete the account "
        + a.name
        + " and all of its associated transactions?"
    ).format()
    form.cid.data = aid

    return render_template(
        "delete_confirm.html",
        message=message,
        form=form,
        title="Confirm Delete",
    )


# @TODO Not deleting
@bills.route("/account/<aid>/delete", methods=["POST"])
@login_required
def account_delete_submit(aid):
    a = db.session.query(Account).get(aid)
    name = a.name
    try:
        db.session.delete(a)
        db.session.commit()
    except exc.SQLAlchemyError:
        flash("Error Deleting Account", "is-danger")
        return redirect(url_for("bills.account_show", aid=aid))

    flash_message = str("Deleted Account {}").format(name)
    flash(flash_message, "is-danger")
    return redirect(url_for("bills.dashboard"))


@bills.route("/account/<aid>/edit", methods=["GET"])
@login_required
def account_edit(aid):
    form = AccountCreate(request.form)
    try:
        a = db.session.query(Account).get(aid)
    except exc.SQLAlchemyError:
        flash("Error Loading Account", "is-danger")
        return redirect(url_for("bills.account_list"))

    if not a:
        flash("Error Loading Account", "is-danger")
        return redirect(url_for("bills.account_list"))

    form.name.data = a.name
    form.recurrence.data = a.recurrence
    form.pay_period.data = a.pay_period
    form.status.data = a.status
    form.outstanding.data = a.outstanding
    form.apr.data = a.apr
    form.tag.data = a.tag
    form.url.data = a.url

    return render_template("bills/acct_form.html", form=form, title=u"Edit Account")


@bills.route("/account/<aid>/edit", methods=["POST"])
@login_required
def account_edit_submit(aid):
    a = db.session.query(Account).get(aid)
    form = AccountCreate(request.form)
    if form.validate_on_submit():
        a.name = request.form.get("name")
        a.recurrence = request.form.get("recurrence")
        a.pay_period = request.form.get("pay_period")
        a.status = request.form.get("status")
        a.outstanding = request.form.get("outstanding")
        a.apr = request.form.get("apr")
        a.tag = request.form.get("tag")
        a.url = request.form.get("url")
        db.session.commit()
        flash("Account Updated", "is-success")
        return redirect(url_for("bills.account_show", aid=a.id))

    return render_template("bills/acct_form.html", form=form, title=u"Edit Account")


@bills.route("/account/<aid>")
@login_required
def account_show(aid):
    a = Account.query.get(aid)
    t = Transaction.query.filter_by(aid=aid)
    t.order_by(Transaction.date.desc())
    return render_template(
        "bills/account.html",
        account=a,
        title=a.name,
        transactions=t,
    )


@bills.route("/account/list", methods=["GET"])
@login_required
def account_list():
    accts = []
    query = db.session.query(Account)
    query.filter_by(uid=current_user.id).all()
    for row in query:
        accts.append(object_as_dict(row))

    return render_template("bills/account_list.html", accts=accts)


@bills.route("/account/<aid>/pay", methods=["GET"])
@login_required
def transaction_create(aid):
    a = db.session.query(Account).filter_by(id=aid).one()
    form = TransactionCreate(request.form)

    return render_template("bills/bill_form.html", form=form, account=a)


@bills.route("/account/<aid>/pay", methods=["POST"])
@login_required
def transaction_create_submit(aid):
    form = TransactionCreate(request.form)
    if form.validate_on_submit():
        new_t = Transaction(
            amount=request.form.get("amount"),
            aid=aid,
            status=request.form.get("status"),
            date=datetime.datetime.now(),
        )
        flash("Account Updated", "is-success")
        db.session.add(new_t)
        db.session.commit()
        return redirect(url_for("bills.transaction_show", tid=new_t.id))


@bills.route("/transaction/<tid>", methods=["GET"])
@login_required
def transaction_show(tid):
    """Show the transaction"""
    try:
        tr = get_transaction(tid)
    except exc.SQLAlchemyError as e:
        flash(type(e), "is-danger")
        pass

    return render_template(
        "bills/transaction.html",
        t=tr,
    )


@bills.route("/transaction/<tid>/edit", methods=["GET"])
@login_required
def transaction_edit(tid):
    """Edit the transaction"""
    form = TransactionCreate(request.form)
    try:
        t = get_transaction(tid)
    except exc.SQLAlchemyError:
        flash("Error Loading Transaction", "is-danger")
        return redirect(url_for("bills.account_list"))

    if not t:
        flash("Error Loading Transaction", "is-danger")
        return redirect(url_for("bills.account_list"))

    form.amount.data = t.Transaction.amount
    form.status.data = t.Transaction.status
    form.date.data = t.Transaction.date

    return render_template(
        "bills/bill_form.html",
        form=form,
        title=u"Edit Transaction",
        account=t.Account,
    )


@bills.route("/transaction/<tid>/edit", methods=["POST"])
@login_required
def transaction_edit_submit(tid):
    t = db.session.query(Transaction).get(tid)
    a = db.session.query(Account).get(t.aid)
    form = TransactionCreate(request.form)
    if form.validate_on_submit():
        t.amount = request.form.get("amount")
        t.status = request.form.get("status")
        db.session.commit()
        flash("Transaction Updated", "is-success")
        return redirect(url_for("bills.transaction_show", tid=t.id))

    return render_template(
        "bills/bill_form.html", form=form, title=u"Edit Transaction", name=a.name
    )


def get_transaction(tid):
    return (
        db.session.query(
            Account,
            Transaction,
        )
        .join(
            Account,
            Account.id == Transaction.aid,
        )
        .filter(
            Transaction.id == tid,
            Transaction.uid == current_user.id,
        )
        .first()
    )


@bills.route("/dashboard")
@login_required
def dashboard():
    content = {}
    content["pd"] = get_profile_data(current_user.id)
    content["account"] = (
        db.session.query(Account).filter(Account.uid == current_user.id).all()
    )
    try:
        content["pending"] = (
            db.session.query(
                Account,
                Transaction,
            )
            .join(
                Account,
                Account.id == Transaction.aid,
            )
            .filter(
                Transaction.status == "pending",
                Transaction.uid == current_user.id,
            )
            .all()
        )
    except exc.SQLAlchemyError as e:
        flash(type(e), "is-danger")
        pass

    return render_template("bills/dashboard.html", content=content, title=u"Dashboard")


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def get_profile_data(id):
    pd = Account.query.filter(Account.outstanding > 0)
    return pd
