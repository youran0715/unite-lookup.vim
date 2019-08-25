#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_filter import *
from lookup_filter_path import *
from lookup import *
from lookup_goimport import *
from lookup_mix import *

def main():
    src_mru.mru_path = '/home/wuhong/.cache/vim/_home_wuhong_.vim/mrulist2'
    src_mru.load()
    mix = LookupMix()

    print(mix.search("unite"))
    print(mix.search("string"))
    print(mix.search("strings"))
    print(mix.search("strings"))

if __name__ == "__main__":
    main()
