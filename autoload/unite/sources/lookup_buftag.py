#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re
import os
import sys
import os.path
import tempfile
import itertools
import multiprocessing
import subprocess
from lookup import *
from lookup_filter_path import *
from asyncExecutor import AsyncExecutor

class LookupBufTag(Lookup):
    def __init__(self):
        super(LookupBufTag, self).__init__()
        self.filter = LookupFilterTag()
        self.name = "buftag"
        self._executor = []

    def need_clear_cache(self):
        return True

    def do_gather_candidates(self):
        buffer = vim.current.buffer
        self._ctags = lfEval("g:ctags")
        if not buffer.name or lfEval("bufloaded(%d)" % buffer.number) == '0':
            return []

        if lfEval("getbufvar(%d, '&filetype')" % buffer.number) == "cpp":
            extra_options = "--language-force=C++ --c++-kinds=+p"
        elif lfEval("getbufvar(%d, '&filetype')" % buffer.number) == "c":
            extra_options = "--c-kinds=+p"
        elif lfEval("getbufvar(%d, '&filetype')" % buffer.number) == "python":
            extra_options = "--language-force=Python"
        else:
            extra_options = ""

        executor = AsyncExecutor()
        self._executor.append(executor)
        if buffer.options["modified"] == True:
            if sys.version_info >= (3, 0):
                tmp_file = partial(tempfile.NamedTemporaryFile, encoding=lfEval("&encoding"))
            else:
                tmp_file = tempfile.NamedTemporaryFile

            with tmp_file(mode='w+', suffix='_'+os.path.basename(buffer.name), delete=False) as f:
                for line in buffer[:]:
                    f.write(line + '\n')
                file_name = f.name
            # {tagname}<Tab>{tagfile}<Tab>{tagaddress}[;"<Tab>{tagfield}..]
            # {tagname}<Tab>{tagfile}<Tab>{tagaddress};"<Tab>{kind}<Tab>{scope}
            cmd = '{} -n -u --fields=Ks {} -f- "{}"'.format(self._ctags, extra_options, lfDecode(file_name))
            result = executor.execute(cmd, cleanup=partial(os.remove, file_name))
        else:
            cmd = '{} -n -u --fields=Ks {} -f- "{}"'.format(self._ctags, extra_options, lfDecode(buffer.name))
            result = executor.execute(cmd)

        return result

    def format(self, rows):
        return [{'word': row, 'kind':'goimport', 'abbr': '[T] %s' % row} for row in rows]
