#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import time
import fnmatch
import heapq
from lookup_filter_filename import *
from lookup_utils import *
from lookup import *

class LookupFile(Lookup):
    def __init__(self):
        super(LookupFile, self).__init__()
        self.filter = LookupFilterFilename()
        self.wildignore = {'dir':[], 'file': []}
        self.followlinks = False
        self.name = "file"
        pass

    def get_filelist_path(self):
        return lookup_get_cache_path("filelist")

    def do_redraw(self):
        self.candidates = self.update()

    def do_gather_candidates(self):
        candidates = []
        if os.path.exists(self.get_filelist_path()):
            try:
                with open(self.get_filelist_path(),'r') as f:
                    lines = f.read().splitlines()
                    for line in lines:
                        items = line.split("\t")
                        candidates.append((items[0], items[1]))
                    f.close()
            except Exception as e:
                raise e
        else:
            candidates = self.update()
        return candidates

    def save(self, candidates):
        with open(self.get_filelist_path(), 'w') as f:
            for item in candidates:
                try:
                    f.write("%s\t%s\n" % item)
                except UnicodeEncodeError:
                    continue

            f.close()

    def update(self):
        start_time = time.time()
        candidates = []
        dir_path = os.getcwd()
        for dir_path, dirs, files in os.walk(dir_path, self.followlinks):
            dirs[:] = [i for i in dirs if True not in (fnmatch.fnmatch(i,j)
                       for j in self.wildignore['dir'])]
            for name in files:
                if True not in (fnmatch.fnmatch(name, j) for j in self.wildignore['file']):
                    candidates.append((name, dir_path))
                if time.time() - start_time > 120:
                    self.save()
                    return

        self.save(candidates)
        return candidates

    def format(self, rows):
        return [{ 
            'word': lookup_get_name_dir_path(row), 
            'abbr': '[F] %s' % lookup_get_name_dir_abbr(row),
            'kind': 'file',
            'group': 'file',
            'action__path': lookup_get_name_dir_path(row),
            } for row in rows]
