#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re
import os
import vim
import time
import platform;

isWindows = platform.system() == "Windows"

class LookupGrep(object):
    def __init__(self):
        self.cache = {}
        self.cacheTime = {}
        self._escape = dict((c , "\\" + c) for c in ['^','$','.','{','}','(',')','[',']','\\','/','+'])

    def clear_cache(self):
        self.cacheTime = {}
        self.cache = {}

    def gather_candidates(self, inputs, limit):
        if inputs == "" or inputs == ";" or inputs.strip() == "":
            return [{'word': 'Please input keyword'}]

        inputItmes = inputs.split(';')
        inputKw = inputItmes[0] if len(inputItmes) > 0 else ""
        inputPath = inputItmes[1] if len(inputItmes) > 1 else ""

        kws = re.split('\s', inputKw)
        paths = re.split('\s', inputPath)

        if len(kws) < 1:
            return [{'word': 'Please input keyword'}]

        if len(kws[0]) <= 2:
            return [{'word': inputs, 'abbr': 'Please input at least 3 chars'}]

        # clean cache
        cacheTemp = {}
        for key in self.cache:
            if time.time() - self.cacheTime[key] < 300:
                cacheTemp[key] = self.cache[key]

        self.cache = cacheTemp

        isCache = False
        isSetCache = False
        keyCache = inputs[:-1]
        output = []
        # print(kws[0][:-1])
        if inputs in self.cacheTime and time.time() - self.cacheTime[inputs] < 300:
            output = self.cache[inputs]
            isCache = True
        elif keyCache in self.cacheTime and time.time() - self.cacheTime[keyCache] < 300:
            isCache = True
            isSetCache = True
            output = self.cache[inputs[:-1]]

        if not isCache:
            isSetCache = True
            args = self.get_args(kws[0])
            if not isWindows:
                output = self.run_command_linux(args, os.getcwd())
            else:
                output = self.run_command_linux(args, os.getcwd())

        rows = []
        rowsMatch = []
        progsKw = []
        for kw in kws:
            if kw != "":
                progsKw.append(self.get_grep_regex_prog(kw, True))

        progsPath = []
        for path in paths:
            if path != "":
                progsPath.append(self.get_grep_regex_prog(path, True))

        for line in output:
            if line.strip() == "":
                continue
            # print("line:%s" % line)
            format = self.__candidate(line, progsKw, progsPath)
            if format is not None:
                rowsMatch.append(line)
                if len(rows) <= limit:
                    rows.append(format)

        if isSetCache:
            self.cache[inputs] = rowsMatch
            self.cacheTime[inputs] = time.time()

        return rows

    def get_grep_regex_prog(self, kw, islower):
        searchkw = kw.lower() if islower else kw

        regex = ''
        escaped = [self._escape.get(c, c) for c in searchkw]

        regex = ''.join(escaped)

        return re.compile(regex)

    def __candidate(self, line, progsKw, progsPath):
        try:
            line = line.replace('"', '')
            items = line.split(':')
            if len(items) < 4:
                return None

            path = items[0].strip()
            row = items[1]
            col = items[2]
            body = ''.join(items[3::]).replace('\r', '').strip()

            bodylower = body.lower()
            for prog in progsKw:
                result = prog.search(bodylower)
                if not result:
                    return None

            if len(progsPath) > 0:
                pathlower = path.lower()
                for prog in progsPath:
                    result = prog.search(pathlower)
                    if not result:
                        return None

            return {
                    "word": line,
                    "abbr": "{0}:{1} {2}".format(path, row, body),
                    "kind": "jump_list",
                    "action__path": path,
                    "action__line": int(row),
                    "action__col": int(col),
                    "action__text": body
                    }
        except TypeError as e:
            return None

    def get_args_rg(self, inputs):
        args = ['rg', '-S', '--vimgrep', '--no-heading', inputs,]
        return args

    def get_args_ag(self, inputs):
        args = ['ag', '-i', '--vimgrep', inputs]
        return args

    def get_args_ack(self, inputs):
        args = ['ack', '-H', '-S', '--nopager', '--nocolor' '--nogroup', '--column', inputs,]
        return args

    def get_args_git(self, inputs):
        args = ['git', '--no-pager', 'grep', '-n', '--no-color', '-i', inputs, ]
        return args

    def get_args(self, inputs):
        if isWindows:
            return self.get_args_ag(inputs)
        else:
            return self.get_args_ag(inputs)

    def run_command_linux(self, command, cwd, encode='utf8'):
        try:
            process = subprocess.run(command,
                    cwd=cwd,
                    stdout=subprocess.PIPE)

            return process.stdout.decode(encode).split('\n')
        except Exception as e:
            return []

    def run_command_windows(self, command, cwd, encode='utf8'):
        try:
            cmd = ' '.join(command)

            output = vim.call("vimproc#system", cmd)
            return output.split('\n')
        except Exception as e:
            return []

lookupgrep = LookupGrep()
def LookupGrepGatherCandidates():
    inputs = vim.eval("s:inputs")
    limit = 100
    rows = lookupgrep.gather_candidates(inputs, limit)

    vim.command('let s:rez = {0}'.format(rows))

def LookupGrepClean():
    lookupgrep.clear_cache()

def main():
    res = do_gather_candidates("can", 100)
    # print(res)
    pass

if __name__ == "__main__":
    # main()
    pass
