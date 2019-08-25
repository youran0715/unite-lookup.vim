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
        self.kind = "file"
        self.mru_path = ""
        self.max_count = 100

        pass

    def load(self):
        with open(self.mru_path,'r') as f:
            lines = f.read().splitlines()
            self.candidates = []
            for line in lines:
                item = (os.path.basename(line), os.path.dirname(line))
                self.candidates.append(item)
            f.close()
        print("mrus:", self.candidates)
        pass

    def save(self):
        with open(self.mru_path, 'w') as f:
            for mru in self.candidates:
                try:
                    f.write("%s\n" % lookup_get_name_dir_path(mru))
                except UnicodeEncodeError:
                    continue

            f.close()

    def clean(self):
        self.candidates = []

    def add(self, path):
        if not os.path.abspath(path).startswith(os.getcwd()):
            return

        file_name = os.path.basename(path)
        dir_name = os.path.dirname(os.path.relpath(path))

        item = (file_name, dir_name)
        try:
            self.candidates.remove(item)
        except Exception as e:
            pass
        self.candidates.insert(0, item)
        self.candidates = self.candidates if len(self.candidates) < self.max_count else self.mrus[0:self.max_count]

    def do_gather_candidates(self):
        return self.candidates

    def format(self, rows):
        return [{ 
            'word': row[0], 
            'abbr': '[M] %s' % lookup_get_name_dir_abbr(row),
            'kind': 'file',
            'group': 'file',
            'action__path': lookup_get_name_dir_path(row),
            } for row in rows]
