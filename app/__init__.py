#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
# from raven.contrib.flask import Sentry
from utils import prepare_json_response
from flask import Flask, jsonify, request, session
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth

# Initialize core objects
app = Flask(__name__)
app.config.from_object("config")
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Check Configuration section for more details
db = SQLAlchemy(app)
basicauth = HTTPBasicAuth()
auth = HTTPTokenAuth(scheme='Token')

# # Import Google credentials
# from oauth2client.client import GoogleCredentials
# credentials = GoogleCredentials.get_application_default()

#  Models
from app.models import user

#  Cache inittialization
from app.cache import cache
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# Sentry integration
# sentry = Sentry(app, dsn=app.config["SENTRY_DNS"])

# Imports the Google Cloud client library
# from google.cloud.logging import Client
# if not app.config['DEBUG']:
#     logging_client = Client('enodo-production')
#     handler = logging_client.get_default_handler()
#     cloud_logger = logging.getLogger('cloudLogger')
#     cloud_logger.setLevel(logging.INFO)
#     cloud_logger.addHandler(handler)
#     cloud_logger.info('log activated')
#
# pubsub_client = pubsub.Client()
# topic = pubsub_client.topic('log_predictions')

# Controllers
from app.controllers import default
from app.controllers.v1.auth import auth

app.register_blueprint(default.mod)
app.register_blueprint(auth.mod)

# Manually Adding CORS
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    if request.method == 'DELETE':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response
app.after_request(add_cors_headers)

# Error handlers

# Override the default handlers with JSON responses
@app.errorhandler(400)
def forbidden400(error):                    # pylint: disable=unused-argument
    """
    Renders 400 response
    :returns: JSON
    :rtype: flask.Response
    """
    return jsonify(
        prepare_json_response(
            message="Error 400: Bad request",
            success=False,
            data=error.description
        )
    ), 400


@app.errorhandler(401)
def forbidden401(error):                     # pylint: disable=unused-argument
    """
    Renders 401 response
    :returns: JSON
    :rtype: flask.Response
    """
    return jsonify(
        prepare_json_response(
            message="Error 401: Unauthorized",
            success=False,
            data=error.description
        )
    ), 401


@app.errorhandler(403)
def forbidden403(error):                     # pylint: disable=unused-argument
    """
    Renders 403 response
    :returns: JSON
    :rtype: flask.Response
    """
    return jsonify(
        prepare_json_response(
            message="Error 403: Forbidden",
            success=False,
            data=error.description
        )
    ), 403


@app.errorhandler(404)
def not_found404(error):                     # pylint: disable=unused-argument
    """
    Renders 404 response
    :returns: JSON
    :rtype: flask.Response
    """
    if "message" in error.description:
        message = error.description["message"]
    else:
        message = "Error 404: Not found"
    return jsonify(
        prepare_json_response(
            message=message,
            success=False,
            data=None
        )
    ), 404


@app.errorhandler(405)
def not_found405(error):                     # pylint: disable=unused-argument
    """
    Renders 405 response
    :returns: JSON
    :rtype: flask.Response
    """
    return jsonify(
        prepare_json_response(
            message="Error 405: Method not allowed",
            success=False,
            data=None
        )
    ), 405


@app.errorhandler(409)
def forbidden409(error):                     # pylint: disable=unused-argument
    """
    Renders 409 response
    :returns: JSON
    :rtype: flask.Response
    """
    return jsonify(
        prepare_json_response(
            message="Error 409: Conflict",
            success=False,
            data=error.description
        )
    ), 409

@app.errorhandler(410)
def not_found410(error):                     # pylint: disable=unused-argument
    """
    Renders 410 response
    :returns: JSON
    :rtype: flask.Response
    """
    return jsonify(
        prepare_json_response(
            message="Error 410: We don't have enough data in that zone, we will be there soon",
            success=False,
            data=None
        )
    ), 410


@app.errorhandler(411)
def not_found411(error):                     # pylint: disable=unused-argument

    """
    Renders 411 response
    :returns: JSON
    :rtype: flask.Response
    """
    return jsonify(
        prepare_json_response(
            message="Error 411: We don't have enough apartments/buildings similar to yours, we are working on solving that issue",
            success=False,
            data=None
        )
    ), 411


@app.errorhandler(500)
def internal_server_error500(error):         # pylint: disable=unused-argument
    """
    Renders 500 response
    :returns: JSON
    :rtype: flask.Response
    """
    db.session.rollback()
    db.session.close()
    return jsonify(
        prepare_json_response(
            message="Error 500: Internal server error",
            success=False,
            data=None
        )
    ), 405
