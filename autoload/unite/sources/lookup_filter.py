#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re

class LookupFilter(object):
    def __init__(self):
        self.is_fuzzy = True
        self.is_smartcase = True
        self.is_casesensive = False
        self._escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])
        pass

    def contain_upper(self, kw):
        prog = re.compile('[A-Z]+')
        return prog.search(kw)

    def is_search_lower(self, kw):
        return False if self.contain_upper(kw) else True

    def get_score_kw(self, regrog, item):
        return 1.0

    def get_score_path(self, regrog, item):
        return 1.0

    def get_regex(self, kw):
        islower = self.is_search_lower(kw)
        searchkw = kw.lower() if islower else kw

        regex = ''
        escaped = [self._escape.get(c, c) for c in searchkw]

        if self.is_fuzzy:
            if len(searchkw) > 1:
                regex = ''.join([c + "[^" + c + "]*" for c in escaped[:-1]])
            regex += escaped[-1]
        else:
            regex = ''.join(escaped)

        return re.compile(regex)
