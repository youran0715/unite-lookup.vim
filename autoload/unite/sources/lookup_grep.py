#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re
import os
import vim
import platform;

isWindows = platform.system() == "Windows"

def gather_candidates():
    inputs = vim.eval("s:inputs")
    limit = 100
    rows = do_gather_candidates(inputs, limit)
    # rows = do_gather_candidates("can", 10)

    # print(rows)
    vimrez = [str(row).replace('\\', '\\\\').replace("'", "\'") for row in rows]

    vim.command('let s:rez = [%s]' % ','.join(vimrez))

cache = {}

def do_gather_candidates(inputs, limit):
    kws = re.split('\s', inputs)

    if inputs == "" or len(kws) < 1:
        return [{'word': 'Please input keyword'}]

    if len(kws[0]) <= 2:
        return [{'word': inputs, 'abbr': 'Please input at least 3 chars'}]

    global cache
    output = []
    # print(kws[0][:-1])
    if inputs in cache:
        output = cache[inputs]
    elif inputs[:-1] in cache:
        output = cache[inputs[:-1]]
    else:
        args = get_args(kws[0])
        output = run_command_linux(args, os.getcwd())

    rows = []
    rowsMatch = []
    progs = []
    for kw in kws:
        if kw == "":
            continue
        progs.append(get_regex_prog(kw, True))

    for line in output:
        if line.strip() == "":
            continue
        # print("line:%s" % line)
        format = __candidate(line, progs)
        if format is not None:
            rowsMatch.append(line)
            if len(rows) <= limit:
                rows.append(format)

    cache[inputs] = rowsMatch

    return rows

_escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])
def get_regex_prog(kw, islower):
    searchkw = kw.lower() if islower else kw

    regex = ''
    escaped = [_escape.get(c, c) for c in searchkw]

    if len(searchkw) > 1:
        regex = ''.join([c + "[^" + c + "]*" for c in escaped[:-1]])
    regex += escaped[-1]

    return re.compile(regex)

def __candidate(line, progs):
    try:
        items = line.split(':')
        if len(items) < 4:
            return None

        path = items[0].strip()
        row = items[1]
        col = items[2]
        body = ''.join(items[3::]).replace('\r', '').replace('\\', '').strip()

        bodylower = body.lower()
        for prog in progs:
            result = prog.search(bodylower)
            if not result:
                return None

        return {
                'word': body,
                "abbr": '{0}:{1}: {2}'.format(
                    path,
                    row,
                    body
                    ),
                'kind': 'jump_list',
                'action__path': path,
                'action__line': int(row),
                'action__col': int(col),
                'action__text': body
                }
    except TypeError as e:
        return None

def get_args_rg(inputs):
    args = ['rg', '-S', '--vimgrep', '--no-heading', inputs,]
    return args

def get_args_ag(inputs):
    args = ['ag', '-i', '--vimgrep', inputs]
    return args

def get_args_ack(inputs):
    args = ['ack', '-H', '-S', '--nopager', '--nocolor' '--nogroup', '--column', inputs,]
    return args

def get_args_git(inputs):
    args = ['git', '--no-pager', 'grep', '-n', '--no-color', '-i', inputs, ]
    return args

def get_args(inputs):
    if isWindows:
        return get_args_ag(inputs)
    else:
        return get_args_rg(inputs)

def run_command_linux(command, cwd, encode='utf8'):
    try:
        process = subprocess.run(command,
                cwd=cwd,
                stdout=subprocess.PIPE)

        return process.stdout.decode(encode).split('\n')
    except Exception as e:
        return []

def run_command_windows(command, cwd, encode='utf8'):
    try:
        filename = 'ripgrep.txt'
        cmd = ' '.join(command) + ' > ' + filename

        os.system(cmd)

        with open(filename,'r') as f:
            lines = f.read().splitlines()
            f.close()
            os.remove(filename)
            return lines

        return []
    except Exception as e:
        return []

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def main():
    res = do_gather_candidates("can", 100)
    # print(res)
    pass

if __name__ == "__main__":
    # main()
    pass
