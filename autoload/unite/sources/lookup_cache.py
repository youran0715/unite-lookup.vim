#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import time

class Cache(object):
    def __init__(self):
        self.clear()

    def set_result(self, key, result, expire):
        self.results[key] = result
        self.expires[key] = time.time() + expire

    def get_result(self, key):
        return self.results[key] if key in self.results else []

    def exist(self, key):
        if key not in self.expires:
            return False

        if self.expires[key] < time.time():
            return False

        return True

    def clear(self):
        self.results = {}
        self.expires = {}
