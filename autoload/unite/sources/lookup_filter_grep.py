#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re
from lookup_filter import *

class LookupFilterGrep(LookupFilter):
    def __init__(self):
        super(LookupFilterGrep, self).__init__()

    def get_score_kw(self, reprog, item):
        return 1 if reprog.search(item[3]) else 0

    def get_score_path(self, reprog, item):
        return 1 if reprog.search(item[0]) else 0

    def get_regex_kw(self, kw):
        islower = self.is_search_lower(kw)
        searchkw = kw.lower() if islower else kw

        escaped = [self._escape.get(c, c) for c in searchkw]

        regex = ''.join(escaped)

        return re.compile(regex)
