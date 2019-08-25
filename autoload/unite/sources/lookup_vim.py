#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import sys
import vim

lookup_plugin_path = vim.eval("s:lookup_plugin_path")
sys.path.append(lookup_plugin_path)
# print(sys.path)

from lookup_sources import *
from lookup_mix import *

src_mix = LookupMix()

def UnitePyLookupMruClean():
    src_mru.clean()

def UnitePyLookupMruSave():
    src_mru.save()

def UnitePyLookupMruLoad():
    src_mru.load()

def UnitePyLookupMruAdd():
    path = vim.eval('s:buf_path')
    src_mru.add(path)

def UnitePyLookupSetCacheDir():
    path = vim.eval('s:cache_dir')
    lookup_set_cache_dir(path)

def UnitePyLookupMixSearch():
    src_mix.redraw()

def UnitePyLookupMixSearch():
    src_file.wildignore = vim.eval("g:lookupfile_WildIgnore")
    src_file.followlinks = vim.eval("g:lookupfile_FollowLinks")

    inputs = vim.eval("s:inputs")

    start_time = time.time()

    rows = src_mix.search(inputs)
    vim.command('let s:rez = {0}'.format(rows))

    end_time = time.time()

    vim.command('echo "search %s cost %.1f ms, return %d rows"' % (inputs, (end_time - start_time)*1000, len(rows)))

