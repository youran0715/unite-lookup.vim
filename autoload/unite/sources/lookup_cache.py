#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import time

class LookupCache(object):
    def __init__(self):
        self.clear()

    def set_result(self, key, result):
        self.results[key] = result

    def get_result(self, key):
        return self.results[key] if key in self.results else []

    def exist_result(self, key):
        return key in self.results 

    def set_candidates(self, key, candidates):
        self.candidates[key] = candidates

    def get_candidates(self, key):
        return self.candidates[key] if key in self.candidates else []

    def exist_pre_candidates(self, key):
        if key == "":
            return False

        key_pre = key[:-1]
        return key_pre in self.candidates

    def get_pre_candidates(self, key):
        if key == "":
            return []

        key_pre = key[:-1]

        return self.get_candidates( key_pre )

    def exist_candidates(self, key):
        return key in self.candidates

    def clear(self):
        self.results = {}
        self.candidates = {}
