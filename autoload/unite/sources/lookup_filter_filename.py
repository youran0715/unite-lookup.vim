#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_filter import *

class LookupFilterFilename(LookupFilter):
    def __init__(self):
        super(LookupFilterFilename, self).__init__()
        self.is_filter_path = True
        pass

    def tolower(self, item):
        return (item[0].lower(), item[1].lower())

    def get_score_kw(self, reprog, item):
        result = reprog.search(item[0])
        if result:
            score = result.start() * 2
            score = score + result.end() - result.start() + 1
            score = score + ( len(item[0]) + 1 ) / 100.0
            score = score + ( len(item[1]) + 1 ) / 1000.0
            return 1000.0 / score

        return 0

    def get_score_path(self, reprog, item):
        result = reprog.search(item[1])
        if result:
            score = result.end() - result.start() + 1
            score = score + ( len(item[1]) + 1 ) / 100.0
            return 1000.0 / score

        return 0
