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
        self.is_redraw = False #有缓存文件
        self.enable_filter_path = True

    def get_filelist_path(self):
        return lookup_get_cache_path("filelist")

    def do_unite_init(self):
        candidates = []
        if not self.is_redraw:
            return

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
            candidates = self.do_gather_candidates()

        self.candidates = candidates
        self.is_redraw = False

    def do_gather_candidates(self):
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

    def save(self, candidates):
        with open(self.get_filelist_path(), 'w') as f:
            for item in candidates:
                try:
                    f.write("%s\t%s\n" % item)
                except UnicodeEncodeError:
                    continue

            f.close()

    def do_format(self, rows):
        return [{ 
            'word': lookup_get_name_dir_abs_path(row), 
            'abbr': '[F] %s' % lookup_get_name_dir_abbr(row),
            'kind': 'file',
            'group': 'file',
            'action__path': lookup_get_name_dir_path(row),
            } for row in rows]
