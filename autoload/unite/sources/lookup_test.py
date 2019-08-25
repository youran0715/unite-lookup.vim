#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_filter import *
from lookup_filter_path import *
from lookup import *
from lookup_goimport import *
from lookup_mix import *

def main():
    lookup_set_cache_dir('/home/wuhong/.cache/vim/lookup')

    mix = LookupMix()

    print(mix.search("mru"))
    print(mix.search("string"))
    print(mix.search("strings"))
    print(mix.search("strings"))

if __name__ == "__main__":
    main()
