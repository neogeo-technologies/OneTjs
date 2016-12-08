# -*- coding: utf-8 -*-

from flask import render_template
from flask import url_for
from flask import redirect
from flask import flash
from flask import request

from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required

from flask_admin.contrib.sqla import ModelView

from app import bcrypt
from app import app
from app import db
from app import admin

from app.models.models import User

from app.forms import LoginForm
from app.forms import RegisterForm

admin.add_view(ModelView(User, db.session))


def render_object_list(template_name, query, paginate_by=10, **context):
    page = request.args.get("page")
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    object_list = query.paginate(page, paginate_by)

    return render_template(template_name, object_list=object_list, **context)


@app.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash("Thank you for registering.", "success")
        return redirect(url_for("users"))

    return render_template("register.html", form=form)


@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form["password"]):
            login_user(user)
            flash("You are logged in. Welcome!", "success")
            return redirect(url_for("users"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("login.html", form=form)
    return render_template("login.html", title="Please Login", form=form)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You were logged out. Bye!", "success")
    return redirect(url_for("index"))


@app.route("/users/")
@login_required
def users():
    user_objects = User.query.order_by(User.id.asc())
    return render_object_list("users.html", user_objects, cfg=app.config)
