#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_goimport import *
from lookup_mru import *
from lookup_file import *
from lookup_grep import *
from lookup_command import *

src_mru = LookupMru()
src_file = LookupFile()
src_grep = LookupGrep()
src_goimport = LookupGoimport()
src_command = LookupCommand()

class LookupMix(object):
    def __init__(self, src_names):
        self.sources = []
        for name in src_names:
            if name == "mru":
                self.sources.append(src_mru)
            elif name == "file":
                self.sources.append(src_file)
            elif name == "goimport":
                self.sources.append(src_goimport)
            elif name == "command":
                self.sources.append(src_command)
            elif name == "grep":
                self.sources.append(src_grep)

    def search(self, inputs):
        results = []
        dictKind = {}
        for src in self.sources:
            result = src.search(inputs)

            # remove duplicate rows
            for row in result:
                word = row['word']
                kind = row['kind']

                if kind not in dictKind:
                    dictKind[kind] = {}

                dictResult = dictKind[kind]

                if word in dictResult:
                    continue

                dictResult[word] = 1
                results.append(row)

        return results

    def redraw(self):
        for src in self.sources:
            src.redraw()

    def set_buffer(self, buffer):
        for src in self.sources:
            src.set_buffer(buffer)
