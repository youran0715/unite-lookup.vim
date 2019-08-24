#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from lookup import *
from lookup_filter_path import *

class LookupGoimport(Lookup):
    def __init__(self):
        super(LookupGoimport, self).__init__()
        self.filter = LookupFilterPath()
        pass

