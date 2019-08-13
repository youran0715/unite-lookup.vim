#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re
import os
import vim

cache = {}

def gather_candidates():
    inputs = vim.eval("s:inputs")
    limit = 100
    rows = do_gather_candidates(inputs, limit)

    # print(rows)
    vimrez = [str(row).replace('\\', '\\\\').replace('"', '\\"') for row in rows]

    vim.command('let s:rez = [%s]' % ','.join(vimrez))

def do_gather_candidates(inputs, limit):
    inputs = inputs.strip()
    kws = re.split('\s', inputs)

    if inputs == "" or len(kws) < 1:
        return [{'word': 'Please input keyword'}]

    if len(kws[0]) <= 2:
        return [{'word': inputs, 'abbr': 'Please input at least 3 chars'}]

    global cache
    output = []
    # print(kws[0][:-1])
    if kws[0] in cache:
        output = cache[kws[0]]
    elif kws[0][:-1] in cache:
        # print(kws[0][:-1])
        output = cache[kws[0][:-1]]
    else:
        args = get_args(kws[0])
        output = run_command(args, os.getcwd())
        cache[kws[0]] = output

    rows = []
    progs = []
    for kw in kws:
        progs.append(get_regex_prog(kw, True))

    for line in output:
        if line.strip() == "":
            continue
        # print("line:%s" % line)
        format = __candidate(line, progs)
        if format is not None:
            rows.append(format)

        if len(rows) > limit:
            break

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

        path = items[0]
        row = items[1]
        col = items[2]
        body = ''.join(items[3::])

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
                'action__path': path,
                'action__line': int(row),
                'action__col': 0,
                'action__text': body
                }
    except TypeError as e:
        return None

def get_args_rg(inputs):
    args = ['rg', '-S', '--vimgrep', '--no-heading', inputs,]
    return args

def get_args_ag(inputs):
    args = ['ag', '-S', '--vimgrep', inputs,]
    return args

def get_args_ack(inputs):
    args = ['ack', '-H', '-S', '--nopager', '--nocolor' '--nogroup', '--column', inputs,]
    return args

def get_args_git(inputs):
    args = ['git', '--no-pager', 'grep', '-n', '--no-color', '-i', inputs, ]
    return args

def get_args(inputs):
    if cmd_exists("rg"):
        return get_args_rg(inputs)
    elif cmd_exists("ag"):
        return get_args_ag(inputs)
    elif cmd_exists("ack"):
        return get_args_ack(inputs)
    elif cmd_exists("git"):
        return get_args_ack(inputs)

def run_command(command, cwd, encode='utf8'):
    try:
        process = subprocess.run(command,
                cwd=cwd,
                stdout=subprocess.PIPE)

        return process.stdout.decode(encode).split('\n')
    except Exception as e:
        return []

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def main():
    res = do_gather_candidates("exists cmd", 10)
    # print(res)
    pass

if __name__ == "__main__":
    # main()
    pass
