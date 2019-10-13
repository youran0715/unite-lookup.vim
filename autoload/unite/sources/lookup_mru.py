#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import os
from lookup import *
from lookup_filter_filename import *
from lookup_utils import *

class LookupMru(Lookup):
    def __init__(self):
        super(LookupMru, self).__init__()
        self.filter = LookupFilterFilename()
        self.name = "mru"
        self.max_count = 30
        self.max_candidates = 15
        self.enable_filter_path = True

    def do_unite_init(self):
        self.is_redraw = True

    def get_mru_path(self):
        return lookup_get_cache_path("mru")

    def do_gather_candidates(self):
        edit_path = os.path.abspath(self.buffer)
        return [item for item in self.candidates if lookup_get_name_dir_abs_path(item) != edit_path and os.path.isfile(item)]

    def load(self):
        candidates = []
        try:
            with open(self.get_mru_path(),'r') as f:
                lines = f.read().splitlines()
                for line in lines:
                    item = (os.path.basename(line), os.path.dirname(line))
                    candidates.append(item)
                f.close()
        except Exception as e:
            pass

        self.candidates = candidates

    def save(self):
        with open(self.get_mru_path(), 'w') as f:
            for mru in self.candidates:
                try:
                    f.write("%s\n" % lookup_get_name_dir_path(mru))
                except UnicodeEncodeError:
                    continue

            f.close()

    def clean(self):
        self.candidates = []

    def add(self, path):
        file_name = os.path.basename(path)
        dir_name = os.path.dirname(os.path.relpath(path))

        item = (file_name, dir_name)
        try:
            self.candidates.remove(item)
        except Exception as e:
            pass
        self.candidates.insert(0, item)
        self.candidates = self.candidates if len(self.candidates) < self.max_count else self.candidates[0:self.max_count]

    def do_format(self, rows):
        return [{ 
            'word': lookup_get_name_dir_abs_path(row), 
            'abbr': '[M] %s' % lookup_get_name_dir_abbr(row),
            'kind': 'file',
            'group': 'file',
            'action__path': lookup_get_name_dir_path(row),
            } for row in rows]
