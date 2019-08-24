#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_filter import *

class LookupFilterPath(LookupFilter):
    def __init__(self):
        super(LookupFilterPath, self).__init__()
        pass

    def get_score(self, reprog, item):
        result = reprog.search(name)
        if result:
            score = result.start() * 2
            score = result.end() - result.start() + 1
            score = score + ( len(name) + 1 ) / 100.0
            return 1000.0 / score

        return 0
