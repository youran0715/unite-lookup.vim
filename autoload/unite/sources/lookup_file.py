#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import time
import fnmatch
import heapq

class LookupFile(object):
    def __init__(self):
        self.files = []
        self.mrus = []
        self.caches = {}
        self._escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])

    def load_filelist(self, file_path):
        with open(file_path,'r') as f:
            lines = f.read().splitlines()
            self.files = []
            self.caches = {}
            for line in lines:
                items = line.split("\t")
                fileItem = (items[0], items[1])
                self.files.append(fileItem)
            f.close()

    def save_filelist(self, file_path, file_list):
        with open(file_path, 'w') as f:
            self.files = []
            self.caches = {}
            for item in file_list:
                try:
                    fileItem = (os.path.basename(item) , os.path.dirname(os.path.relpath(item)))
                    self.files.append(fileItem)
                    f.write("%s\t%s\n" % (fileItem))
                except UnicodeEncodeError:
                    continue

            f.close()

    def update_filelist(self, dir_path, file_path, wildignore, linksflag):
        start_time = time.time()
        file_list = []
        for dir_path, dirs, files in os.walk(dir_path, followlinks = False if linksflag == '0' else True):
            dirs[:] = [i for i in dirs if True not in (fnmatch.fnmatch(i,j)
                       for j in wildignore['dir'])]
            for name in files:
                if True not in (fnmatch.fnmatch(name, j) for j in wildignore['file']):
                    file_list.append(os.path.join(dir_path,name))
                if time.time() - start_time > 120:
                    self.save_filelist(file_path, file_list)
                    return

        self.save_filelist(file_path, file_list)

    def filename_score(self, reprog, filename, dirname):
        result = reprog.search(filename)
        if result:
            score = result.start() * 2
            score = score + result.end() - result.start() + 1
            score = score + ( len(filename) + 1 ) / 100.0
            score = score + ( len(dirname) + 1 ) / 1000.0
            return 1000.0 / score

        return 0

    def dir_score(self, reprog, line):
        result = reprog.search(line)
        if result:
            score = result.end() - result.start() + 1
            score = score + ( len(line) + 1 ) / 100.0
            return 1000.0 / score

        return 0

    def get_regex_prog(self, kw, islower):
        searchkw = kw.lower() if islower else kw

        regex = ''
        # Escape all of the characters as necessary
        escaped = [self._escape.get(c, c) for c in searchkw]

        if len(searchkw) > 1:
            regex = ''.join([c + "[^" + c + "]*" for c in escaped[:-1]])
        regex += escaped[-1]

        return re.compile(regex)

    def contain_upper(self, kw):
        prog = re.compile('[A-Z]+')
        return prog.search(kw)

    def is_search_lower(self, kw):
        return False if self.contain_upper(kw) else True

    def do_search(self, rows, progs, islower):
        res = []

        for row in rows:
            filename = row[0].lower() if islower else row[0]
            dir = row[1].lower() if islower else row[1]
            scoreTotal = 0.0
            for (prog, tp) in progs:
                score = 0
                if tp == "name":
                    score = self.filename_score(prog, filename, dir)
                else:
                    score = self.dir_score(prog, dir)
                if score == 0:
                    scoreTotal = 0
                    break
                else:
                    scoreTotal += score

            if scoreTotal != 0:
                res.append((scoreTotal, row))

        return res

    def search(self, rows, inputs, limit, is_cache):
        if inputs == "" or inputs == ";":
            return rows if len(rows) <= limit else rows[:limit]

        rowsWithScore = []
        if is_cache and inputs in self.caches:
            rowsWithScore = self.caches[inputs]
        else:
            if is_cache and len(inputs) > 1:
                cacheInputs = inputs[:-1]
                if cacheInputs in self.caches:
                    rowsWithScore = self.caches[cacheInputs]
                    rows = [line for score, line in rowsWithScore]

            islower = self.is_search_lower(inputs)

            kwsAndDirs = inputs.split(';')
            inputs_file = (kwsAndDirs[0] if len(kwsAndDirs) > 0 else "").strip()
            inputs_dir  = (kwsAndDirs[1] if len(kwsAndDirs) > 1 else "").strip()

            progs = [(self.get_regex_prog(kw, islower), "name") for kw in inputs_file.split() if kw != ""]
            progs.extend([(self.get_regex_prog(kw, islower), "dir") for kw in inputs_dir.split() if kw != ""])

            rowsWithScore = self.do_search(rows, progs, islower)
            # save in cache
            if is_cache and len(progs) > 0:
                self.caches[inputs] = rowsWithScore

        return [line for score, line in heapq.nlargest(limit, rowsWithScore)]

    def add_mru(self, path):
        file_name = os.path.basename(path)
        dir_name = os.path.dirname(os.path.relpath(path))

        item = (file_name, dir_name)
        # print("item:%s" % str(item))
        try:
            self.mrus.remove(item)
        except Exception as e:
            pass
        # print("before")
        # print(mrus)
        self.mrus.insert(0, item)
        self.mrus = self.mrus if len(self.mrus) < 30 else self.mrus[0:30]
        # print("after")
        # print(mrus)

