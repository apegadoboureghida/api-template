#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
import urllib
import json


def prepare_json_response(success, message, data=None):
    response = {"meta":{"success":success, "request":request.url}}
    if data:
        response["data"] = data
        response["meta"]["data_count"] = len(data)

    if message:
        response["meta"]["message"] = message

    return response


def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

class Fips():

    @staticmethod
    def get(lat, lng):
        try:
            url = 'http://data.fcc.gov/api/block/find?format=json&latitude={0}&longitude={1}&showall={2}'.format(lat, lng, True)
            data = json.loads(urllib.urlopen(url).read())
            response = data['Block']['FIPS'].replace('.','')
            return response[:11], response
        except Exception,e:
            return None, None

class Walkscore():

    @staticmethod
    def get(street_address, city, st, zip):
        formatted_address = '%s, %s, %s %s' % (street_address, city, st, zip)
        try:
            url = 'https://www.walkscore.com/auth/_pv/overview/{0}?d=current'.format(formatted_address)
            response = urllib.urlopen(url).read()
            json_object = json.loads(response)
            return json_object['walkscore']
        except Exception,e:
            return None
