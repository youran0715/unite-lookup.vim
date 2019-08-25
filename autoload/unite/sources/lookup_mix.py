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
            if src.kind not in dictKind:
                dictKind[src.kind] = {}

            dictResult = dictKind[src.kind]

            # remove duplicate rows
            for row in result:
                word = row['word']
                if word in dictResult:
                    continue

                dictResult[word] = 1
                results.append(row)

        return results

    def redraw(self):
        for src in self.sources:
            src.redraw()

    def enable_filetype(self, ft):
        for src in self.sources:
            src.enable_filetype(ft)
