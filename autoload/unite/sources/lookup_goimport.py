#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import subprocess
from lookup import *
from lookup_filter_path import *

class LookupGoimport(Lookup):
    def __init__(self):
        super(LookupGoimport, self).__init__()
        self.filter = LookupFilterPath()
        self.kind = "Goimport"
        pass

    def enable_filetype(self, ft):
        if ft != "go":
            self.enable = False

    def do_gather_candidates(self):
        try:
            output = subprocess.run(['gopkgs'], stdout=subprocess.PIPE, check=True)
            return output.stdout.decode('utf-8').splitlines()
        except subprocess.CalledProcessError as err:
            denite.util.error(self.vim, "command returned invalid response: " + str(err))
            return []

    def format(self, rows):
        return [{'word': row, 'abbr': '[G] %s' % row} for row in rows]