lookupfile = LookupFile()

def lookupfile_get_path(row):
    return os.path.join(row[1], row[0])

def UnitePyLookupFileAddMru():
    path = vim.eval('s:buf_path')
    if os.path.abspath(path).startswith(os.getcwd()):
        lookupfile.add_mru(path)

def UnitePyLookupFileCleanMrus():
    lookupfile.mrus = []

def UnitePyLookupFileSaveMrus():
    file_path = vim.eval('s:file_path')
    with open(file_path, 'w') as f:
        for mru in lookupfile.mrus:
            # vim.command('echo "' + str(mru) + '"')
            try:
                f.write("%s\n" % (lookupfile_get_path(mru)))
            except UnicodeEncodeError:
                continue

        f.close()

def UnitePyLookupFileLoadMrus():
    file_path = vim.eval('s:file_path')
    with open(file_path,'r') as f:
        lines = f.read().splitlines()
        lookupfile.mrus = []
        for line in lines:
            item = (os.path.basename(line), os.path.dirname(line))
            lookupfile.mrus.append(item)
        f.close()

def UnitePyLookupFileLoad():
    file_path = vim.eval('s:file_path')
    lookupfile.load_filelist(file_path)

def UnitePyLookupFileGetResult():
    start_time = time.time()
    inputs = vim.eval('s:inputs').strip()

    rows_file = lookupfile.search(lookupfile.files, inputs, 20, True)
    rows_mru = lookupfile.search(lookupfile.mrus,  inputs, 20, False)

    # print(lookupfile.mrus)

    lines = [{
        'word': row[0],
        'abbr': ('[M] %s' % lookupfile_get_path(row)).replace('\\', '/'),
        'kind': 'file',
        'group': 'file',
        'action__path': lookupfile_get_path(row),
        } for row in rows_mru]

    lines.extend([{
        'word': row[0],
        'abbr': lookupfile_get_path(row).replace('\\', '/'),
        'kind': 'file',
        'group': 'file',
        'action__path': lookupfile_get_path(row),
        } for row in rows_file if row not in rows_mru ])

    vim.command('let s:rez = {0}'.format(lines))

    end_time = time.time()
    vim.command('echo "search %s cost %.1f ms, return %d rows"' % (inputs, (end_time - start_time)*1000, len(lines)))

def UnitePyLookupFileGetFileList():
    dir_path = vim.eval('s:dir_path')
    file_path = vim.eval('s:file_path')
    wildignore = vim.eval("g:lookupfile_WildIgnore")
    linksflag = vim.eval("g:lookupfile_FollowLinks")

    lookupfile.update_filelist(dir_path, file_path, wildignore, linksflag)

def main():
    wildignore={"file":[], "dir":[]}
    filepath = "filelist"
    # update_filelist("C:\\Users\\WuHong\\vimfiles", filepath, wildignore, "0")
    lookupfile.update_filelist("/home/wuhong/gohome/src/hello", filepath, wildignore, "0")
    lookupfile.load_filelist(filepath)
    print(files)
    # res = search(files, "min", 10)
    res = lookupfile.search(files, "w;wor", 10)
    print(res)

# main()

