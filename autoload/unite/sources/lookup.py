#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re
from lookup_cache import *

class Lookup(object):
    def __init__(self):
        self.cache = LookupCache()
        self.inputs = ""
        self.input_kws = []
        self.input_paths = []
        self.re_kws = []
        self.re_paths = []
        self.candidates = []
        self.max_candidates = 50
        self.min_input = 0
        self.is_path_split = False

        self.filter = None

    def load(self):
        pass

    def redraw(self):
        self.cache.clear()
        pass

    def parse_inputs(self):
        inputs = self.inputs

        if inputs == "" or inputs == ";" or inputs.strip() == "":
            return

        inputItmes = inputs.split(';')
        inputKw = inputItmes[0] if len(inputItmes) > 0 else ""
        inputPath = inputItmes[1] if len(inputItmes) > 1 else ""

        self.input_kws = re.split('\s', inputKw)
        self.input_paths = re.split('\s', inputPath)

        for kw in self.input_kws:
            if kw != "":
                self.re_kws.append(self.filter.get_regex(kw))

        for kw in self.input_paths:
            if kw != "":
                self.re_paths.append(self.filter.get_regex(kw))

        return

    def get_result(self, inputs):
        pass

    def is_input_empty(self):
        return len(self.input_kws) == 0 and len(self.input_paths) == 0

    def is_input_length_ok(self):
        if self.min_input == 0:
            return True

        if len(self.input_kws) <= 0:
            return False

        if len(self.input_kws[0]) < self.min_input:
            return False

        return True


    def search(self, inputs):
        self.inputs = inputs

        self.parse_inputs()
        if not self.is_input_length_ok():
            return [{'word': inputs, 'abbr': 'Please input at least %d chars' % self.min_input}]

        pass

    def calc_score_by_name_with_dir(self, reprog, filename, dirname):
        result = reprog.search(filename)
        if result:
            score = result.start() * 2
            score = score + result.end() - result.start() + 1
            score = score + ( len(filename) + 1 ) / 100.0
            score = score + ( len(dirname) + 1 ) / 1000.0
            return 1000.0 / score

        return 0
