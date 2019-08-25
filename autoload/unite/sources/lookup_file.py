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
        pass

    def get_filelist_path(self):
        return lookup_get_cache_path("filelist")

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
            'word': row[0], 
            'abbr': '[F] %s' % lookup_get_name_dir_abbr(row),
            'kind': 'file',
            'group': 'file',
            'action__path': lookup_get_name_dir_path(row),
            } for row in rows]

# def UnitePyLookupFileLoad():
#     file_path = vim.eval('s:file_path')
#     lookupfile.load_filelist(file_path)

# def UnitePyLookupFileGetResult():
#     start_time = time.time()
#     inputs = vim.eval('s:inputs').strip()
#
#     rows_file = lookupfile.search(lookupfile.files, inputs, 20, True)
#
#     lines.extend([{
#         'word': row[0],
#         'abbr': lookupfile_get_path(row).replace('\\', '/'),
#         'kind': 'file',
#         'group': 'file',
#         'action__path': lookupfile_get_path(row),
#         } for row in rows_file if row not in rows_mru ])
#
#     vim.command('let s:rez = {0}'.format(lines))
#
#     end_time = time.time()
#     vim.command('echo "search %s cost %.1f ms, return %d rows"' % (inputs, (end_time - start_time)*1000, len(lines)))

# def UnitePyLookupFileGetFileList():
#     wildignore = vim.eval("g:lookupfile_WildIgnore")
#     linksflag = vim.eval("g:lookupfile_FollowLinks")
#
#     lookupfile.update_filelist(dir_path, file_path, wildignore, linksflag)

