#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import os
from lookup import *
from lookup_filter_filename import *
from lookup_utils import *

class LookupEdit(Lookup):
    def __init__(self):
        super(LookupEdit, self).__init__()
        self.filter = LookupFilterFilename()
        self.name = "edit"
        self.max_count = 1
        self.is_init_reload = True

    def do_gather_candidates(self, is_redraw):
        path = self.buffer
        if not os.path.isfile(path):
            return []

        file_name = os.path.basename(path)
        dir_name = os.path.dirname(os.path.relpath(path))
        return [(file_name, dir_name)]

    def format(self, rows):
        return [{ 
            'word': lookup_get_name_dir_abs_path(row), 
            'abbr': '[E] %s' % lookup_get_name_dir_abbr(row),
            'kind': 'file',
            'group': 'file',
            'action__path': lookup_get_name_dir_path(row),
            } for row in rows]
