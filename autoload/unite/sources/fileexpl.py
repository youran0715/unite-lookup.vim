#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import sys
import time
import os.path
import fnmatch

lfEval = vim.eval

def saveFileList(file_path, file_list):
    with open(file_path, 'w') as f:
        for item in file_list:
            f.write("%s\n" % os.path.relpath(item))
        f.close()

def updateFileList(dir_path, file_path, wildignore, linksflag):
    start_time = time.time()
    file_list = []
    for dir_path, dirs, files in os.walk(dir_path, followlinks = False
            if linksflag == '0' else True):
        dirs[:] = [i for i in dirs if True not in (fnmatch.fnmatch(i,j)
                   for j in wildignore['dir'])]
        for name in files:
            if True not in (fnmatch.fnmatch(name, j)
                            for j in wildignore['file']):
                file_list.append(os.path.join(dir_path,name))
            if time.time() - start_time > 120:
                writelist2file(file_path, file_list)
                return

    saveFileList(file_path, file_list)

def UnitePyGetFileList():
    dir_path = vim.eval('s:dir_path')
    file_path = vim.eval('s:file_path')
    wildignore = lfEval("g:lookupfile_WildIgnore")
    linksflag = lfEval("g:lookupfile_FollowLinks")

    updateFileList(dir_path, file_path, wildignore, linksflag)

