#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import re
import os
import time
from lookup import *
from lookup_filter_grep import *
from asyncExecutor import AsyncExecutor

class LookupGrep(Lookup):
    def __init__(self):
        super(LookupGrep, self).__init__()
        self.filter = LookupFilterGrep()
        self.name = "grep"
        self.min_input = 3
        self.enable_filter_path = True
        self.max_candidates = 100

    def need_sort(self):
        return False

    def need_gather_candidates(self):
        return not self.cache.exist_result(self.inputs) and not self.cache.exist_pre_candidates(self.inputs)

    def do_gather_candidates(self, is_redraw):
        output = []
        args = self.get_args(self.input_kws[0])
        output = self.run_command_linux(args, os.getcwd())

        rows = []
        for line in output:
            item = self.parse_line(line)
            if item is not None:
                rows.append(item)

        return rows

    def parse_line(self, line):
        try:
            line = line.replace('"', '')
            items = line.split(':')
            if len(items) < 4:
                return None

            path = items[0].strip()
            row = items[1]
            col = items[2]
            body = ''.join(items[3::]).replace('\r', '').replace('\t', '').strip()

            return (path, row, col, body)
        except TypeError as e:
            return None

    def format(self, rows):
        return [{
                "word": row[3],
                "abbr": "{0}:{1} {2}".format(row[0], row[1], row[3]),
                "kind": "jump_list",
                "action__path": row[0],
                "action__line": int(row[1]),
                "action__col": int(row[2]),
                "action__text":row[3] 
                } for row in rows]

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
        return self.get_args_ag(inputs)

    def run_command_linux(self, command, cwd, encode='utf8'):
        try:
            executor = AsyncExecutor()
            result = executor.execute(' '.join(command))
            return [line for line in result if line is not None]
        except Exception as e:
            return []

    def run_command_linux_old(self, command, cwd, encode='utf8'):
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
