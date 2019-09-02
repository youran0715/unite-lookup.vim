#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import subprocess
from lookup import *
from lookup_utils import *
from lookup_filter_path import *
from asyncExecutor import AsyncExecutor

class LookupGoimport(Lookup):
    def __init__(self):
        super(LookupGoimport, self).__init__()
        self.filter = LookupFilterPath()
        self.name = "goimport"
        self.cache_path = ".goimport"

    def do_unite_init(self):
        self.cache_path = lookup_get_cache_path('goimport', False)
        self.enable = self.get_buffer_filetype() == ".go"
        if not self.enable:
            return

        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path,'r') as f:
                    candidates = f.read().splitlines()
                    f.close()
            except Exception as e:
                raise e
        else:
            candidates = self.do_gather_candidates()

        self.candidates = candidates
        self.is_redraw = False

    def do_gather_candidates(self):
        try:
            executor = AsyncExecutor()
            result = executor.execute("gopkgs")
            rows = [line for line in result if line is not None]
            self.save(rows)
            return rows
        except Exception as e:
            return []

    def save(self, candidates):
        with open(self.cache_path, 'w') as f:
            for item in candidates:
                try:
                    f.write("%s\n" % item)
                except UnicodeEncodeError:
                    continue

            f.close()

    def do_format(self, rows):
        return [{'word': row, 'kind':'goimport', 'abbr': '[G] %s' % row} for row in rows]

