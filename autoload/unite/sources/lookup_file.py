#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import time
import fnmatch
import heapq

files = []
mrus = []
caches = {}
def load_filelist(file_path):
    with open(file_path,'r') as f:
        lines = f.read().splitlines()
        global files
        global caches
        files = []
        caches = {}
        for line in lines:
            items = line.split("\t")
            fileItem = (items[0], items[1])
            files.append(fileItem)
        f.close()

def save_filelist(file_path, file_list):
    with open(file_path, 'w') as f:
        global files
        files = []
        caches = {}
        for item in file_list:
            try:
                fileItem = (os.path.basename(item) , os.path.dirname(os.path.relpath(item)))
                files.append(fileItem)
                f.write("%s\t%s\n" % (fileItem))
            except UnicodeEncodeError:
                continue

        f.close()

def update_filelist(dir_path, file_path, wildignore, linksflag):
    start_time = time.time()
    file_list = []
    for dir_path, dirs, files in os.walk(dir_path, followlinks = False if linksflag == '0' else True):
        dirs[:] = [i for i in dirs if True not in (fnmatch.fnmatch(i,j)
                   for j in wildignore['dir'])]
        for name in files:
            if True not in (fnmatch.fnmatch(name, j) for j in wildignore['file']):
                file_list.append(os.path.join(dir_path,name))
            if time.time() - start_time > 120:
                save_filelist(file_path, file_list)
                return

    save_filelist(file_path, file_list)

def filename_score(reprog, filename, dirname):
    result = reprog.search(filename)
    if result:
        score = result.start() * 2
        score = score + result.end() - result.start() + 1
        score = score + ( len(filename) + 1 ) / 100.0
        score = score + ( len(dirname) + 1 ) / 1000.0
        return 1000.0 / score

    return 0

def dir_score(reprog, line):
    result = reprog.search(line)
    if result:
        score = result.end() - result.start() + 1
        score = score + ( len(line) + 1 ) / 100.0
        return 1000.0 / score

    return 0

_escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])
def get_regex_prog(kw, islower):
    searchkw = kw.lower() if islower else kw

    regex = ''
    # Escape all of the characters as necessary
    escaped = [_escape.get(c, c) for c in searchkw]

    if len(searchkw) > 1:
        regex = ''.join([c + "[^" + c + "]*" for c in escaped[:-1]])
    regex += escaped[-1]

    return re.compile(regex)

def contain_upper(kw):
    prog = re.compile('[A-Z]+')
    return prog.search(kw)

def is_search_lower(kw):
    return False if contain_upper(kw) else True

def do_search_file(rows, progs, limit, islower):
    res = []

    for row in rows:
        line = row[0].lower() if islower else row[0]
        scoreTotal = 0.0
        for prog in progs:
            score = filename_score(prog, line, row[1])
            if score == 0:
                scoreTotal = 0
                break
            else:
                scoreTotal += score

        if scoreTotal != 0:
            res.append((scoreTotal, row))

    return [line for score, line in heapq.nlargest(limit, res)]

def do_search_dir(rows, progs, limit, islower):
    res = []

    for row in rows:
        line = row[1].lower() if islower else row[1]
        scoreTotal = 0.0
        for prog in progs:
            score = dir_score(prog, line)
            if score == 0:
                scoreTotal = 0
                break
            else:
                scoreTotal += score

        if scoreTotal != 0:
            res.append((scoreTotal, row))

    return [line for score, line in heapq.nlargest(limit, res)]

def search(rows, inputs, limit):
    islower = is_search_lower(inputs)

    kwsAndDirs = inputs.split(';')
    inputs_file = (kwsAndDirs[0] if len(kwsAndDirs) > 0 else "").strip()
    inputs_dir  = (kwsAndDirs[1] if len(kwsAndDirs) > 1 else "").strip()

    fprogs = [get_regex_prog(kw, islower) for kw in inputs_file.split() if kw != ""]
    dprogs = [get_regex_prog(kw, islower) for kw in inputs_dir.split() if kw != ""]

    rez = []
    if len(fprogs) > 0:
        rez = do_search_file(rows, fprogs, limit, islower)
    else:
        rez = rows

    if len(dprogs) > 0:
        rez = do_search_dir(rez, dprogs, limit, islower)

    if len(rez) > limit:
        return rez[:limit]

    return rez

def add_mru(path):
    file_name = os.path.basename(path)
    dir_name = os.path.dirname(os.path.relpath(path))

    global mrus
    item = (file_name, dir_name)
    # print("item:%s" % str(item))
    try:
        mrus.remove(item)
    except Exception as e:
        pass
    # print("before")
    # print(mrus)
    mrus.insert(0, item)
    mrus = mrus if len(mrus) < 30 else mrus[0:30]
    # print("after")
    # print(mrus)

def get_path(row):
    return ('%s%s%s' % (row[1], '/' if row[1] != "" else '', row[0]))

def UnitePyAddMru():
    path = vim.eval('s:buf_path')
    if os.path.abspath(path).startswith(os.getcwd()):
        add_mru(path)

def UnitePySaveMrus():
    file_path = vim.eval('s:file_path')
    with open(file_path, 'w') as f:
        global mrus
        for mru in mrus:
            # vim.command('echo "' + str(mru) + '"')
            try:
                f.write("%s\n" % (get_path(mru)))
            except UnicodeEncodeError:
                continue

        f.close()

def UnitePyLoadMrus():
    file_path = vim.eval('s:file_path')
    with open(file_path,'r') as f:
        lines = f.read().splitlines()
        global mrus
        mrus = []
        for line in lines:
            item = (os.path.basename(line), os.path.dirname(line))
            mrus.append(item)
        f.close()

def UnitePyLoad():
    file_path = vim.eval('s:file_path')
    load_filelist(file_path)

def UnitePyGetResult():
    start_time = time.time()
    inputs = vim.eval('s:inputs')

    global files
    global mrus
    rows_file = search(files, inputs, 20)
    rows_mru = search(mrus,  inputs, 20)

    # print(mrus)

    lines = [{
        'word': row[0],
        'abbr': ('[M] %s' % get_path(row)),
        'kind': 'file',
        'group': 'file',
        'action__path': get_path(row),
        } for row in rows_mru]

    lines.extend([{
        'word': row[0],
        'abbr': get_path(row),
        'kind': 'file',
        'group': 'file',
        'action__path': get_path(row),
        } for row in rows_file if row not in rows_mru ])

    vimrez = [str(line).replace('\\', '\\\\').replace('"', '\\"') for line in lines]
    vim.command('let s:rez = [%s]' % ','.join(vimrez))

    end_time = time.time()
    vim.command('echo "search %s cost %.1f ms"' % (inputs, (end_time - start_time)*1000))

def UnitePyGetFileList():
    dir_path = vim.eval('s:dir_path')
    file_path = vim.eval('s:file_path')
    wildignore = vim.eval("g:lookupfile_WildIgnore")
    linksflag = vim.eval("g:lookupfile_FollowLinks")

    update_filelist(dir_path, file_path, wildignore, linksflag)

def main():
    wildignore={"file":[], "dir":[]}
    filepath = "filelist"
    # update_filelist("C:\\Users\\WuHong\\vimfiles", filepath, wildignore, "0")
    update_filelist("/home/wuhong/gohome/src/hello", filepath, wildignore, "0")
    load_filelist(filepath)
    print(files)
    # res = search(files, "min", 10)
    res = search(files, "w;wor", 10)
    print(res)

# main()

