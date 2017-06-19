#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

_basedir = os.path.abspath(os.path.dirname(__file__))

#-- Flask
DEBUG = False
SECRET_KEY = "development_key"
SECURITY_PASSWORD_SALT = "development_key_2"
CACHE_TIMEOUT = 60 * 60 * 15  # 15 minutes
APP_NAME = ""

#-- Session
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = 'session'

#-- SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is None:
    SQLALCHEMY_DATABASE_URI = "postgres://user:password@server/db_name"

SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_POOL_TIMEOUT	= 10

#-- Log
GOOGLE_PROJECT_ID = "name"
SENTRY_DNS = "url"
