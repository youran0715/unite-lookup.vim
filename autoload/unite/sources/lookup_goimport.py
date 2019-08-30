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
        self.cache_path = lookup_get_cache_path('goimport', False)

    def do_unite_init(self):
        self.enable = self.get_buffer_filetype() == ".go"

    def do_gather_candidates(self):
        try:
            executor = AsyncExecutor()
            result = executor.execute("gopkgs")
            return [line for line in result if line is not None]
        except Exception as e:
            return []

    def do_format(self, rows):
        return [{'word': row, 'kind':'goimport', 'abbr': '[G] %s' % row} for row in rows]

