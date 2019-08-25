#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import os

def lookup_get_name_dir_abbr(row):
    return os.path.join(row[1], row[0]).replace('\\', '/')

def lookup_get_name_dir_path(row):
    return os.path.join(row[1], row[0])
