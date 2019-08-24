#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup_filter import *
from lookup_filter_path import *
from lookup import *
from lookup_goimport import *

def main():
    goimport = LookupGoimport()
    goimport.candidates = [
            'bufio', 'fmt', 'strings', 'strconv', 
            'github.com/youran0715/vim',
        ]

    print(goimport.search(""))
    print(goimport.search("str"))

if __name__ == "__main__":
    main()
