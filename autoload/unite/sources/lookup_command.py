#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup import *
from lookup_filter_path import *
import vim

def escQuote(str):
    return "" if str is None else str.replace("'","''")

class LookupCommand(Lookup):
    def __init__(self):
        super(LookupCommand, self).__init__()
        self.filter = LookupFilterPath()
        self.name = "command"
        pass

    def do_gather_candidates(self, is_redraw):
        tmp = vim.eval("@x")
        vim.command("redir @x")

        vim.command("silent command")
        result = vim.eval("@x")
        vim.command("let @x = '%s'" % escQuote(tmp))
        vim.command("redir END")

        result_list = result.splitlines()[2:]
        result_list = [x[4:].split()[0]
                for x in result_list
                if x.strip()]
        return result_list

    def format(self, rows):
        return [{'word': row, 'kind':'command', 'abbr': '[C] %s' % row} for row in rows]
