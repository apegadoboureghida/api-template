#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import abort
from app import app, db
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired, URLSafeTimedSerializer)
from passlib.apps import custom_app_context
from hashids import Hashids
import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String(512), index=True)
    referral_code = db.Column(db.String(512))
    account_type = db.Column(db.Integer, default=0)
    credits = db.Column(db.Integer, default=3)
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    status = db.Column(db.Integer, default=0)
    token = db.Column(db.String(512))
    stripe_id = db.Column(db.String(64))
    company = db.Column(db.String(512))
    modified_on = db.Column(db.Date, default=datetime.datetime.utcnow)
    created_on = db.Column(db.Date, default=datetime.datetime.utcnow)

    def hash_password(self, password):
        if len(password) < 8 or len(password) > 17:
            abort(401, 'The password length must be between 8 and 17 (included) characters.')
        self.password_hash = custom_app_context.encrypt(password)

    def verify_password(self, password):
        if len(password) < 8 or len(password) > 17:
            abort(401, 'The password length must be between 8 and 17 (included) characters.')
        if self.password_hash is None:
            return True
        else:
            return custom_app_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        self.token = s.dumps({'id': self.id})
        db.session.commit()
        return self.token

    def generate_url_token(self):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return serializer.dumps(self.id, salt=app.config['SECURITY_PASSWORD_SALT'])

    def generate_referral_token(self):
        hashids = Hashids()
        referral = hashids.encode(self.id)
        return referral

    def activate_user(self):
        self.status = STATUS_ACTIVE
        self.credits = app.config['REFERRAL_INITIAL_CREDITS']
        hashids = Hashids()
        if self.referral_code is not None and len(hashids.decode(user.referral_code)) > 0:
            referral_user = User.query.filter_by(id=hashids.decode(user.referral_code)).first()
            if referral_user is not None:
                referral_user.credits = referral_user.credits + app.config['REFERRAL_ADD_CREDITS']
        db.session.commit()

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {"id": self.id, "username": self.username,
                "first_name": self.first_name, "last_name": self.last_name,
                "account_type": self.account_type, "credits": self.credits,
                "email": self.email, "referral_code": self.referral_code,
                "company": self.company, "password": self.password_hash is not None,
                "token": {"token": self.token, "duration": app.config['TOKEN_MAX_AGE']}}

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = db.session.query(User).filter(User.id == data["id"]).first()

        if not user or user.token != token:
           return None
        return user


    @staticmethod
    def create_user(email, password, referral_code):
        a_user = User(email=email)

        if password is not None:
            a_user.hash_password(password)

        a_user.account_type = app.config['DEFAULT_ACCOUNT']

        # Saving referal code
        if referral_code is not None:
            a_user.referral_code = referral_code

        # id needed for next steps
        db.session.add(a_user)
        db.session.commit()

        #Send Email confirmation
        if app.config['EMAIL_CONFIRMATION']:
            a_user.status = STATUS_PENDING
            confirmEmail(email,User.query.filter_by(email=a_user.email).first())
        else:
            a_user.activate_user()

        #Storing new user
        db.session.add(a_user)
        db.session.commit()

        #Subscribe user to mailchimp
        if app.config['AUTO_SUBSCRIPTION']:
            subscribeUser(email)

        return a_user
