#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import subprocess
from lookup import *
from lookup_filter_path import *
from asyncExecutor import AsyncExecutor

class LookupGoimport(Lookup):
    def __init__(self):
        super(LookupGoimport, self).__init__()
        self.filter = LookupFilterPath()
        self.name = "goimport"

    def need_gather_candidates(self):
        return not self.is_load_candidates and self.get_buffer_filetype() == ".go"

    def do_gather_candidates(self, is_redraw):
        try:
            executor = AsyncExecutor()
            result = executor.execute("gopkgs")
            output = [line for line in result if line is not None]
            return output
        except Exception as e:
            return []

    def do_gather_candidates_old(self, is_redraw):
        try:
            output = subprocess.run(['gopkgs'], stdout=subprocess.PIPE, check=True)
            return output.stdout.decode('utf-8').splitlines()
        except subprocess.CalledProcessError as err:
            denite.util.error(self.vim, "command returned invalid response: " + str(err))
            return []

    def format(self, rows):
        return [{'word': row, 'kind':'goimport', 'abbr': '[G] %s' % row} for row in rows]

