#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import abort, Blueprint, request, jsonify, g, url_for
import json, datetime
from functools import wraps
from app.utils import *
from app.models.user import User
from app import app, db, auth, basicauth, cache

mod = Blueprint("v1_auth", __name__, url_prefix="/v1/auth")

@mod.route("/user", methods=["GET"])
@auth.login_required
def single():
    user = g.user
    if not user:
        abort(400)

    result = jsonify(
        prepare_json_response(
            message="User found",
            success=True,
            data=user.serialize
        )
    )

    return result


@mod.route("/user/token", methods=["GET"])
@basicauth.login_required
def token():
    token = g.user.generate_auth_token(app.config['TOKEN_MAX_AGE'])
    return jsonify(
        prepare_json_response(
            message=None,
            success=True,
            data=g.user.serialize
        )
    )


@basicauth.verify_password
def verify_password(email, password):
    # try to authenticate with username/password
    user = User.query.filter_by(email=email).first()
    if not user:
        abort(401, 'The email you have entered is invalid')
    if not user.verify_password(password):
        abort(401, 'The password you have entered is invalid')
    if not user.status == STATUS_ACTIVE:
        abort(401, 'Email not validated')
    g.user = user
    return True

@auth.verify_token
def verify_token(token):
    g.user = User.verify_auth_token(token)
    if not g.user:
        abort(401)
    g.user.modified_on = datetime.datetime.utcnow()
    db.session.commit()
    return True
