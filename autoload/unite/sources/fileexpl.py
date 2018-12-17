#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import sys
import time
import os.path
import fnmatch
import locale

lfEval = vim.eval

if sys.version_info >= (3, 0):
    # vim.command('echomsg "use python3"')
    def lfEncode(str):
        return str

    def lfDecode(str):
        return str
else: # python 2.x
    def lfEncode(str):
        try:
            if locale.getdefaultlocale()[1] is None:
                return str
            else:
                return str.decode(locale.getdefaultlocale()[1]).encode(lfEval("&encoding"))
        except ValueError:
            return str
        except UnicodeDecodeError:
            return str

    def lfDecode(str):
        try:
            if locale.getdefaultlocale()[1] is None:
                return str
            else:
                return str.decode(lfEval("&encoding")).encode(
                        locale.getdefaultlocale()[1])
        except UnicodeDecodeError:
            return str

def writelist2file(file_path, file_list):
    with open(file_path, 'w') as f:
        for item in file_list:
            f.write("%s\n" % item)
        f.close()

def UnitePyGetFileList():
    dir_path = vim.eval('s:dir_path')
    file_path = vim.eval('s:file_path')
    # vim.command('echomsg "dir_path:%s"' % dir_path)
    # dir_path = "./"
    start_time = time.time()
    wildignore = lfEval("g:lookupfile_WildIgnore")
    # wildignore = {"dir":[], "file":[]}
    file_list = []
    for dir_path, dirs, files in os.walk(dir_path, followlinks = False
            if lfEval("g:lookupfile_FollowLinks") == '0' else True):
        dirs[:] = [i for i in dirs if True not in (fnmatch.fnmatch(i,j)
                   for j in wildignore['dir'])]
        for name in files:
            if True not in (fnmatch.fnmatch(name, j)
                            for j in wildignore['file']):
                file_list.append(lfEncode(os.path.join(dir_path,name)))
            # return
            if time.time() - start_time > 120:
                writelist2file(file_path, file_list)
                # vim.command('echoerr "FileList:%s"' % ','.join(file_list))
                # vim.command('let s:file_list = [%s]' % ','.join(file_list))
                return
                # return file_list
    # vim.command('echomsg "%s"' % ','.join(file_list))
    # return file_list
    writelist2file(file_path, file_list)
    # vim.command('let s:file_list = [%s]' % ','.join(file_list))

def UnitePyGetFileListTest():
    # dir_path = vim.eval('s:dir_path')
    # vim.command('echomsg "dir_path:%s"' % dir_path)
    dir_path = "./"
    start_time = time.time()
    wildignore = {"dir":[], "file":[]}
    file_list = []
    for dir_path, dirs, files in os.walk(dir_path, followlinks = False):
        dirs[:] = [i for i in dirs if True not in (fnmatch.fnmatch(i,j)
                   for j in wildignore['dir'])]
        for name in files:
            if True not in (fnmatch.fnmatch(name, j)
                            for j in wildignore['file']):
                file_list.append(lfEncode(os.path.join(dir_path,name)))
            if time.time() - start_time > float(1000):
                # vim.command('let s:file_list = [%s]' % ','.join(file_list))
                return
                # return file_list
    print(file_list)
    # return file_list
    # vim.command('let s:file_list = [%s]' % ','.join(file_list))

# UnitePyGetFileListTest()
