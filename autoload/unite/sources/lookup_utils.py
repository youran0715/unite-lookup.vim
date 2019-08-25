#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import os
import hashlib

lookup_cache_dir = ".vimconfig"

def lookup_get_name_dir_abbr(row):
    return os.path.join(row[1], row[0]).replace('\\', '/')

def lookup_get_name_dir_path(row):
    return os.path.join(row[1], row[0])

def lookup_set_cache_dir(path):
    hl = hashlib.md5()
    hl.update(os.getcwd().encode(encoding='utf-8'))
    lookup_cache_dir = os.path.join(path, hl.hexdigest())
    try:
        os.makedirs(lookup_cache_dir)
    except Exception as e:
        pass

def lookup_get_cache_path(name):
    return os.path.join(lookup_cache_dir, name)
