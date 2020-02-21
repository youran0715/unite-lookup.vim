#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re
import heapq
import pathlib
from lookup_cache import *

class Lookup(object):
    def __init__(self):
        self.cache = LookupCache()
        self.inputs = ""
        self.input_kws = []
        self.input_paths = []
        self.candidates = []
        self.max_candidates = 200
        self.min_input = 0
        self.is_path_split = False
        self.enable_filter_path = False
        self.buffer = ""
        self.name = "none"

        self.enable = True
        self.filter = None
        self.is_redraw = True
        self.sortable = True

    def do_unite_init(self):
        pass

    def unite_init(self):
        self.do_unite_init()

    def need_sort(self):
        return self.sortable

    def clear_cache(self):
        self.cache.clear()

    def need_gather_candidates(self):
        return self.is_redraw

    def do_gather_candidates(self):
        return self.candidates

    def set_buffer(self, buffer):
        self.buffer = buffer

    def get_buffer_filetype(self):
        return pathlib.Path(self.buffer).suffix

    def gather_candidates(self):
        self.clear_cache()
        self.candidates = self.do_gather_candidates()
        self.is_redraw = False

    def redraw(self):
        self.is_redraw = True

    def parse_inputs(self):
        inputs = self.inputs

        self.input_kws = []
        self.input_paths = []

        if inputs == "" or inputs == ";" or inputs.strip() == "":
            return

        inputItmes = inputs.split(';')
        inputKw = inputItmes[0] if len(inputItmes) > 0 else ""
        inputPath = inputItmes[1] if len(inputItmes) > 1 else ""

        self.input_kws = re.split('\s', inputKw)
        self.input_paths = re.split('\s', inputPath)
        return

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

    def filter_candidates(self):
        if self.cache.exist_result(self.inputs):
            return self.cache.get_result(self.inputs)

        candidates = self.candidates
        if self.cache.exist_pre_candidates(self.inputs):
            candidates = self.cache.get_pre_candidates(self.inputs)

        islower = self.filter.is_search_lower(self.inputs)
        rows = self.filter.get_result(islower, self.input_kws, self.input_paths, candidates)

        result = []
        if self.need_sort():
            result = [line for score, line in heapq.nlargest(self.max_candidates, rows)]
        else:
            result = [line for score, line in rows]
            if len(result) > self.max_candidates:
                result = result[:self.max_candidates]

        self.cache.set_candidates(self.inputs, [line for score, line in rows])
        self.cache.set_result(self.inputs, result)

        return result

    def do_format(self, rows):
        return [{'word': 'Please define do_format for %s' % self.name, 'kind': 'error'}]

    def search(self, inputs):
        if not self.enable:
            return []

        self.inputs = inputs
        self.parse_inputs()

        if not self.is_input_length_ok():
            return [{'kind': 'none', 'word': 'Please input at least %d chars' % self.min_input}]

        if self.need_gather_candidates():
           self.gather_candidates()

        if self.is_input_empty():
            rows = self.candidates if len(self.candidates) <= self.max_candidates else self.candidates[:self.max_candidates]
            # print("input empty rows count:%d" % len(rows))
            return self.do_format(rows)

        rows = self.filter_candidates()

        return self.do_format(rows)

    def calc_score_by_name_with_dir(self, reprog, filename, dirname):
        result = reprog.search(filename)
        if result:
            score = result.start() * 2
            score = score + result.end() - result.start() + 1
            score = score + ( len(filename) + 1 ) / 100.0
            score = score + ( len(dirname) + 1 ) / 1000.0
            return 1000.0 / score

        return 0
