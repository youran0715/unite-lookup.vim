#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_sources import *

class LookupMix(object):
    def __init__(self):
        self.sources = [
                src_mru,
                src_file,
                src_goimport,
            ]

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
