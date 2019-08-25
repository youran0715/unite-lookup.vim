#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_filter import *
from lookup_filter_path import *
from lookup import *
from lookup_goimport import *

def main():
    goimport = LookupGoimport()
    goimport.candidates = [
            'github.scom/tyou/nvim',
            'github.scom/tyouran0715/rvim',
            'bufio', 'fmt', 'strings', 'strconv', 
            'github.com/youran0715/vim',
        ]

    print(goimport.search("st"))
    print(goimport.search("str"))
    print(goimport.search("str"))

if __name__ == "__main__":
    main()
