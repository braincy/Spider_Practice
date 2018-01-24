# -*- coding: utf-8 -*-
import oss2
import time
import requests
import random
from scrapy.utils.project import get_project_settings
import hashlib
import sys
import os

class Oss_Adapter:
    _bucket = None

    def __init__(self):
        _settings = get_project_settings()
        auth = oss2.Auth(_settings['ACCESS_KEY_ID'], _settings['ACCESS_KEY_SECRET'])
        service = oss2.Service(auth, _settings['END_POINT'])
        self._bucket = oss2.Bucket(auth, _settings['INTERNAL_END_POINT'], _settings['BUCKET_NAME'])
        pass

    def getName(self, type):
        key = {'page':'fjeiw!#@179'}
        m = hashlib.md5()
        m.update(key[type] + str(time.time()) + type + str(random.random()))
        return m.hexdigest()

    def uploadPage(self, data):
        name = self.getName('page')+'.txt'
        ret = self._bucket.put_object(name, data)
        if ret.status == 200:
            return name
        return ''
