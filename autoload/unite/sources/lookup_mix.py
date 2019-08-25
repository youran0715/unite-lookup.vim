#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_sources import *

class LookupMix(object):
    def __init__(self):
        self.sources = [
                src_mru,
                src_goimport,
            ]

    def search(self, inputs):
        results = []
        for src in self.sources:
            result = src.search(inputs)
            results.extend(result)

        return results

    def enable_filetype(self, ft):
        for src in self.sources:
            src.enable_filetype(ft)
        pass
