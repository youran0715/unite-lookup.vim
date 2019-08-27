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
        self.re_kws = []
        self.re_paths = []
        self.candidates = []
        self.max_candidates = 20
        self.min_input = 0
        self.is_path_split = False
        self.enable_filter_path = False
        self.buffer = ""
        self.name = "none"

        self.enable = True
        self.filter = None
        self.is_load_candidates = False
        self.is_redraw = False

    def need_sort(self):
        return True

    def need_clear_cache(self):
        return False

    def need_gather_candidates(self):
        return not self.is_load_candidates

    def do_gather_candidates(self, is_redraw = False):
        return self.candidates

    def set_buffer(self, buffer):
        self.buffer = buffer

    def get_buffer_filetype(self):
        return pathlib.Path(self.buffer).suffix

    def gather_candidates(self):
        self.cache.clear()
        self.candidates = self.do_gather_candidates(self.is_redraw)
        self.is_load_candidates = True
        self.is_redraw = False

    def redraw(self):
        self.is_load_candidates = False
        self.is_redraw = True

    def parse_inputs(self):
        inputs = self.inputs

        self.re_kws = []
        self.re_paths = []
        self.input_kws = []
        self.input_paths = []

        if inputs == "" or inputs == ";" or inputs.strip() == "":
            return

        inputItmes = inputs.split(';')
        inputKw = inputItmes[0] if len(inputItmes) > 0 else ""
        inputPath = inputItmes[1] if len(inputItmes) > 1 else ""

        self.input_kws = re.split('\s', inputKw)
        self.input_paths = re.split('\s', inputPath)
        for kw in self.input_kws:
            if kw != "":
                self.re_kws.append(self.filter.get_regex_kw(kw))

        for kw in self.input_paths:
            if kw != "":
                self.re_paths.append(self.filter.get_regex_path(kw))

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

    def format(self, rows):
        return [{'word': row, 'kind': 'None'} for row in rows]

    def filter_candidates(self):
        if self.cache.exist_result(self.inputs):
            return self.cache.get_result(self.inputs)

        candidates = []
        if self.cache.exist_pre_candidates(self.inputs):
            candidates = self.cache.get_pre_candidates(self.inputs)
            # print("%s use pre candidates, len:%d" % (self.name, len(candidates)))
            # print(candidates)
        else:
            # print("candidates len:%d" % len(self.candidates))
            candidates = self.candidates

        rows = []
        rows_cache = []
        islower = self.filter.is_search_lower(self.inputs)
        for item in candidates:
            itemcmp = None
            if type(item) == type("") and islower:
                itemcmp = item.lower()
            elif type(item) == type(("", "")) and islower:
                if len(item) == 2:
                    itemcmp = (item[0].lower(), item[1].lower())
                elif len(item) == 4:
                    itemcmp = (item[0].lower(), item[1].lower(), item[2].lower(), item[3].lower())
            else:
                itemcmp = item

            ok = True
            score_total = 0
            for prog in self.re_kws:
                score = self.filter.get_score_kw(prog, itemcmp)
                if score == 0:
                    ok = False
                    break
                score_total += score

            if not ok:
                continue

            if self.enable_filter_path:
                for prog in self.re_paths:
                    score = self.filter.get_score_path(prog, itemcmp)
                    if score == 0:
                        ok = False
                        break
                    score_total += score

                if not ok:
                    continue

            rows.append((score_total, item))
            rows_cache.append(item)

        result = []
        if self.need_sort():
            result = [line for score, line in heapq.nlargest(self.max_candidates, rows)]
        else:
            result = [line for score, line in rows]
            if len(result) > self.max_candidates:
                result = result[:self.max_candidates]

        self.cache.set_candidates(self.inputs, rows_cache)
        self.cache.set_result(self.inputs, result)

        return result

    def search(self, inputs):
        if not self.enable:
            return []

        self.inputs = inputs
        self.parse_inputs()

        if not self.is_input_length_ok():
            return [{'kind': 'none', 'word': 'Please input at least %d chars' % self.min_input}]

        if self.need_clear_cache():
            self.cache.clear()

        if self.need_gather_candidates():
           self.gather_candidates()

        if self.is_input_empty():
            rows = self.candidates if len(self.candidates) <= self.max_candidates else self.candidates[:self.max_candidates]
            # print("input empty rows count:%d" % len(rows))
            return self.format(rows)

        rows = self.filter_candidates()

        return self.format(rows)

    def calc_score_by_name_with_dir(self, reprog, filename, dirname):
        result = reprog.search(filename)
        if result:
            score = result.start() * 2
            score = score + result.end() - result.start() + 1
            score = score + ( len(filename) + 1 ) / 100.0
            score = score + ( len(dirname) + 1 ) / 1000.0
            return 1000.0 / score

        return 0
