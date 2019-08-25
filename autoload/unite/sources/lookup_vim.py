#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_sources import *
from lookup_mix import *

def UnitePyLookupMruClean():
    src_mru.clean()

def UnitePyLookupMruSave():
    src_mru.save()

def UnitePyLookupMruSetPath():
    file_path = vim.eval('s:file_path')
    src_mru.mru_path = file_path
    src_mru.load()

def UnitePyLookupMruAdd():
    path = vim.eval('s:buf_path')
    src_mru.add(path)
