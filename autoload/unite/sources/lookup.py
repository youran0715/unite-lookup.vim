#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_cache import *

class Lookup(object):
    def __init__(self):
        self.cache = Cache()
        self.input_kws = []
        self.input_paths = []
        self.candidates = []
        self.max_candidates = 50
        self.min_input = 1
        self.is_fuzzy = True
        self.is_path_split = False
        self._escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])

    def load(self):
        pass

    def redraw(self):
        self.cache.clear()
        pass

    def search(self, inputs):
        pass

    def contain_upper(self, kw):
        prog = re.compile('[A-Z]+')
        return prog.search(kw)

    def is_search_lower(self, kw):
        return False if self.contain_upper(kw) else True

    def get_regex_prog(self, kw):
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

    def calc_score_by_name_with_dir(self, reprog, filename, dirname):
        result = reprog.search(filename)
        if result:
            score = result.start() * 2
            score = score + result.end() - result.start() + 1
            score = score + ( len(filename) + 1 ) / 100.0
            score = score + ( len(dirname) + 1 ) / 1000.0
            return 1000.0 / score

        return 0

    def calc_score_by_name(self, reprog, name):
        result = reprog.search(name)
        if result:
            score = result.start() * 2
            score = result.end() - result.start() + 1
            score = score + ( len(name) + 1 ) / 100.0
            return 1000.0 / score

        return 0

def main():
    lookup = Lookup()

if __name__ == "__main__":
    main()
