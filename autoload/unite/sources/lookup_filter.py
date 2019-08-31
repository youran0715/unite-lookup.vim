#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

class LookupFilter(object):
    def __init__(self):
        self.is_fuzzy = True
        self.is_smartcase = True
        self.is_casesensive = False
        self.is_filter_path = False
        self._escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])

    def get_result(self, islower, kws, paths, candidates):
        re_kws = []
        re_paths = []
        for kw in kws:
            if kw != "":
                re_kws.append(self.get_regex_kw(kw))

        for kw in paths:
            if kw != "":
                re_paths.append(self.get_regex_path(kw))

        result = []
        for item in candidates:
            score = self.get_score(item, islower, re_kws, re_paths)
            if score > 0:
                result.append((score, item))
        return result

    def get_score(self, item, islower, re_kws, re_paths):
        if islower:
            item = self.tolower(item)

        score_total = 0
        for prog in re_kws:
            score = self.get_score_kw(prog, item)
            if score == 0:
                return 0
            score_total += score

        if self.is_filter_path:
            for prog in re_paths:
                score = self.get_score_path(prog, item)
                if score == 0:
                    return 0
                score_total += score

        return score_total

    def tolower(self, item):
        print("You need define tolower for filter")
        return item

    def contain_upper(self, kw):
        prog = re.compile('[A-Z]+')
        return prog.search(kw)

    def is_search_lower(self, kw):
        return False if self.contain_upper(kw) else True

    def get_score_kw(self, regrog, item):
        return 1.0

    def get_score_path(self, regrog, item):
        return 1.0

    def get_regex_kw(self, kw):
        islower = self.is_search_lower(kw)
        searchkw = kw.lower() if islower else kw

        regex = ''
        escaped = [self._escape.get(c, c) for c in searchkw]

        if self.is_fuzzy:
            if len(searchkw) > 1:
                regex = ''.join([c + "[^" + c + "\/]*" for c in escaped[:-1]])
            regex += escaped[-1]
        else:
            regex = ''.join(escaped)

        return re.compile(regex)

    def get_regex_path(self, kw):
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
