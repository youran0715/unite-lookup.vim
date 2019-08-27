#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re
from lookup_filter import *

class LookupFilterGrep(LookupFilter):
    def __init__(self):
        super(LookupFilterGrep, self).__init__()
        pass

    def get_score_kw(self, reprog, item):
        result = reprog.search(item[3])
        return 1 if result else 0

    def get_score_path(self, reprog, item):
        result = reprog.search(item[0])
        return 1 if result else 0

    def get_regex_kw(self, kw):
        islower = self.is_search_lower(kw)
        searchkw = kw.lower() if islower else kw

        escaped = [self._escape.get(c, c) for c in searchkw]

        regex = ''.join(escaped)

        return re.compile(regex)
